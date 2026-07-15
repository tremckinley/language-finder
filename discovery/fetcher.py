"""Asynchronous HTTP fetcher for Phase 1 discovery."""

from __future__ import annotations

import asyncio
from typing import Iterable

import aiohttp

from config import DEFAULT_CONFIG, DiscoveryConfig
from models import FetchResult


class AsyncFetcher:
    """Small async HTTP client wrapper with consistent headers and errors."""

    def __init__(self, config: DiscoveryConfig = DEFAULT_CONFIG):
        self.config = config
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AsyncFetcher":
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout_seconds)
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": self.config.accept_language,
        }
        connector = aiohttp.TCPConnector(ssl=self.config.verify_ssl)
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=connector,
            raise_for_status=False,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("AsyncFetcher must be used as an async context manager.")
        return self._session

    async def fetch_text(self, url: str) -> FetchResult:
        """Fetch text content from a URL and return a normalized result object."""
        try:
            async with self.session.get(
                url,
                allow_redirects=True,
                max_redirects=self.config.max_redirects,
            ) as response:
                content_type = response.headers.get("content-type")
                text = await response.text(errors="replace")
                final_url = str(response.url)
                return FetchResult(
                    requested_url=url,
                    final_url=final_url,
                    status_code=response.status,
                    content_type=content_type,
                    text=text,
                    redirected=final_url.rstrip("/") != url.rstrip("/"),
                )
        except asyncio.TimeoutError:
            return FetchResult(requested_url=url, error="timeout")
        except aiohttp.TooManyRedirects:
            return FetchResult(requested_url=url, error="too_many_redirects")
        except aiohttp.ClientError as exc:
            return FetchResult(requested_url=url, error=f"client_error: {exc.__class__.__name__}")
        except Exception as exc:  # pragma: no cover - defensive boundary
            return FetchResult(requested_url=url, error=f"unexpected_error: {exc.__class__.__name__}")

    async def fetch_many(self, urls: Iterable[str]) -> list[FetchResult]:
        """Fetch multiple URLs concurrently."""
        tasks = [self.fetch_text(url) for url in urls]
        return await asyncio.gather(*tasks)

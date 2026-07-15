from __future__ import annotations
import argparse, asyncio, json
from pathlib import Path

from discovery.crawler import DomainDiscoverer
from language.aggregator import LanguageAggregator
from reporting.reporter import write_discovery_csv, write_json, write_language_csv

async def analyze_domain(domain: str) -> tuple:
    discovery = await DomainDiscoverer().discover(domain)
    report = LanguageAggregator().aggregate(discovery)
    return discovery, report

async def analyze_domains(domains: list[str]) -> tuple[list, list]:
    discoveries = []
    reports = []
    for domain in domains:
        discovery, report = await analyze_domain(domain)
        discoveries.append(discovery)
        reports.append(report)
    return discoveries, reports

def read_domains(args) -> list[str]:
    values = []
    if args.domain:
        values.extend(args.domain)
    if args.input:
        text = Path(args.input).read_text(encoding='utf-8')
        for line in text.splitlines():
            line = line.strip().strip(',')
            if line and not line.lower().startswith('domain'):
                values.append(line.split(',')[0].strip())
    return list(dict.fromkeys(values))

def parse_args():
    p = argparse.ArgumentParser(description='Language Discovery Engine')
    p.add_argument('--domain', action='append', help='Domain to analyze. Can be repeated.')
    p.add_argument('--input', help='Optional CSV or text file with domains in first column.')
    p.add_argument('--output-dir', default='output', help='Directory for JSON and CSV output.')
    p.add_argument('--include-text', action='store_true', help='Include extracted visible text in discovery JSON.')
    return p.parse_args()

def main() -> None:
    args = parse_args()
    domains = read_domains(args)
    if not domains:
        raise SystemExit('Provide --domain or --input')
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    discoveries, reports = asyncio.run(analyze_domains(domains))
    write_json(out/'language_reports.json', [r.to_dict() for r in reports])
    write_json(out/'discovery_results.json', [d.to_dict(include_text=args.include_text) for d in discoveries])
    write_language_csv(out/'language_reports.csv', reports)
    write_discovery_csv(out/'discovery_results.csv', discoveries)
    print(json.dumps([r.to_dict() for r in reports], indent=2, sort_keys=True))

if __name__ == '__main__':
    main()

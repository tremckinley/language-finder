from __future__ import annotations
import argparse, asyncio, json
from pathlib import Path
from discovery.crawler import DomainDiscoverer
from language.aggregator import LanguageAggregator
from reporting.reporter import write_discovery_csv, write_json, write_language_csv
async def analyze_domain(domain: str):
    discovery = await DomainDiscoverer().discover(domain)
    report = LanguageAggregator().aggregate(discovery)
    return discovery, report
async def analyze_domains(domains: list[str]):
    discoveries=[]; reports=[]
    for domain in domains:
        d,r=await analyze_domain(domain); discoveries.append(d); reports.append(r)
    return discoveries,reports
def read_domains(args):
    values=[]
    if args.domain: values.extend(args.domain)
    if args.input:
        for line in Path(args.input).read_text(encoding='utf-8').splitlines():
            line=line.strip().strip(',')
            if line and not line.lower().startswith('domain'): values.append(line.split(',')[0].strip())
    return list(dict.fromkeys(values))
def parse_args():
    p=argparse.ArgumentParser(description='Language Discovery Engine')
    p.add_argument('--domain', action='append')
    p.add_argument('--input')
    p.add_argument('--output-dir', default='output')
    p.add_argument('--include-text', action='store_true')
    return p.parse_args()
def main():
    args=parse_args(); domains=read_domains(args)
    if not domains: raise SystemExit('Provide --domain or --input')
    out=Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    discoveries,reports=asyncio.run(analyze_domains(domains))
    write_json(out/'language_reports.json',[r.to_dict() for r in reports])
    write_json(out/'discovery_results.json',[d.to_dict(include_text=args.include_text) for d in discoveries])
    write_language_csv(out/'language_reports.csv',reports)
    write_discovery_csv(out/'discovery_results.csv',discoveries)
    print(json.dumps([r.to_dict() for r in reports], indent=2, sort_keys=True))
if __name__ == '__main__': main()

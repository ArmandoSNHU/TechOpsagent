"""Preview read requests by default; --read explicitly performs the request."""
import argparse
import json
from techops.settings import load_settings
import time
from techops.connectors.github import GitHubIssues
from techops.connectors.observability import Grafana,Loki
from techops.connectors.http import ConnectorError

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('service',choices=['github','grafana','loki'])
    parser.add_argument('--repository')
    parser.add_argument('--url')
    parser.add_argument('--label',default='checkout')
    parser.add_argument('--read',action='store_true')
    args=parser.parse_args()
    settings=load_settings()
    try:
        if args.service=='github':
            adapter=GitHubIssues(args.repository or settings['GITHUB_REPOSITORY'],token=settings.get('GITHUB_TOKEN'))
            result=adapter.list_issues() if args.read else adapter.preview()
        elif args.service=='grafana':
            adapter=Grafana(args.url or settings['GRAFANA_URL'],token=settings.get('GRAFANA_TOKEN'))
            result=adapter.health() if args.read else adapter.preview()
        else:
            adapter=Loki(args.url or settings['LOKI_URL'],token=settings.get('LOKI_TOKEN'));end=int(time.time())
            result=adapter.query(args.label,end-900,end) if args.read else adapter.preview(args.label,end-900,end)
    except (ValueError,ConnectorError) as exc: parser.exit(1,'Connector: '+str(exc)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()

"""Preview synthetic Loki test events; --send-local writes only to loopback:3100."""
import argparse
import http.client
import json
import time

def build_payload(now=None):
    now=time.time_ns() if now is None else now
    lines=[{'message':'Synthetic checkout failure: KeyError TAX_REGION','status':500},
           {'message':'Synthetic application exception KeyError TAX_REGION'},
           {'message':'Synthetic comparison health check succeeded','status':200}]
    return {'streams':[{'stream':{'service_name':'checkout','environment':'synthetic-lab'},
                        'values':[[str(now-(3-i)*1000000000),json.dumps(line)] for i,line in enumerate(lines)]}]}

def send_local(payload):
    connection=http.client.HTTPConnection('127.0.0.1',3100,timeout=5)
    try:
        connection.request('POST','/loki/api/v1/push',json.dumps(payload),{'Content-Type':'application/json'})
        response=connection.getresponse()
        if response.status!=204: raise RuntimeError('Local Loki ingestion failed: HTTP '+str(response.status))
    finally:connection.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--send-local',action='store_true');args=parser.parse_args()
    payload=build_payload()
    if args.send_local:
        send_local(payload);print('Sent 3 synthetic events to local Loki (HTTP 204).')
    else:print(json.dumps({'dry_run':True,'target':'http://127.0.0.1:3100/loki/api/v1/push','payload':payload},indent=2))

if __name__=='__main__':main()

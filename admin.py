"""Local researcher commands; access is governed by the operating-system account."""
import argparse,json
from pathlib import Path
from pilot.storage import Store
from pilot.analysis import report,export_zip,merge_external

def main():
    p=argparse.ArgumentParser(description='Local pilot diagnostics; no questionnaire is served by the website.')
    p.add_argument('--db',default='data/pilot.sqlite3'); p.add_argument('--include-tests',action='store_true')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('summary')
    e=sub.add_parser('export');e.add_argument('--output',required=True);e.add_argument('--include-incomplete',action='store_true')
    m=sub.add_parser('merge-external');m.add_argument('csv');m.add_argument('--output',required=True)
    a=p.parse_args();s=Store(a.db)
    if a.command=='summary': print(json.dumps(report(s,a.include_tests),ensure_ascii=False,indent=2))
    elif a.command=='export':
        Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(export_zip(s,a.include_tests,not a.include_incomplete));print('Export written:',a.output)
    else:
        result=merge_external(s,a.csv,a.include_tests);Path(a.output).parent.mkdir(parents=True,exist_ok=True);result.to_csv(a.output,index=False);print('Joined rows:',len(result))
if __name__=='__main__': main()

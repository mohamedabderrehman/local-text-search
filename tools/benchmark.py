"""Reproducible generated-corpus benchmark; avoids claims about cold OS caches."""
import os,sys,tempfile,time,json,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from database import Database
from search_engine import SearchEngine,CYTHON_AVAILABLE
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp);corpus=root/'corpus';corpus.mkdir();db=Database(str(root/'benchmark.sqlite'))
 lines=200000
 for i in range(4):
  with (corpus/f'generated-{i}.txt').open('w',encoding='utf-8') as f:
   for n in range(lines):f.write(f'generated record {i}-{n} '+('portfolio marker' if n%1000==0 else 'ordinary log event')+'\n')
 size=sum(p.stat().st_size for p in corpus.iterdir());engine=SearchEngine(str(corpus),str(root/'results'))
 owner=db.create_user('synthetic-benchmark','unused-password-hash',False)
 runs=[]
 for n in range(3):
  job=db.create_job(owner,'portfolio marker');start=time.perf_counter();result=engine.search('portfolio marker',job,db,max_results=10000);elapsed=time.perf_counter()-start
  assert result['matches']==800,result
  runs.append({'run':n+1,'seconds':round(elapsed,4),'matches':result['matches']})
 report={'platform':platform.platform(),'processor':platform.processor(),'logical_cpus':os.cpu_count(),'python':platform.python_version(),'cython':CYTHON_AVAILABLE,'bytes':size,'files':4,'lines':lines*4,'cache_condition':'First process run and immediate repeats; OS page cache not flushed. No cold-cache claim.','runs':runs}
 print(json.dumps(report,indent=2))
 (Path(__file__).resolve().parents[1]/'docs/benchmark.json').write_text(json.dumps(report,indent=2))

import os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
workspace=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(workspace.name)/'test.sqlite')
os.environ['RESULTS_DIR']=str(Path(workspace.name)/'results')
os.environ['CORPUS_DIR']=str(Path(workspace.name)/'corpus')
os.environ['ENABLE_TELEGRAM']='0'
from app import app,db
from auth import hash_password
from search_engine import SearchEngine
class ReleaseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner=db.create_user('owner',hash_password('synthetic-password'),False)
        cls.other=db.create_user('other',hash_password('synthetic-password'),False)
    def engine(self,files):
        temp=Path(tempfile.mkdtemp(dir=workspace.name));corpus=temp/'corpus';corpus.mkdir()
        for name,content in files.items(): (corpus/name).write_bytes(content)
        return SearchEngine(str(corpus),str(temp/'results'))
    def test_matching_long_lines_and_last_line(self):
        engine=self.engine({'demo.txt':b'Alpha beta\nalpha only\n'+b'x'*100000+b' alpha BETA'})
        job=db.create_job(self.owner,'alpha beta');result=engine.search('alpha beta',job,db)
        self.assertEqual(result['matches'],2)
    def test_zero_matches_and_mixed_bytes(self):
        engine=self.engine({'demo.txt':b'\xff generated alpha\nordinary line\n'})
        self.assertEqual(engine.search('absent',db.create_job(self.owner,'absent'),db)['matches'],0)
        self.assertEqual(engine.search('alpha',db.create_job(self.owner,'alpha'),db)['matches'],1)
    def test_long_keyword_shift_does_not_skip_matches(self):
        content=b''.join(f'generated record 0-{n} portfolio marker\n'.encode() for n in range(1000))
        engine=self.engine({'generated.txt':content})
        self.assertEqual(engine.search('portfolio marker',db.create_job(self.owner,'portfolio marker'),db)['matches'],1000)
    def test_global_limit_across_files(self):
        engine=self.engine({'one.txt':b'demo\ndemo\n','two.txt':b'demo\ndemo\n'})
        job=db.create_job(self.owner,'demo');result=engine.search('demo',job,db,max_results=1)
        text=(engine.results_dir/f'job_{job}_results.txt').read_text(encoding='utf-8')
        self.assertEqual(text.count('FILE:'),1)
        self.assertEqual(result['matches'],1)
    def test_foreign_job_routes_are_inaccessible(self):
        job=db.create_job(self.owner,'demo');client=app.test_client()
        with client.session_transaction() as session:session['user_id']=self.other;session['username']='other'
        for path in [f'/job/{job}',f'/api/job/{job}/status',f'/job/{job}/download']:
            self.assertIn(client.get(path).status_code,[302,403,404])
    def test_unauthenticated_search_redirects(self):
        self.assertEqual(app.test_client().post('/search',data={'keywords':'demo'}).status_code,302)
if __name__=='__main__':unittest.main()

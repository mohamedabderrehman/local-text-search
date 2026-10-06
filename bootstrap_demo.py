"""Create a synthetic corpus and one administrator; never resets existing accounts."""
from getpass import getpass
from database import Database
from auth import hash_password
import config
if __name__ == '__main__':
    config.CORPUS_DIR.mkdir(parents=True,exist_ok=True)
    sample = config.CORPUS_DIR / 'synthetic-demo.txt'
    if not sample.exists():
        sample.write_text('demo order 1001 ready\ndemo order 1002 delivered\nsample inventory restocked\n',encoding='utf-8')
    password=getpass('New demo administrator password (at least 12 characters): ')
    if len(password)<12: raise SystemExit('Password too short')
    user=Database(str(config.DATABASE_PATH)).create_user('demo-admin',hash_password(password),True)
    print('Demo administrator created.' if user else 'Account exists; unchanged.')

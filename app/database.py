#mysql 연동
from venv import create

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

global DB_url
DB_url = '' #azure

try:
    engine = create_engine(DB_url, pool_recycle= 500, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("DB 연결 성공")
except Exception as e:
    print("DB 연결 실패")
    print(e)


# main.py
# from typing import Union
import json
import os
import random
from fastapi import FastAPI, UploadFile, File, Depends
import shutil
from datetime import datetime,timedelta
import logging
from pydantic import BaseModel
from sqlalchemy import DateTime, TEXT, VARCHAR, desc,func
from fastapi import HTTPException

import report_generate
from database import engine, SessionLocal
import models
from models import Child, Parent, Report,Txt
from sqlalchemy.orm import Session

from typing import List, Annotated

LOGGER = logging.getLogger(__name__)

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}

def get_db():
    global db
    db = SessionLocal()
    try:
        logging.info(f"DB 성공")
        print("success db ")
        yield db
    finally:
        logging.info(f"DB 실패")
        print("close db")
        db.close()

# db_dependency = Annotated[db, Depends(get_db)]

"""
class Report(Base):
__tablename__ = 'report'

id = Column(Integer, primary_key=True)
report_date = Column(DateTime, nullable=False)
report = Column(Text, nullable=False)
child_id = Column(String(255), nullable=False)
abuse_count = Column(Integer, nullable=False)
"""

def get_txt(child_id: str, session: Session) -> str:
    try:
        # 오늘 날짜 기준으로 일주일 전 날짜 계산
        one_week_ago = datetime.now() - timedelta(days=7)

        # 주어진 child_id와 일주일 간의 데이터를 필터링
        query = session.query(Txt).filter(
            Txt.child_id == child_id,
            Txt.date >= one_week_ago
        )
        results = query.all()

        # 각 결과를 문자열로 변환하여 리스트에 추가
        formatted_results = []
        for result in results:
            formatted_results.append(f"[{result.date}] '{result.report_text}'")

        # 리스트를 하나의 문자열로 합침
        final_result = ",\n".join(formatted_results)
        
        print(final_result)
        return final_result
    
    except Exception as e:
        print(f"데이터를 가져오는 중 오류 발생: {e}")
        return None


def generate_filename(child_id: str) -> str:
    try:
        # 현재 날짜를 기반으로 파일 이름 생성
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"txt_{current_date}_{child_id}.txt"
        
        print(f"Generated filename: {filename}")
        return filename

    except Exception as e:
        print(f"파일 이름 생성 중 오류 발생: {e}")
        return None

def save_txt_to_file(child_id: str, session: Session, filename: str) -> bool:
    try:
        # 데이터베이스에서 데이터를 가져옴
        data_str = get_txt(child_id, session)
        
        if data_str:
            # .txt 파일로 저장 (덮어쓰기 허용)
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(data_str)
            print(f"Data successfully written to {filename}")
            return True
        else:
            print("No data to write.")
            return False

    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")
        return False
      

@app.get("/save_txt_file")
async def save_txt_file(child_id: str, db: Session = Depends(get_db)):
    # 파일 이름 생성
    filename = generate_filename(child_id)
    
    if filename:
        # 항상 파일을 생성하고 덮어쓰기 허용
        success = save_txt_to_file(child_id=child_id, session=db, filename=filename)
        if success:
            return {"message": f"Data saved to {filename}", "filename": filename}
        else:
            return {"message": "Failed to save data to file", "filename": filename}
    else:
        return {"message": "Filename generation failed"}

@app.post("/report-to-db/")
async def report_to_db(db: Session = Depends(get_db), child_id: str = "test_user_id", filename: str = "", kind_report: int = 1):
    try:
        # 보고서 생성
        report_db = report_generate.generate_report(file_name=filename, kind=kind_report)
        
        # report_db의 타입 확인
        report_type = type(report_db)
        print(f"Report generated. Type: {report_type}")
        
        # report_db가 문자열인지 확인하고 처리
        if isinstance(report_db, str):
            try:
                # JSON 문자열을 파싱하고 예쁘게 포맷
                report_data = json.loads(report_db)
                formatted_report = json.dumps(report_data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # JSON 형식이 아닐 경우 그대로 사용
                formatted_report = report_db
        else:
            # JSON 문자열이 아닌 경우 str로 변환
            formatted_report = str(report_db)
        
        print("success : " + formatted_report[:500])  # 첫 500자를 로그로 출력
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")
    
    # 새로운 보고서 엔트리를 데이터베이스에 생성
    new_report = Report(
        report_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 시간을 포함하여 중복 방지
        child_id=child_id,
        report=formatted_report,
        abuse_count=random.randint(1, 30),
        report_type=str(kind_report),  # kind_report를 문자열로 변환
    )

    db.add(new_report)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")
    
    return {
        "child_id": child_id,
        "report": formatted_report,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kind_report": kind_report,
    }

@app.get("/save-and-report")
async def save_and_report(child_id: str, kind: int, db: Session = Depends(get_db)):
    # Step 1: Save the txt file
    save_result = await save_txt_file(child_id, db)
    
    if "filename" in save_result:
        filename = save_result["filename"]
        # Step 2: Use the saved filename to generate the report and store it in the database
        report_result = await report_to_db(db=db, child_id=child_id, filename=filename, kind_report=kind)
        return report_result
    else:
        return {"message": "Failed to save txt file or generate report"}
    
# Changed this endpoint to accept file uploads
@app.post("/generate-word/") # 대체 단어 생성 API
async def generate_word(txt: str):
    alter_word = report_generate.generate_word(txt)
    
    return {
        "alter_word": alter_word,
        }
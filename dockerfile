# syntax=docker/dockerfile:1

# Python 버전 선택
# 필요한 버전을 https://hub.docker.com/_/python 여기서 확인할 수 있습니다.
FROM python:3.11.9

# 디폴트 폴더 변경
WORKDIR /app

# Pip 패키지 설치
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
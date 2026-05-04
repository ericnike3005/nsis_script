# 1. 파이썬 3.9가 설치된 가벼운 리눅스 환경을 베이스로 가져옵니다.
FROM python:3.9-slim

# 2. 컨테이너 안에서 우리가 작업할 기본 폴더(/app)를 만듭니다.
WORKDIR /app

# 3. 내 컴퓨터(또는 Codespaces)에 있는 파일들을 저 폴더 안으로 모두 복사합니다.
COPY . /app

# requirements.txt 파일을 컨테이너 안으로 복사
COPY requirements.txt .

# 파일에 적힌 라이브러리들을 설치
RUN pip install -r requirements.txt

# 4. 준비물 목록(requirements.txt)을 보고 필요한 도구를 한 번에 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 도커 컨테이너가 켜지면 가장 먼저 'main.py'를 실행하라고 명령합니다.
CMD ["python", "main.py"]


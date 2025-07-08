# 가벼운 Python 이미지 사용
FROM python:3.11-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 의존성 설치 (최소한만)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정 (선택사항)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 기본 명령어
CMD ["python", "main.py"]

# 헬스체크 (선택사항)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('https://api.upbit.com/v1/market/all')" || exit 1 
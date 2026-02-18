# 🚀 PersonaBot 배포 가이드

## 📋 목차
1. [기본 배포](#기본-배포)
2. [HTTPS 설정](#https-설정)
3. [보안 강화](#보안-강화)
4. [모니터링](#모니터링)
5. [트러블슈팅](#트러블슈팅)

---

## 🎯 기본 배포

### 1. 환경 설정

```bash
# 1. 저장소 클론
git clone <your-repo-url>
cd PersonaBot

# 2. 가상환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp env.example .env
# .env 파일에 OPENAI_API_KEY 입력
```

### 2. 로컬 실행

```bash
# 로컬 테스트 (인증 없음, localhost만)
python app_gradio.py
```

### 3. 배포 실행

**현재 설정:**
- **인증:** `sgrfuture` / `misanee`
- **공개 URL:** Gradio Share (자동 생성)
- **유효 기간:** 72시간
- **접속 제한:** 20명 동시

```bash
python app_gradio.py
```

실행 후 터미널에서 Public URL 확인:
```
* Running on public URL: https://xxxxx.gradio.live
```

---

## 🔒 HTTPS 설정

### 옵션 1: Cloudflare Tunnel (가장 간편)

```bash
# 1. Cloudflared 설치
# Windows
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -o cloudflared.exe

# Mac
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64

# 2. 터널 생성
cloudflared tunnel --url http://localhost:7886

# 3. 생성된 HTTPS URL 사용
# https://xxxxx.trycloudflare.com
```

**장점:**
- 무료
- 자동 HTTPS
- 설정 불필요
- 방화벽 우회

**단점:**
- URL이 매번 바뀜
- 커스텀 도메인 불가

---

### 옵션 2: Nginx + Let's Encrypt (프로덕션 권장)

#### 2-1. Nginx 설치

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nginx
```

**CentOS/RHEL:**
```bash
sudo yum install nginx
```

**Windows:**
- Nginx 공식 사이트에서 다운로드: http://nginx.org/en/download.html

#### 2-2. Let's Encrypt SSL 인증서

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# 인증서 발급 + Nginx 자동 설정
sudo certbot --nginx -d your-domain.com
```

#### 2-3. Nginx 설정

`/etc/nginx/sites-available/personabot`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://127.0.0.1:7886;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 지원 (Gradio 실시간 업데이트)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 타임아웃 설정
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/personabot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 2-4. 앱 실행 (백그라운드)

```bash
# systemd 서비스 생성
sudo nano /etc/systemd/system/personabot.service
```

내용:
```ini
[Unit]
Description=PersonaBot Multi-Agent Debate System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/PersonaBot
Environment="PATH=/path/to/PersonaBot/venv/bin"
ExecStart=/path/to/PersonaBot/venv/bin/python app_gradio.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl start personabot
sudo systemctl enable personabot

# 상태 확인
sudo systemctl status personabot

# 로그 확인
sudo journalctl -u personabot -f
```

---

### 옵션 3: Docker 배포

#### Dockerfile 생성

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일 복사
COPY . .

# 로그 디렉토리
RUN mkdir -p logs

# 환경 변수
ENV OPENAI_API_KEY=""

# 포트 노출
EXPOSE 7886

# 실행
CMD ["python", "app_gradio.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  personabot:
    build: .
    ports:
      - "7886:7886"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./rag/vector_stores_new:/app/rag/vector_stores_new
    restart: unless-stopped
```

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 🛡️ 보안 강화

### 1. API 키 보안

**.env 파일 사용:**
```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxx

# 절대 Git에 커밋하지 마세요!
# .gitignore에 .env 포함 확인
```

**OpenAI 대시보드 설정:**
- Usage Limits 설정 ($50/month 등)
- Alert 설정 (80%, 90%, 100%)
- API 키 로테이션 (월 1회)

### 2. 방화벽 설정

**특정 IP만 허용 (Nginx):**
```nginx
location / {
    allow 123.456.789.0/24;  # 회사 IP
    deny all;
    
    proxy_pass http://127.0.0.1:7886;
    ...
}
```

**Cloudflare Access (권장):**
- 무료로 IP 화이트리스트 설정
- 2FA 인증 추가 가능
- DDoS 방어 자동

### 3. Rate Limiting

**Nginx 레벨:**
```nginx
limit_req_zone $binary_remote_addr zone=debatelimit:10m rate=10r/m;

location / {
    limit_req zone=debatelimit burst=5;
    ...
}
```

**Python 레벨 (추가 구현 가능):**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
def run_debate_simple(...):
    ...
```

---

## 📊 모니터링

### 1. 로그 모니터링

**실시간 로그:**
```bash
# 전체 로그
tail -f logs/app.log

# 에러만
tail -f logs/app.log | grep ERROR

# 특정 패턴
tail -f logs/app.log | grep "Debate"
```

**로그 분석:**
```bash
# 오늘 에러 수
grep "ERROR" logs/app.log | grep "$(date '+%Y-%m-%d')" | wc -l

# API 호출 수
grep "API Call" logs/app.log | wc -l

# 평균 응답 시간
grep "Duration" logs/app.log | awk '{print $NF}' | sed 's/s//' | awk '{sum+=$1; count++} END {print sum/count}'
```

### 2. API 사용량 추적

**UI 내 모니터링:**
- 오른쪽 컬럼 "📊 시스템 모니터링" 섹션
- 30초마다 자동 업데이트
- 총 호출 수, 활성 세션, 가동 시간

**OpenAI 대시보드:**
- https://platform.openai.com/usage
- 토큰 사용량
- 비용 추적
- 일일/월별 통계

### 3. 시스템 리소스

**리눅스:**
```bash
# CPU/메모리
htop

# 특정 프로세스
ps aux | grep app_gradio

# 네트워크
netstat -tulpn | grep 7886
```

**Windows:**
- 작업 관리자
- Resource Monitor
- Performance Monitor

---

## 🔧 트러블슈팅

### 문제 1: "Cannot find empty port"

**원인:** 포트가 이미 사용 중

**해결:**
```bash
# Windows
netstat -ano | findstr :7886
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :7886
kill -9 <PID>

# 또는 포트 변경
server_port=7887
```

---

### 문제 2: "AuthenticationError"

**원인:** OpenAI API 키 오류

**해결:**
1. .env 파일 확인
2. API 키 유효성 확인 (OpenAI 대시보드)
3. 사용량 한도 확인
4. 키 재발급

---

### 문제 3: "Context length exceeded"

**원인:** 토큰 수 초과 (8192 제한)

**해결:**
1. Temperature 낮추기 (0.7 → 0.5)
2. 참가자 수 줄이기 (10명 → 5명)
3. 라운드 수 줄이기 (3 → 1)
4. RAG k 값 줄이기 (3 → 2)

---

### 문제 4: 느린 응답

**원인:** 네트워크, API 지연

**해결:**
1. OpenAI API 상태 확인 (status.openai.com)
2. 네트워크 속도 테스트
3. 서버 리소스 확인
4. 동시 접속자 수 확인

---

## 💰 비용 최적화

### OpenAI API 비용 절감

**설정 조정:**
```python
# app_gradio.py
temperature = 0.7  # 0.9 → 0.7 (20% 토큰 절감)
k = 2              # 3 → 2 (RAG 검색)
num_rounds = 1     # 3 → 1 (대화 길이)
```

**예상 비용:**
- **GPT-4o-mini:** $0.15/1M input tokens, $0.60/1M output tokens
- **평균 토론:** ~6,800 tokens
- **비용/토론:** ~$0.004 (0.4센트)
- **월 1,000회:** ~$4

**text-embedding-ada-002:**
- $0.10/1M tokens
- 거의 무시 가능한 수준

---

## 📈 성능 모니터링

### Prometheus + Grafana (고급)

**설치:**
```bash
# Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Grafana
docker run -d -p 3000:3000 grafana/grafana
```

**메트릭 추가:**
```python
from prometheus_client import Counter, Histogram

debate_counter = Counter('debates_total', 'Total debates')
debate_duration = Histogram('debate_duration_seconds', 'Debate duration')

@debate_duration.time()
def run_debate_simple(...):
    debate_counter.inc()
    ...
```

---

## 🎯 프로덕션 체크리스트

### 배포 전

- [ ] `.env` 파일에 API 키 설정
- [ ] `.gitignore`에 민감 정보 추가
- [ ] 로그 디렉토리 권한 설정
- [ ] 테스트 토론 실행 (모든 페르소나)
- [ ] 에러 핸들링 확인

### 배포 시

- [ ] HTTPS 설정 (Nginx/Cloudflare)
- [ ] 인증 시스템 활성화
- [ ] 방화벽 규칙 설정
- [ ] 로그 모니터링 설정
- [ ] 백업 스크립트 실행

### 배포 후

- [ ] 로그 파일 확인 (첫 1시간)
- [ ] API 사용량 모니터링
- [ ] 응답 시간 측정
- [ ] 사용자 피드백 수집
- [ ] 정기 점검 스케줄 (주 1회)

---

## 🔐 보안 권장 사항

### 1. 다단계 인증
- Gradio의 기본 auth는 HTTP Basic Auth
- HTTPS 필수 (Cloudflare/Nginx)
- 추가 보안: Cloudflare Access, VPN

### 2. API 키 관리
- 환경 변수 사용
- 절대 코드에 하드코딩 금지
- 정기적 키 로테이션
- 사용량 제한 설정

### 3. 네트워크 보안
- IP 화이트리스트
- Rate Limiting
- DDoS 방어 (Cloudflare)
- 정기 보안 업데이트

---

## 📞 지원

**문제 발생 시:**
1. `logs/app.log` 확인
2. GitHub Issues 생성
3. 로그 첨부 + 재현 단계

**성능 개선:**
- Temperature 조정
- 참가자/라운드 수 최적화
- 서버 스펙 업그레이드

**기능 요청:**
- 새 페르소나 추가
- 다국어 지원
- UI 커스터마이징

---

**작성일:** 2025-10-22  
**버전:** 1.0  
**업데이트:** 배포 및 보안 기능 추가



# 🚀 PersonaBot 배포 빠른 시작

## ✅ **설정 완료!**

Cloudflare Tunnel이 설치되어 **영구 HTTPS URL**을 사용할 수 있습니다!

---

## 🎯 **실행 방법 (2단계)**

### 1단계: 앱 실행

```bash
python app_gradio.py
```

**확인 사항:**
```
✅ Total 14 personas ready
✅ Running on local URL: http://0.0.0.0:7886
✅ Running on public URL: https://xxxxx.gradio.live (1주일 유효)
```

---

### 2단계: Cloudflare Tunnel 실행

**간단 실행:**
```bash
start_tunnel.bat
```

**또는 직접 실행:**
```bash
cloudflared.exe tunnel --url http://localhost:7886
```

**출력 예시:**
```
2025-10-22T00:00:00Z INF +--------------------------------------------------------------------------------------------+
2025-10-22T00:00:00Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
2025-10-22T00:00:00Z INF |  https://random-name-1234.trycloudflare.com                                               |
2025-10-22T00:00:00Z INF +--------------------------------------------------------------------------------------------+
```

**이 URL이 영구 HTTPS URL입니다!** 🎉

---

## 🔐 **접속 정보**

### Gradio Share URL (1주일)
```
URL: https://851a44283b6c83d5b2.gradio.live
만료: 2025-10-29 (7일 후)
```

### Cloudflare Tunnel URL (영구)
```
URL: https://xxxxx.trycloudflare.com (터널 실행 시 표시됨)
만료: 없음 (터널 실행 중 계속 유효)
```

**둘 다 인증 필요:**
- **Username:** `sgrfuture`
- **Password:** `misanee`

---

## 📋 **URL 비교**

| 특징 | Gradio Share | Cloudflare Tunnel |
|------|-------------|-------------------|
| **유효기간** | 1주일 | 영구 (실행 중) |
| **재시작 필요** | 7일마다 | 앱 재시작 시만 |
| **URL 변경** | 매번 | 매번 (고정 가능) |
| **HTTPS** | ✅ | ✅ |
| **인증** | ✅ | ✅ |
| **설정** | 자동 | 1회 설치 |
| **추천** | 단기 데모 | 장기 사용 |

---

## 🎯 **사용 시나리오**

### 📌 시나리오 1: 빠른 데모 (1주일)
**→ Gradio Share만 사용**
```
현재 URL: https://851a44283b6c83d5b2.gradio.live
설정: 완료 (이미 실행 중)
추가 작업: 없음
```

---

### 📌 시나리오 2: 장기 사용 (추천)
**→ Cloudflare Tunnel 사용**

**실행:**
```bash
# 터미널 1: 앱 실행
python app_gradio.py

# 터미널 2: 터널 실행
start_tunnel.bat
```

**결과:**
- Gradio URL: https://851a44283b6c83d5b2.gradio.live (1주일)
- Cloudflare URL: https://xxxxx.trycloudflare.com (영구)

**→ 두 URL 모두 동시에 사용 가능!**

---

### 📌 시나리오 3: 고정 URL (프로페셔널)

**Cloudflare 계정 필요 (무료):**

```bash
# 1. Cloudflare 로그인
cloudflared.exe tunnel login

# 2. 터널 생성
cloudflared.exe tunnel create personabot

# 3. 설정 파일 생성
```

**config.yml:**
```yaml
tunnel: <UUID>
credentials-file: C:\Users\yoonj\.cloudflared\<UUID>.json

ingress:
  - hostname: personabot.yourdomain.com
    service: http://localhost:7886
  - service: http_status:404
```

```bash
# 4. DNS 라우팅
cloudflared.exe tunnel route dns personabot personabot.yourdomain.com

# 5. 실행
cloudflared.exe tunnel run personabot
```

**결과: https://personabot.yourdomain.com (완전 고정!)**

---

## 🔧 **트러블슈팅**

### 문제: "tunnel" 명령어 인식 안됨
```bash
# 전체 경로 사용
C:\Users\yoonj\Documents\PersonaBot\cloudflared.exe tunnel --url http://localhost:7886
```

### 문제: 포트 연결 안됨
```bash
# 앱이 실행 중인지 확인
# 터미널에서 "Running on local URL" 확인
netstat -ano | findstr :7886
```

### 문제: URL이 표시 안됨
```bash
# 터미널 출력 확인
# "Your quick Tunnel has been created! Visit it at..." 메시지 찾기
```

---

## 💡 **권장 사항**

### 단기 사용 (1주일 이내)
**→ 현재 Gradio URL 그대로 사용**
```
https://851a44283b6c83d5b2.gradio.live
추가 설정 불필요
```

### 장기 사용 (1주일 이상)
**→ start_tunnel.bat 실행**
```
영구 HTTPS URL 생성
앱 실행 중일 때만 터널도 같이 실행
```

### 프로덕션
**→ 고정 URL 설정**
```
도메인 필요
10분 초기 설정
완전 전문적
```

---

## 📞 **지금 실행 중인 URL**

**Gradio Share (이미 활성화):**
```
🌐 https://851a44283b6c83d5b2.gradio.live
🔐 ID: sgrfuture / PW: misanee
⏰ 만료: 2025-10-29
```

**Cloudflare Tunnel (백그라운드 실행 중):**
```
실행 확인: 터미널에서 "trycloudflare.com" URL 확인
또는: start_tunnel.bat을 새 터미널에서 실행하여 URL 확인
```

---

**작성일:** 2025-10-22  
**다음 단계:** start_tunnel.bat 실행 후 생성된 URL 확인


# ✅ Railway 배포 체크리스트

## 📋 **배포 전 확인**

- [x] `railway.json` 생성됨
- [x] `Procfile` 생성됨
- [x] `requirements.txt` 업데이트됨 (Gradio 추가)
- [x] `app_gradio.py` 포트 설정 수정됨
- [x] `.gitignore` 설정됨
- [x] `.railwayignore` 생성됨

---

## 🚀 **배포 단계**

### 1. GitHub Repository 생성

```bash
# Git 초기화 (필요시)
git init

# 파일 추가
git add .

# 커밋
git commit -m "Ready for Railway deployment"

# GitHub에서 새 Private Repository 생성
# https://github.com/new

# Remote 추가 및 Push
git remote add origin https://github.com/YOUR_USERNAME/PersonaBot.git
git branch -M main
git push -u origin main
```

### 2. Railway 배포

1. https://railway.app 접속
2. "New Project" → "Deploy from GitHub repo"
3. Repository 선택: `PersonaBot`
4. 자동 배포 시작 ⏳

### 3. 환경 변수 설정

Railway 프로젝트 → "Variables" 탭:

```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 4. 도메인 생성

"Settings" → "Generate Domain"

---

## 🎯 **배포 완료 후**

### 접속 확인:

```
URL: https://personabot-production.up.railway.app
Username: sgrfuture
Password: misanee
```

### 기능 테스트:

- [ ] 로그인 성공
- [ ] 페르소나 로드 확인
- [ ] 토론 시작 가능
- [ ] 실시간 스트리밍 작동
- [ ] 투표 결과 표시

---

## 💰 **비용 모니터링**

Railway Dashboard → "Usage" 탭:

- 무료 크레딧: $5/월
- 예상 사용량: ~$2-3/월
- 알림 설정: $4 도달 시

---

## 🔄 **업데이트 방법**

코드 수정 후:

```bash
git add .
git commit -m "Update: [변경 내용]"
git push
```

Railway가 자동으로 재배포! ✅

---

## ❓ **문제 해결**

### 빌드 실패
- Railway "Deployments" → 로그 확인
- `requirements.txt` 의존성 문제 확인

### 실행 오류
- "Variables" 탭에서 `OPENAI_API_KEY` 확인
- 로그에서 에러 메시지 확인

### 접속 안됨
- "Settings" → 도메인 확인
- 5-10분 대기 (첫 배포 시)

---

## 📊 **배포 상태**

| 항목 | 상태 |
|------|------|
| **코드 준비** | ✅ 완료 |
| **GitHub Push** | ⏳ 대기 |
| **Railway 배포** | ⏳ 대기 |
| **환경 변수** | ⏳ 대기 |
| **도메인 생성** | ⏳ 대기 |
| **테스트** | ⏳ 대기 |

---

## 🎊 **다음 단계**

**지금 바로 시작하세요!**

```bash
# 1. GitHub에 Push
git push origin main

# 2. Railway에서 배포
# https://railway.app → New Project

# 3. 5-10분 후 완료!
```

**예상 시간:** 10분  
**비용:** 무료 ($5 크레딧)  
**결과:** 24/7 프라이빗 실행! 🎉


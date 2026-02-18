# 🚀 PersonaBot 빠른 시작 가이드

## ⚡ 5분 안에 시작하기

### 1️⃣ 필수 요구사항 확인
```bash
✅ Python 3.8 이상
✅ OpenAI API Key
✅ 인터넷 연결 (HuggingFace 모델 다운로드)
```

### 2️⃣ 설치 (2분)
```bash
# PersonaBot 폴더로 이동
cd C:\Users\yoonj\Documents\PersonaBot

# 패키지 설치
pip install -r requirements.txt
```

### 3️⃣ 환경 설정 (1분)
```bash
# 1. env.example을 .env로 복사
copy env.example .env

# 2. .env 파일 열기
notepad .env

# 3. API 키 입력
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4️⃣ 실행 (1분)
```bash
python main.py
```

---

## 📋 메뉴 선택 가이드

실행하면 다음 메뉴가 나타납니다:

```
🎯 Multi-Agent Debate System - 메뉴

[토론 주제 선택]
1. S펜 제거 결정 토론
2. 가격 전략 토론
3. 생태계 전쟁 토론
4. 폴더블의 미래 토론

[기타]
5. 커스텀 토론 생성
6. RAG 시스템 테스트
0. 종료
```

### 추천: 먼저 "6번" 선택!
```
6번을 선택하면 RAG 시스템이 제대로 작동하는지 테스트합니다.
실제 페르소나들이 어떻게 답변하는지 미리 볼 수 있습니다.
```

---

## 🎯 토론 주제별 가이드

### 1번: S펜 제거 결정 토론
**참여자**: Galaxy 충성 고객, 마케터, 개발자, 디자이너

**예상 전개**:
- Galaxy 충성 고객: "S펜은 차별화 요소, 반대!"
- 마케터: "대중화를 위해 필요, 찬성"
- 개발자: "기술적 제약, 불가피"
- 디자이너: "얇음이 더 중요, 찬성"

**예상 시간**: 5-10분

---

### 2번: 가격 전략 토론
**참여자**: 가격 민감 고객, 기술 애호가, 마케터

**예상 전개**:
- 가격 민감 고객: "230만원 너무 비싸!"
- 기술 애호가: "스펙 대비 합리적"
- 마케터: "프리미엄 포지셔닝 필요"

**예상 시간**: 5-10분

---

### 3번: 생태계 전쟁 토론
**참여자**: iPhone→Galaxy 전환자, Galaxy 충성 고객, 마케터, 개발자

**예상 전개**:
- iPhone→Galaxy: "전환했지만 생태계 아쉬움"
- Galaxy 충성 고객: "Samsung 생태계도 좋음"
- 마케터: "번들 전략으로 극복 가능"
- 개발자: "기술적 통합 개선 중"

**예상 시간**: 10-15분

---

### 4번: 폴더블의 미래 토론
**참여자**: iPhone→Galaxy 전환자, 기술 애호가, 디자이너, 마케터

**예상 전개**:
- 전환자: "폴더블이 미래다!"
- 기술 애호가: "내구성 개선되면 주류화"
- 디자이너: "폼팩터 혁신 계속될 것"
- 마케터: "5년 후 시장 30% 예상"

**예상 시간**: 10-15분

---

## 🔧 문제 해결

### 문제 1: 모듈 import 오류
```bash
ModuleNotFoundError: No module named 'autogen'

해결:
pip install pyautogen
```

### 문제 2: OpenAI API 오류
```bash
AuthenticationError: Invalid API key

해결:
1. .env 파일 확인
2. API 키 정확한지 확인
3. https://platform.openai.com/api-keys 에서 키 재생성
```

### 문제 3: HuggingFace 모델 다운로드 느림
```bash
첫 실행 시 임베딩 모델을 다운로드합니다 (~500MB)
인터넷 연결 확인하고 잠시 기다려주세요.

다운로드 위치:
C:\Users\[사용자]\.cache\huggingface\
```

### 문제 4: ChromaDB 오류
```bash
삭제 후 재실행:
rmdir /s rag\vector_stores
```

---

## 📊 예상 소요 시간

### 초기 설정
- 패키지 설치: 2-5분
- 모델 다운로드: 2-5분 (첫 실행 시)
- RAG 초기화: 30초-1분
- **총 5-10분**

### 토론 실행
- 짧은 토론: 5분
- 중간 토론: 10분
- 긴 토론: 15분

### API 비용
- 토론 1회: $0.5-1.0
- RAG 테스트: $0.1-0.2

---

## 🎓 학습 경로

### 1단계: RAG 시스템 이해
```bash
python main.py
→ 6번 선택 (RAG 시스템 테스트)
```
각 페르소나가 어떻게 답변하는지 확인

### 2단계: 간단한 토론 경험
```bash
python main.py
→ 2번 선택 (가격 전략 토론)
```
3명의 짧은 토론으로 시스템 이해

### 3단계: 복잡한 토론 참여
```bash
python main.py
→ 3번 선택 (생태계 전쟁 토론)
```
4명의 다각도 토론 경험

### 4단계: 커스터마이징
- `agents/` 파일 수정
- 페르소나 특성 변경
- 새로운 토론 주제 추가

---

## 💡 활용 팁

### Tip 1: RAG 품질 개선
```
rag/data/*.txt 파일에 더 많은 데이터 추가
→ 답변 품질 향상
```

### Tip 2: 토론 시간 조절
```python
# debate_system.py에서 조절
max_round=20  # 토론 라운드 수
```

### Tip 3: 비용 절감
```python
# main.py에서 변경
use_openai_embeddings=False  # HuggingFace 사용 (무료)
```

### Tip 4: 출력 저장
```bash
python main.py > debate_log.txt
```

---

## 📖 더 알아보기

- `README.md` - 전체 프로젝트 개요
- `SYSTEM_ARCHITECTURE.md` - 시스템 구조 상세
- `docs/persona_profiles.md` - 페르소나 프로필
- `PROJECT_SUMMARY.md` - 데이터 형식 요약

---

## 🆘 도움이 필요하면

1. README.md 확인
2. docs/ 폴더 문서 읽기
3. 코드 주석 참조
4. Issue 등록

---

**지금 바로 시작하세요!**
```bash
python main.py
```

🎉 즐거운 토론 되세요!


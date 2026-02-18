# 🧪 PersonaBot 테스트 가이드

## 🚀 단계별 테스트

### 1단계: 가장 간단한 테스트 (RAG만)
```bash
python test_simple.py
```

**테스트 내용:**
- ✅ RAG Manager 초기화
- ✅ 1개 페르소나 로드
- ✅ get_context() 메서드
- ✅ query_persona() 메서드

**예상 시간:** 30초-1분  
**API 비용:** $0.05-0.10

**성공 시 출력:**
```
✅ RAG 시스템 테스트 성공!
```

---

### 2단계: 2인 미니 토론 (AutoGen 통합)
```bash
python test_debate.py
```

**테스트 내용:**
- ✅ RAG + AutoGen 통합
- ✅ 2개 에이전트 (고객 1명, 직원 1명)
- ✅ 1라운드 토론
- ✅ RAG 컨텍스트 자동 검색

**예상 시간:** 1-2분  
**API 비용:** $0.10-0.20

**성공 시 출력:**
```
✅ 미니 토론 완료!
```

---

### 3단계: 투표 시스템 테스트
```bash
python -c "from debate.voting_system import VotingSystem; exec(open('debate/voting_system.py').read().split('if __name__')[1])"
```

또는 더 간단하게:
```bash
cd debate
python voting_system.py
```

**테스트 내용:**
- ✅ 가중치 시스템 (고객 40%, 직원 각 20%)
- ✅ 1-5점 스케일 투표
- ✅ 과반수 판정 (3.0점 기준)
- ✅ 2개 라운드 시뮬레이션

**예상 시간:** 즉시  
**API 비용:** $0 (로컬)

**성공 시 출력:**
```
✅ 테스트 완료!
   히스토리: data/voting_history_*.json
```

---

### 4단계: 전체 시스템 실행
```bash
python main.py
```

**테스트 내용:**
- ✅ 전체 시스템 초기화 (7개 페르소나)
- ✅ 메뉴 선택
- ✅ 6번: RAG 테스트
- ✅ 7번: 투표 테스트

**예상 시간:** 2-3분 (초기화)  
**API 비용:** $0.20-0.50

---

## 🔧 오류 해결 가이드

### 오류 1: ModuleNotFoundError
```
❌ ModuleNotFoundError: No module named 'autogen'
```

**해결:**
```bash
pip install pyautogen
```

---

### 오류 2: OpenAI API 오류
```
❌ AuthenticationError: Invalid API key
```

**해결:**
```bash
1. .env 파일 확인
2. OPENAI_API_KEY=sk-... (실제 키 입력)
3. API 키 유효성 확인: https://platform.openai.com/api-keys
```

---

### 오류 3: LangChain 버전 오류
```
❌ ImportError: cannot import name 'OpenAIEmbeddings'
```

**해결:**
```bash
pip install --upgrade langchain langchain-openai langchain-community
```

**또는 정확한 버전:**
```bash
pip install langchain==0.1.0 langchain-openai==0.0.5 langchain-community==0.0.20
```

---

### 오류 4: ChromaDB 오류
```
❌ ChromaDB collection error
```

**해결:**
```bash
# 벡터 스토어 삭제 후 재생성
rmdir /s rag\vector_stores
python test_simple.py
```

---

### 오류 5: AutoGen config_list 오류
```
❌ llm_config must contain 'config_list'
```

**해결:**
이미 수정됨! 모든 에이전트 파일에 최신 형식 적용:
```python
llm_config = {
    "config_list": [{
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }],
    "temperature": 0.7,
    "timeout": 120,
}
```

---

## ✅ 테스트 체크리스트

### 환경 설정
- [ ] Python 3.8 이상 설치
- [ ] pip 최신 버전
- [ ] .env 파일 생성
- [ ] OPENAI_API_KEY 설정
- [ ] 인터넷 연결

### 패키지 설치
- [ ] pip install -r requirements.txt
- [ ] pyautogen 설치 확인
- [ ] langchain 설치 확인
- [ ] chromadb 설치 확인

### 단계별 테스트
- [ ] test_simple.py (RAG만)
- [ ] test_debate.py (AutoGen 통합)
- [ ] voting_system.py (투표)
- [ ] main.py (전체 시스템)

---

## 📊 예상 비용

### API 비용 (OpenAI)
```
Embeddings (text-embedding-ada-002):
- 7개 페르소나 × 평균 100청크 = $0.01-0.02

GPT-4:
- RAG 테스트 (3개 질문) = $0.05-0.10
- 미니 토론 (1라운드) = $0.10-0.20
- 전체 토론 (3라운드) = $0.50-1.00

총 예상 비용:
- 초기 설정: $0.05
- 테스트 1회: $0.20-0.50
- 토론 1회: $0.50-1.00
```

---

## 💡 테스트 팁

### Tip 1: 단계별 진행
```
❌ 바로 main.py 실행 (X)
✅ test_simple.py → test_debate.py → main.py (O)
```

### Tip 2: 오류 로그 확인
```bash
python test_simple.py 2>&1 | tee test_log.txt
```

### Tip 3: 비용 절감
```python
# test_simple.py에서 페르소나 1개만 로드
# 전체 시스템은 검증 후 실행
```

### Tip 4: 벡터 스토어 재사용
```
첫 실행 후 vector_stores/ 폴더 생성됨
→ 다음 실행부터 빠름 (재사용)
→ 문제 있으면 삭제 후 재생성
```

---

## 🎯 성공 기준

### test_simple.py
✅ "RAG 시스템 테스트 성공!" 출력
✅ 2개 컨텍스트 검색됨
✅ 답변 생성됨

### test_debate.py
✅ "미니 토론 완료!" 출력
✅ 에이전트 대화 진행됨
✅ RAG 컨텍스트 통합됨

### voting_system.py
✅ 가중 평균 계산됨
✅ 통과/부결 판정됨
✅ 히스토리 JSON 저장됨

### main.py
✅ 7개 페르소나 로드됨
✅ 메뉴 정상 표시
✅ 기능 정상 작동

---

## 📞 문제 발생 시

### 빠른 진단
```bash
# Python 버전 확인
python --version

# 패키지 확인
pip list | grep -E "autogen|langchain|chromadb"

# API 키 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') else 'NO KEY')"
```

### 완전 초기화
```bash
# 1. 가상환경 삭제 (있다면)
# 2. 패키지 재설치
pip uninstall -y pyautogen langchain langchain-openai langchain-community chromadb
pip install -r requirements.txt

# 3. 벡터 스토어 삭제
rmdir /s rag\vector_stores

# 4. 재테스트
python test_simple.py
```

---

**단계별로 천천히 테스트하세요!** ✅

**모든 테스트 성공을 기원합니다!** 🎉


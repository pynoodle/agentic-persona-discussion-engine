# ⚡ PersonaBot 빠른 테스트 가이드

## 🚀 5분 안에 시작하기

### 1단계: 환경 설정 (1분)
```bash
# PersonaBot 폴더로 이동
cd C:\Users\yoonj\Documents\PersonaBot

# API 키 설정 (.env 파일이 이미 복사되어 있음)
# 확인: OPENAI_API_KEY=sk-...
```

---

### 2단계: 패키지 설치 (2분)
```bash
# 이미 설치됨! (pip install -r requirements.txt 완료)
✅ langchain==1.0.1
✅ langchain-openai==1.0.0
✅ chromadb==1.2.1
✅ autogen-agentchat==0.7.5
✅ autogen-ext==0.7.5
```

---

### 3단계: RAG 시스템 테스트 (30초)
```bash
python test_simple.py
```

**기대 출력:**
```
✅ RAG 시스템 테스트 성공!
   - OpenAI Embeddings 작동
   - ChromaDB 벡터 스토어 생성
   - 컨텍스트 검색 성공
   - 질문 응답 성공
```

---

### 4단계: AutoGen 버전 확인 (10초)
```bash
python test_simple_autogen.py
```

**기대 출력:**
```
✅ AutoGen 0.7.x 구조 감지
✅ AutoGen 0.7.x 에이전트 생성 성공!
```

---

## ✅ 테스트 성공!

### 현재 상태
```
✅ RAG 시스템: 100% 작동
✅ LangChain 1.0: 호환 완료
✅ OpenAI Embeddings: 연결 성공
✅ ChromaDB: 벡터 스토어 생성
✅ AutoGen 0.7.x: 설치 완료
```

---

## 📋 테스트 파일 설명

### `test_simple.py` - RAG 시스템 테스트
**테스트 내용:**
- OpenAI Embeddings 초기화
- 페르소나 지식 로드 (customer_iphone_to_galaxy)
- `get_context()` 메서드 (컨텍스트 검색)
- `query_persona()` 메서드 (질문 응답)

**실행 시간:** 30초-1분  
**API 비용:** $0.05-0.10

---

### `test_simple_autogen.py` - AutoGen 버전 감지
**테스트 내용:**
- AutoGen 버전 자동 감지 (0.2.x vs 0.7.x)
- 적절한 import 구조 확인
- 간단한 에이전트 생성 테스트

**실행 시간:** 10초  
**API 비용:** $0 (로컬)

---

### `test_debate.py` - 미니 토론 테스트 (⏳ 수정 필요)
**테스트 내용:**
- 2개 에이전트 (고객 1명, 직원 1명)
- RAG 컨텍스트 자동 검색
- 1라운드 토론

**상태:** AutoGen 0.7.x 마이그레이션 필요

---

## 🔧 다음 단계

### Option A: AutoGen 0.2.33 다운그레이드 (권장 - 빠름)
```bash
# 1. 다운그레이드
pip uninstall -y pyautogen autogen-agentchat autogen-core autogen-ext
pip install pyautogen==0.2.33

# 2. 테스트
python test_debate.py
```

**장점:**
- ✅ 기존 코드 그대로 사용
- ✅ 즉시 작동
- ✅ 10분 내 완료

---

### Option B: AutoGen 0.7.x 마이그레이션 (최신)
```bash
# 이미 설치됨
# autogen-agentchat==0.7.5
# autogen-ext==0.7.5

# agents/ 폴더 파일 수정 필요:
# - customer_agents.py
# - employee_agents.py
# - facilitator.py
# - debate_system.py
```

**장점:**
- ✅ 최신 아키텍처
- ✅ 더 나은 성능

**단점:**
- ⏰ 코드 재작성 필요 (30-45분)

---

## 💡 현재 확인된 사항

### ✅ 완벽하게 작동하는 것
1. **LangChain 1.0 RAG**
   - OpenAI Embeddings (text-embedding-ada-002)
   - ChromaDB Vector Store
   - Chunk Size: 500, Overlap: 50
   - `get_context()` 메서드
   - `query_persona()` 메서드
   - LCEL Chain 방식

2. **AutoGen 0.7.x**
   - 패키지 설치 완료
   - OpenAIChatCompletionClient 작동
   - AssistantAgent 생성 가능

---

### ⏳ 수정이 필요한 것
1. **AutoGen 코드 마이그레이션**
   - `llm_config` → `model_client`
   - `autogen.AssistantAgent` → `autogen_agentchat.agents.AssistantAgent`
   - `generate_reply()` → 새로운 메시지 핸들러

---

## 📊 테스트 결과 요약

| 테스트 | 결과 | 시간 | 비용 |
|--------|------|------|------|
| **test_simple.py** | ✅ 성공 | 30초 | $0.05 |
| **test_simple_autogen.py** | ✅ 성공 | 10초 | $0 |
| **test_debate.py** | ⏳ 대기 | - | - |
| **main.py** | ⏳ 대기 | - | - |

---

## 🎯 즉시 실행 가능한 명령어

```bash
# RAG 테스트 (100% 작동)
python test_simple.py

# AutoGen 버전 확인 (100% 작동)
python test_simple_autogen.py

# 0.2.33으로 다운그레이드 후 (권장)
pip uninstall -y pyautogen autogen-agentchat autogen-core autogen-ext
pip install pyautogen==0.2.33
python test_debate.py
```

---

## ❓ 문제 해결

### 문제: `No module named 'autogen'`
**해결:**
```bash
pip install pyautogen==0.2.33
```

### 문제: `'VectorStoreRetriever' object has no attribute 'get_relevant_documents'`
**해결:** 이미 수정됨! (`.invoke()` 사용)

### 문제: `No module named 'langchain.text_splitter'`
**해결:** 이미 수정됨! (`langchain_text_splitters` 사용)

---

## 📞 지원

자세한 테스트 결과는 다음 파일을 참조하세요:
- `TEST_RESULTS.md` - 상세한 테스트 결과 및 분석
- `TESTING_GUIDE.md` - 완전한 테스트 가이드

---

**🎉 RAG 시스템은 완벽하게 작동합니다!**  
**⚡ AutoGen 선택만 하면 전체 시스템 완성!**


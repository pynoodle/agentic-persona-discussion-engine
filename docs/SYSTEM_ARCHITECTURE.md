# 🏗️ PersonaBot 시스템 아키텍처

## 📐 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                     사용자 인터페이스                          │
│                        (main.py)                             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────┬──────────────────┬────────────┐
             │                 │                  │            │
       ┌─────▼─────┐    ┌─────▼─────┐     ┌─────▼─────┐     │
       │  RAG 시스템 │    │ 고객 에이전트 │     │ 직원 에이전트 │     │
       │ (LangChain) │    │ (AutoGen)   │     │ (AutoGen)   │     │
       └─────┬─────┘    └─────┬─────┘     └─────┬─────┘     │
             │                 │                  │            │
       ┌─────▼─────────────────▼──────────────────▼─────┐     │
       │           퍼실리테이터 (AutoGen)                 │     │
       └─────┬──────────────────────────────────────────┘     │
             │                                                 │
       ┌─────▼─────┐                                    ┌─────▼─────┐
       │ 토론 시스템  │                                    │ 투표 시스템  │
       │(GroupChat) │                                    │  (Voting)  │
       └───────────┘                                    └───────────┘
```

---

## 🧩 컴포넌트 상세

### 1. RAG Manager (LangChain)
**파일**: `rag/rag_manager.py`

**역할**:
- 페르소나별 지식 베이스 관리
- 벡터 검색 (Semantic Search)
- 컨텍스트 제공

**기술 스택**:
```python
- Embeddings: HuggingFace (무료) or OpenAI
- Vector Store: ChromaDB
- LLM: GPT-4 (OpenAI)
- Text Splitter: Recursive Character
```

**주요 메서드**:
```python
load_persona_knowledge(persona_name)  # 지식 로드
query_persona(persona_name, question) # 질의응답
get_relevant_context(persona, query) # 컨텍스트 검색
```

**데이터 플로우**:
```
텍스트 파일 (.txt)
    ↓
문서 로드 (TextLoader)
    ↓
청크 분할 (1000자, 200자 오버랩)
    ↓
임베딩 (HuggingFace)
    ↓
벡터 저장 (ChromaDB)
    ↓
질의 시 유사도 검색
    ↓
컨텍스트 반환 (Top-K)
```

---

### 2. Customer Agents (AutoGen)
**파일**: `agents/customer_agents.py`

**에이전트 구성**:
1. **iPhone→Galaxy 전환자**
   - 데이터: 570명 실제 전환 완료자
   - 특징: 확신, 만족, 비교 경험
   
2. **Galaxy 충성 고객**
   - 데이터: 110명 폴더블 전문가
   - 특징: 세대별 경험, S펜 중시
   
3. **기술 애호가**
   - 특징: 스펙 분석, 가성비
   
4. **가격 민감 고객**
   - 특징: 가격 계산, 할인 추구

**AutoGen 설정**:
```python
AssistantAgent(
    name="iPhone전환자",
    system_message="당신은 iPhone에서 Galaxy로...",
    llm_config={
        "model": "gpt-4",
        "temperature": 0.7
    }
)
```

---

### 3. Employee Agents (AutoGen)
**파일**: `agents/employee_agents.py`

**에이전트 구성**:
1. **마케터**
   - 역할: 시장 전략, 소비자 인사이트
   - 데이터: 전환율, 만족도, 장벽 분석
   
2. **개발자**
   - 역할: 기술 실현, 우선순위
   - 데이터: 버그 리포트, 사용자 불만
   
3. **디자이너**
   - 역할: UX/UI, 디자인 철학
   - 데이터: 디자인 만족도, 선호 색상

---

### 4. Facilitator (AutoGen)
**파일**: `agents/facilitator.py`

**역할**:
- 토론 주제 소개
- 발언 순서 관리
- 의견 요약
- 투표 진행
- 결론 도출

**발언 흐름**:
```
1. 주제 소개
   ↓
2. 참여자별 입장 발표
   ↓
3. 반론 및 토론
   ↓
4. 핵심 쟁점 정리
   ↓
5. 투표 진행
   ↓
6. 최종 결론
```

---

### 5. Debate System (AutoGen GroupChat)
**파일**: `debate/debate_system.py`

**핵심 기능**:
```python
create_group_chat(participants, topic)
    - GroupChat 생성
    - 참여자 구성
    - 발언 순서 설정

run_predefined_debate(debate_type)
    - 사전 정의 토론 실행
    - 's_pen_removal'
    - 'price_strategy'
    - 'ecosystem_battle'
    - 'foldable_future'
```

**GroupChat 설정**:
```python
groupchat = autogen.GroupChat(
    agents=[facilitator, agent1, agent2, ...],
    messages=[],
    max_round=20,
    speaker_selection_method="round_robin"
)
```

---

### 6. Voting System
**파일**: `debate/voting_system.py`

**기능**:
- 투표 수집
- 득표 집계
- 이유 기록
- 결과 시각화

**사용 예시**:
```python
voting = VotingSystem()
voting.cast_vote("마케터", "찬성", "시장성 고려 시 합리적")
voting.cast_vote("개발자", "찬성", "기술적 제약")
results = voting.get_results()
voting.display_results()
```

---

## 🔄 데이터 흐름

### 전체 프로세스

```
1. 초기화 단계
   ┌─────────────────────────────────────┐
   │ RAG Manager 초기화                   │
   │   - 페르소나 7개 지식 로드            │
   │   - 벡터화 (Embeddings)              │
   │   - ChromaDB 저장                    │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 에이전트 생성                         │
   │   - 고객 4명 (RAG 연결)              │
   │   - 직원 3명 (RAG 연결)              │
   │   - 퍼실리테이터 1명                  │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 토론/투표 시스템 준비                 │
   └─────────────────────────────────────┘

2. 토론 실행 단계
   ┌─────────────────────────────────────┐
   │ 사용자가 토론 주제 선택               │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ GroupChat 생성                       │
   │   - 주제별 참여자 선정                │
   │   - 배경 설명 제시                   │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 퍼실리테이터 시작 메시지              │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 에이전트별 순차 발언                  │
   │   (round_robin 방식)                 │
   │                                      │
   │ 각 발언 시:                          │
   │   1. RAG에서 관련 컨텍스트 검색       │
   │   2. GPT-4로 답변 생성               │
   │   3. 페르소나 특성 반영               │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 투표 진행                            │
   │   - 각 에이전트 투표                 │
   │   - 이유 기록                        │
   └──────────┬──────────────────────────┘
              │
   ┌──────────▼──────────────────────────┐
   │ 결과 집계 및 발표                    │
   └─────────────────────────────────────┘
```

---

## 🎯 RAG 동작 원리

### 질의응답 프로세스

```
User Question: "아이폰에서 갤럭시로 바꾸면 어떤 점이 좋아요?"
        ↓
[1] 질문 임베딩
        ↓
[2] 벡터 유사도 검색
        ↓
    ChromaDB에서 Top-3 검색
        ↓
    관련 문서:
    - "폴더블은 진짜 신세계..."
    - "삼성페이 너무 편해..."
    - "화면 크기 대만족..."
        ↓
[3] 컨텍스트 + 질문 → GPT-4
        ↓
    Prompt:
    "당신은 iPhone→Galaxy 전환자입니다.
     컨텍스트: [검색된 문서들]
     질문: [사용자 질문]
     답변:"
        ↓
[4] 페르소나 답변 생성
        ↓
    "저도 아이폰 쓰다가 바꿨는데요,
     폴더블 써보니까 진짜 신세계예요!
     화면 펼치면..."
```

---

## 🤝 AutoGen GroupChat 동작

### 대화 흐름

```
[Round 1]
퍼실리테이터: "주제는 S펜 제거입니다. 마케터님?"
    ↓
마케터: "시장 데이터를 보면 얇음 선호가 88회..."
    ↓
[Round 2]
개발자: "기술적으로 S펜 넣으면 2mm 두꺼워집니다..."
    ↓
[Round 3]
디자이너: "디자인 관점에서 얇음이 더 중요..."
    ↓
[Round 4]
Galaxy 충성 고객: "하지만 S펜이 차별화 요소인데..."
    ↓
...
    ↓
[Final Round]
퍼실리테이터: "투표하겠습니다. 찬성/반대?"
    ↓
각 에이전트 투표
    ↓
결과 발표
```

---

## 💾 데이터 레이어

### 3-Tier 데이터 구조

```
[Tier 1] 원본 데이터
├── combined_sentiment_analysis_*.json (23MB)
│   - 40,377개 원본 댓글
│   - 감성 분석 결과
│   - 메타데이터
└── precise_conversion_scores_*.json (1.8MB)
    - 2,621개 전환 의도 댓글
    - 방향/강도 분석

[Tier 2] 구조화 데이터
└── structured_reviews_*.json
    - 2,621개 구조화된 리뷰
    - pain_points 추출
    - satisfaction 추출
    - rating 자동 산출

[Tier 3] 페르소나 지식 베이스
└── rag/data/*.txt (7개 파일)
    - 페르소나별 요약
    - 핵심 인사이트
    - 실제 발언 인용
    - 통계 데이터
```

---

## 🔧 기술 스택 상세

### AutoGen
```python
용도: 멀티 에이전트 대화
주요 클래스:
- AssistantAgent: 개별 에이전트
- GroupChat: 그룹 대화
- GroupChatManager: 대화 관리

설정:
- model: gpt-4
- temperature: 0.7
- max_round: 20
- speaker_selection: round_robin
```

### LangChain
```python
용도: RAG (검색 증강 생성)
주요 컴포넌트:
- TextLoader: 문서 로드
- RecursiveCharacterTextSplitter: 청크 분할
- HuggingFaceEmbeddings: 임베딩 (무료)
- ChromaDB: 벡터 저장
- RetrievalQA: 질의응답 체인

설정:
- chunk_size: 1000
- chunk_overlap: 200
- k (검색 결과): 3
```

---

## 📊 성능 최적화

### 임베딩 모델 선택
```python
# Option 1: HuggingFace (무료, 로컬)
embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
장점: 무료, 빠름
단점: 정확도 낮음

# Option 2: OpenAI (유료, API)
embeddings = OpenAIEmbeddings()
장점: 높은 정확도
단점: API 비용
```

### 벡터 저장소
```python
ChromaDB 사용 이유:
- 로컬 저장 (외부 서버 불필요)
- 빠른 검색 속도
- Python 네이티브
- 무료

대안:
- FAISS: 더 빠름, 메모리 기반
- Pinecone: 클라우드, 유료
```

---

## 🎭 페르소나 시스템 메시지 구조

### 템플릿
```python
"""당신은 [페르소나 설명]입니다.

[페르소나 특성]
- 특징1: ...
- 특징2: ...

[주요 경험]
- 경험1
- 경험2

[대화 스타일]
- 톤: ...
- 특징: ...

[실제 발언 예시]
"실제 사용자 발언..."

RAG 시스템을 통해 실제 데이터를 참조하여 답변하세요."""
```

### 페르소나별 차별화
```python
iPhone→Galaxy 전환자:
- 확신에 찬 톤
- "진짜", "완전" 강조어
- 비교 경험 공유

Galaxy 충성 고객:
- 전문가 톤
- 세대별 비교
- 기술 용어

가격 민감 고객:
- 계산적 톤
- 가격 비교
- "비싸다" 자주 언급
```

---

## 🔐 보안 및 환경 설정

### 환경 변수
```
OPENAI_API_KEY=required
USE_OPENAI_EMBEDDINGS=optional (기본: false)
```

### API 비용 관리
```python
- Embeddings: HuggingFace 사용 (무료)
- LLM: GPT-4 사용 (필수, 유료)
- 예상 비용: 토론 1회당 $0.5-1.0
```

---

## 📈 확장 가능성

### 추가 가능한 페르소나
- 중고령 사용자
- 학생/젊은층
- 비즈니스 사용자
- 사진/영상 크리에이터

### 추가 가능한 토론 주제
- 카메라 성능 vs 가격
- AI 기능 전략
- 배터리 vs 얇음
- 색상 전략

### 시스템 개선
- 실시간 웹 UI (Streamlit)
- 토론 기록 저장
- 통계 시각화
- 다국어 지원 강화

---

**작성일**: 2025-10-21
**버전**: 1.0


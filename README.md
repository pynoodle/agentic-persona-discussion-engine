# 🤖 PersonaBot - 멀티 에이전트 토론 시스템

> **Built:** October 2025

실제 사용자 리뷰 데이터 기반 페르소나 멀티 에이전트 토론 시스템

**AutoGen + LangChain 기반**

---

## 📊 프로젝트 개요

### 목적
iPhone 17과 Galaxy Z 플립/폴드7에 대한 실제 사용자와 직원 페르소나 간의 데이터 기반 토론 시스템

### 핵심 기술
- **AutoGen**: 멀티 에이전트 대화 및 토론
- **LangChain**: RAG (Retrieval-Augmented Generation)
- **실제 데이터**: 40,377개 사용자 댓글 분석

### 데이터 소스
- **YouTube 댓글**: 40,377개
  - iPhone 17: 22,071개
  - Galaxy Z 플립/폴드7: 18,306개
- **전환 의도 분석**: 2,621개 구조화
- **수집 기간**: 2025년 9월
- **분석 완료**: 2025년 10월

---

## 🚀 빠른 시작

### 1. 설치
```bash
cd C:\Users\yoonj\Documents\PersonaBot
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# env.example을 복사하여 .env 생성
copy env.example .env

# .env 파일 편집하여 API 키 입력
OPENAI_API_KEY=your-api-key-here
```

### 3. 실행
```bash
python main.py
```

---

## 🎭 페르소나 에이전트 (7명)

### 고객 페르소나 (4명)
1. **iPhone→Galaxy 전환자** (570명 데이터)
   - 폴더블에 완전히 매료
   - 전환 완료, 높은 만족도
   - "진짜 신세계" 발언

2. **Galaxy 충성 고객** (110명 데이터)
   - 폴더블 전문가
   - 세대별 업그레이드
   - S펜 중시

3. **기술 애호가** (데이터 기반)
   - 스펙 비교 전문
   - 가성비 분석
   - 합리적 의사결정

4. **가격 민감 고객** (데이터 기반)
   - 가격 최우선
   - 할인 추구
   - 계산적 소비

### 직원 페르소나 (3명)
1. **마케터**
   - 시장 전략 수립
   - 소비자 인사이트
   - 캠페인 기획

2. **개발자**
   - 기술 실현 가능성
   - 우선순위 결정
   - 제약사항 설명

3. **디자이너**
   - UX/UI 설계
   - 디자인 철학
   - 감성 가치

---

## 📁 프로젝트 구조

```
PersonaBot/
├── data/                                          # 데이터 파일
│   ├── combined_sentiment_analysis_*.json        # 원본 감성 분석 데이터
│   ├── precise_conversion_scores_*.json          # 전환 의도 분석 (방향+강도)
│   ├── detailed_persona_segments_*.json          # 상세 페르소나 세그먼트
│   ├── conversion_persona_data_*.json            # 페르소나 프로필 데이터
│   ├── structured_reviews_*.json                 # 구조화된 리뷰 형식
│   └── improved_dynamic_topic_analysis_*.json    # 토픽 분석 결과
│
├── analysis/                                      # 분석 스크립트
│   └── convert_to_structured_reviews.py          # 구조화 변환기
│
├── docs/                                          # 문서
│   └── data_format_comparison.md                 # 데이터 형식 비교
│
└── README.md                                      # 이 파일
```

---

## 🎯 수집된 데이터 특징

### 현재 데이터 형식

우리 데이터는 **형식 1 (구조화된 리뷰)에 가장 가깝습니다**.

#### 기본 구조:
```json
{
  "id": "review_000001",
  "date": "2025-10-21",
  "rating": 4,
  "prev_device": "iPhone 15 Pro Max",
  "new_device": "iPhone 17 Air",
  "conversion_direction": "iPhone_to_iPhone",
  "conversion_intensity": 1.0,
  "conversion_level": "completed",
  "category": "하드웨어",
  "review": "에어(골드) 어제 받아서...",
  "pain_points": ["스피커품질"],
  "satisfaction": ["디자인", "가벼움"],
  "language": "ko",
  "engagement": 1
}
```

#### 포함된 정보:
✅ **전환 방향** - 4가지 (iPhone↔Galaxy, iPhone→iPhone, Galaxy→Galaxy)
✅ **전환 강도** - 0.0~1.0 스코어링
✅ **감성 분석** - positive/negative/neutral
✅ **Rating** - 1-5점 자동 산출
✅ **Pain Points** - 자동 추출
✅ **Satisfaction** - 자동 추출
✅ **언어 구분** - 한국어/영어
✅ **참여도** - 좋아요 수

---

## 📊 데이터 통계

### 전환 의도 분석
- **총 전환 의도 댓글**: 2,621개
  - iPhone 데이터: 1,057개 (4.79%)
  - Galaxy 데이터: 1,564개 (8.54%)

### Rating 분포
**iPhone:**
- 4점: 551개 (52.1%) - 긍정적
- 3점: 353개 (33.4%) - 중립
- 2점: 153개 (14.5%) - 부정적

**Galaxy:**
- 4점: 901개 (57.6%) - 긍정적
- 3점: 452개 (28.9%) - 중립
- 2점: 211개 (13.5%) - 부정적

### 전환 방향별 분포

**iPhone 데이터:**
1. iPhone → iPhone: 728개 (68.9%) - 자체 업그레이드
2. Galaxy → iPhone: 257개 (24.3%)
3. iPhone → Galaxy: 44개 (4.2%)
4. Galaxy → Galaxy: 28개 (2.6%)

**Galaxy 데이터:**
1. **iPhone → Galaxy: 1,093개 (69.9%)** ⭐ 압도적
2. Galaxy → Galaxy: 249개 (15.9%)
3. Galaxy → iPhone: 161개 (10.3%)
4. iPhone → iPhone: 61개 (3.9%)

### 전환 강도별 분포

**iPhone:**
- 완료 (1.0): 361개 (34.2%)
- 결정 (0.8): 200개 (18.9%)
- 약한 고려 (0.4): 214개 (20.2%)
- 관심 (0.2): 151개 (14.3%)
- 강한 고려 (0.6): 131개 (12.4%)

**Galaxy:**
- **완료 (1.0): 777개 (49.7%)** ⭐ 거의 절반
- 강한 고려 (0.6): 222개 (14.2%)
- 약한 고려 (0.4): 206개 (13.2%)
- 관심 (0.2): 200개 (12.8%)
- 결정 (0.8): 159개 (10.2%)

---

## 🎭 주요 페르소나 타입

### 1. **"폴더블 매력파"** (564명)
- 전환: iPhone → Galaxy
- 강도: 완료 (1.0)
- 특징: 폴더블 기술에 완전히 매료, 이미 구매 완료
- 주요 발언: "폴드7으로 넘어갔는데 진짜 너무 좋아여"

### 2. **"생태계 충성파"** (247명)
- 전환: iPhone → iPhone
- 강도: 완료 (1.0)
- 특징: Apple 생태계 충성, 정기적 업그레이드
- 주요 발언: "맥북, 아이패드 다 있어서 못 바꿔"

### 3. **"망설이는 탈주자"** (138명)
- 전환: iPhone → Galaxy
- 강도: 강한 고려 (0.6)
- 특징: 폴더블 끌리지만 생태계 장벽 고민
- 주요 발언: "앱등이인데 갤럭시 잘쓸수 있을까"

### 4. **"폴더블 덕후"** (110명)
- 전환: Galaxy → Galaxy
- 강도: 완료 (1.0)
- 특징: 폴더블 전문가, S펜 중시
- 주요 발언: "폴드 시리즈 계속 써왔어"

### 5. **"가성비 추구자"** (8명, but 평균 좋아요 376개!)
- 전환: iPhone → iPhone
- 특징: 합리적 소비, 17 일반형 선호
- 주요 발언: "17 is a value monster"

---

## 💡 페르소나봇 활용 방안

### 1. **전환 의도 상담봇**
```
User: "아이폰 쓰는데 갤럭시로 바꿀까 고민이에요"
Bot: [망설이는 탈주자 페르소나 활성화]
     "저도 그 고민 정말 많이 했어요. 10년 아이폰 써서 
      적응 못할까봐 걱정되잖아요. 저도 그랬는데..."
```

### 2. **장벽 극복 가이드봇**
```
User: "생태계 때문에 못 바꾸겠어요"
Bot: [생태계 장벽 극복 사례 제시]
     "저도 애플워치, 에어팟 다 있었는데 
      Galaxy Watch + Buds로 바꾸니까 오히려 
      삼성페이가 더 편하더라고요..."
```

### 3. **모델 추천봇**
```
User: "17 프로 vs 일반 뭐가 나아요?"
Bot: [가성비 추구자 페르소나 활성화]
     "올해는 17 일반이 진짜 가성비 미쳤어요.
      프로랑 차이가 거의 없는데 가격은..."
```

---

## 🔧 기술 스택

### 데이터 처리
- Python 3.x
- JSON
- Regex (정규표현식)

### 분석 기술
- 감성 분석 (GPT-3.5-turbo)
- 전환 의도 스코어링 (0.0~1.0)
- 토픽 분석 (키워드 기반)
- 페르소나 세분화 (복합 특성)

---

## 📈 핵심 인사이트

### 1. **Galaxy 폴더블의 압도적 흡인력**
- iPhone → Galaxy 전환: 1,093개 (평균 강도 0.73)
- 그 중 52%가 이미 구매 완료
- "폴더블은 진짜 신세계"

### 2. **iPhone 생태계 락인 효과**
- iPhone → iPhone: 728개 (68.9%)
- "맥북, 워치 때문에 못 바꿔"
- 하지만 가성비로 일반형 선택 증가

### 3. **한국 vs 글로벌 차이**
- 한국: iPhone 부정적 (52.6%), Galaxy 전환 활발
- 해외: iPhone 긍정적 (57.6%), 균형적 평가

### 4. **전환 완료율**
- Galaxy 전환: 49.7% 완료 (결정적)
- iPhone 전환: 34.2% 완료 (신중함)

---

## 🎯 데이터 형식 비교 결론

### 우리 데이터는:
✅ **형식 1 (구조화된 리뷰)에 가장 가까움**
- `id`, `date`, `rating` ✅
- `prev_device`, `new_device` ✅
- `category` ✅
- `review` (원본 텍스트) ✅
- `pain_points` ✅ (자동 추출)
- `satisfaction` ✅ (자동 추출)

### 추가 고유 필드:
- `conversion_direction` (4가지 방향)
- `conversion_intensity` (0.0~1.0 정량화)
- `conversion_level` (5단계)
- `language` (ko/en)
- `engagement` (좋아요 수)

### 형식 2 (서술형 가이드)는:
❌ **현재 형식과 맞지 않음**
- 개별 리뷰가 아닌 집계된 가이드
- 추후 리뷰 데이터를 기반으로 생성 가능

---

## 🎯 토론 주제 (4가지 내장)

### 1. S펜 제거 결정 토론
**참여자**: Galaxy 충성 고객, 마케터, 개발자, 디자이너
**쟁점**: 실용성(S펜) vs 휴대성(얇음)

### 2. 가격 전략 토론
**참여자**: 가격 민감 고객, 기술 애호가, 마케터
**쟁점**: 230만원 가격의 적정성

### 3. 생태계 전쟁 토론
**참여자**: iPhone→Galaxy 전환자, Galaxy 충성 고객, 마케터, 개발자
**쟁점**: Apple 생태계 vs Samsung 생태계

### 4. 폴더블의 미래 토론
**참여자**: iPhone→Galaxy 전환자, 기술 애호가, 디자이너, 마케터
**쟁점**: 폴더블이 주류가 될 것인가?

---

## 💡 시스템 특징

### 1. 실제 데이터 기반
- ✅ 40,377개 실제 사용자 댓글
- ✅ 2,621개 전환 의도 분석
- ✅ 방향별, 강도별 세분화
- ✅ 실제 발언 인용

### 2. RAG 시스템
- ✅ LangChain 기반
- ✅ 페르소나별 지식 베이스
- ✅ 컨텍스트 기반 답변
- ✅ 출처 추적 가능

### 3. AutoGen 멀티 에이전트
- ✅ 7개 페르소나 에이전트
- ✅ 자동 대화 진행
- ✅ 순서 관리
- ✅ 퍼실리테이터 조율

### 4. 투표 시스템
- ✅ 민주적 의사결정
- ✅ 득표 집계
- ✅ 이유 기록
- ✅ 결과 시각화

---

## 🤖 Multi-Agent Orchestration

AutoGen 기반으로 7개 페르소나 에이전트가 구조화된 절차에 따라 토론을 진행합니다.

| 컴포넌트 | 구현 내용 |
|----------|-----------|
| **Facilitator Agent** | `AssistantAgent` 기반 패시브 퍼실리테이터 — 라운드 안건 제시 및 투표 프롬프트 생성 |
| **Persona Agents** | 고객 4명 + 직원 3명, 각자 독립 system prompt와 RAG 지식 베이스 보유 |
| **Debate Mode 1** | `DebateSystem` — `MaxMessageTermination(rounds × agents × 2)`으로 발화 수 제한 |
| **Debate Mode 2** | `DeepDebateSystem` — 5단계 페이즈(Phase I~V), 페이즈별 라운드 수 명시 제어 |
| **Voting Mechanism** | 라운드 종료 후 각 에이전트가 1~5점 투표 → 가중 평균 산출 → 60% 이상(3.0/5.0) 시 가결 |
| **Structured Output** | 모든 이벤트(start / message / vote / complete)를 JSON 스트림으로 emit |

```python
# 종료 조건 예시 (debate_system.py)
MaxMessageTermination(max_messages=num_rounds * len(participants) * 2)
# 3라운드 × 3에이전트 × 2 = 최대 18개 메시지
```

## 🛡️ Stability Mechanisms

실제 구현된 안정성 장치:

| 항목 | 구현 내용 |
|------|-----------|
| **Max Iteration Limit** | `MaxMessageTermination` — 라운드·참여자 수 기반 동적 메시지 상한 (`debate_system.py:91`) |
| **Phase-based Control** | DeepDebateSystem은 5개 페이즈 × 명시적 라운드 수로 무한 루프 방지 (`deep_debate_system.py:29-60`) |
| **Consensus Threshold** | 가중 평균 ≥ 3.0 (5점 척도의 60%)일 때 가결, 결과를 `passed` 플래그로 반환 (`voting_system.py:32`) |
| **Conflict-aware Facilitation** | `simple_chat/facilitator.py`에서 turn count와 conflict 여부로 토론 페이즈 자동 전환 (opening → discussion → conflict → synthesis → conclusion) |
| **RAG Grounding** | 각 에이전트 응답에 실제 사용자 댓글 데이터(40,377개) 기반 컨텍스트 주입으로 hallucination 억제 |

## ⚠️ Failure Handling

| 항목 | 구현 내용 |
|------|-----------|
| **Session Timeout** | 30분 세션 타임아웃 — 장시간 비활성 시 자동 종료 (`app_gradio.py:48`) |
| **Agent Error Fallback** | 에이전트 응답 실패 시 try/catch로 포착 후 안전 메시지 반환 (`deep_debate_system.py:170-174`) |
| **Vote Score Validation** | 투표 점수 1~5 범위 벗어날 시 즉시 reject (`voting_system.py:158-160`) |
| **Stream Termination Guard** | `StopAsyncIteration` 예외 처리로 스트림 비정상 종료 시 debate 루프 안전하게 탈출 (`app_gradio.py:533-535`) |
| **Message Attribute Check** | 수신 메시지의 `source` / `content` 속성 존재 여부 검증 후 처리 (`debate_system.py:122`) |

---

## 📚 사용 예시

### 토론 실행
```python
from rag.rag_manager import RAGManager
from agents.customer_agents import CustomerAgents
from agents.employee_agents import EmployeeAgents
from debate.debate_system import DebateSystem

# 초기화
rag = RAGManager()
rag.load_all_personas()

customer_agents = CustomerAgents(rag)
employee_agents = EmployeeAgents(rag)

# 토론 실행
debate_system = DebateSystem(customer_agents, employee_agents, facilitator)
debate_system.run_predefined_debate('s_pen_removal')
```

### RAG 질의
```python
# iPhone→Galaxy 전환자에게 질문
result = rag.query_persona(
    'customer_iphone_to_galaxy',
    '생태계 전환이 어렵지 않았나요?'
)
print(result['answer'])
```

---

## 🎯 주요 파일

### 핵심 스크립트
- `main.py` - 메인 실행 파일
- `rag/rag_manager.py` - RAG 시스템
- `agents/customer_agents.py` - 고객 에이전트
- `agents/employee_agents.py` - 직원 에이전트
- `debate/debate_system.py` - 토론 시스템
- `debate/voting_system.py` - 투표 시스템

### 데이터 파일
- `data/structured_reviews_*.json` - 구조화된 리뷰 (2,621개)
- `data/precise_conversion_scores_*.json` - 전환 분석
- `rag/data/*.txt` - 페르소나별 지식 베이스

---

## 📊 데이터 품질

### 전환 데이터
- iPhone 데이터: 1,057개 전환 의도
- Galaxy 데이터: 1,564개 전환 의도
- 총 2,621개 구조화된 리뷰

### Rating 분포
- iPhone: 52.1% 긍정 (4점)
- Galaxy: 57.6% 긍정 (4점)

### 전환 완료율
- Galaxy 전환: 49.7% 완료
- iPhone 전환: 34.2% 완료

---

**생성일**: 2025-10-21  
**버전**: 1.0  
**FusionView 프로젝트 기반**

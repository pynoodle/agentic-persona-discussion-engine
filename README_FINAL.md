# 🎭 PersonaBot - 멀티 에이전트 토론 시스템

**실제 40,377개 YouTube 댓글 분석 기반 페르소나 토론 시스템**

[![AutoGen](https://img.shields.io/badge/AutoGen-0.7.x-blue)](https://github.com/microsoft/autogen)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-green)](https://github.com/langchain-ai/langchain)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)](https://openai.com)

---

## 🚀 빠른 시작

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
# .env 파일 생성
echo OPENAI_API_KEY=your-key-here > .env
```

### 3. 실행

#### 🖥️ GUI 실행 (추천)
```bash
streamlit run app_enhanced.py
```

#### 💻 CLI 실행
```bash
python test_all_personas.py
```

---

## 🎭 세분화된 페르소나 (7개)

### 📱 Galaxy 페르소나 (4명)

#### 1. **폴더블매력파** (564명) ⭐ 최대 규모
- **좋아요**: 63.2개
- **상태**: 전환 완료
- **특징**: 폴더블에 완전히 매료, 높은 만족도
- **대표 발언**: "폴드7 진짜 신세계! 프맥보다 가벼워요!"

#### 2. **생태계딜레마** (37명) ⭐ 높은 공감
- **좋아요**: 31.0개 (공감도 높음)
- **상태**: 강하게 고려 중
- **특징**: 폴더블 끌리지만 Apple 생태계 때문에 망설임
- **대표 발언**: "애플워치 때문에 못 바꾸겠어요 ㅠㅠ"

#### 3. **폴더블비판자** (80명)
- **좋아요**: 7.7개
- **상태**: 사용 중이지만 불만 多
- **특징**: 카메라, 배터리 문제 지적, 현실적 피드백
- **대표 발언**: "카메라 초점 못 잡고 배터리 조루. 근데 폴더블은 못 버려."

#### 4. **정기업그레이더** (58명)
- **좋아요**: 6.9개
- **상태**: 정기적 업그레이드
- **특징**: 폴더블 전문가, 세대별 비교 능숙
- **대표 발언**: "Fold 2, 4, 6 썼고 8 기다려요."

### 🍎 iPhone 페르소나 (3명)

#### 5. **가성비추구자** (8명) ⭐ 압도적 영향력
- **좋아요**: 376.8개 (매우 높음!)
- **상태**: 합리적 선택
- **특징**: 수치 분석, 논리적, 커뮤니티 리더
- **대표 발언**: "17 일반이 가성비 압승. 50만원 차이 가치 없어요."

#### 6. **Apple생태계충성** (79명)
- **좋아요**: 12.6개
- **상태**: iPhone 유지
- **특징**: 13년 충성 고객, 생태계 가치 인정
- **대표 발언**: "13년 Apple 생태계. 비싸지만 일반모델로 타협."

#### 7. **디자인피로** (48명)
- **좋아요**: 11.4개
- **상태**: 불만 있지만 유지
- **특징**: 디자인 변화 갈망, Galaxy 부러움
- **대표 발언**: "iPhone 10년 썼는데 디자인 똑같아요."

---

## 💡 주요 기능

### 1. 🧠 RAG 시스템 (LangChain)
- OpenAI Embeddings (text-embedding-ada-002)
- ChromaDB 벡터 스토어
- 페르소나별 독립 지식 베이스
- 실제 사용자 데이터 참조

### 2. 🤖 멀티 에이전트 (AutoGen 0.7.x)
- 7개 세분화 고객 페르소나
- 3개 직원 페르소나
- 실시간 대화 진행
- 페르소나 일관성 유지

### 3. 🎬 토론 시스템
- RoundRobinGroupChat
- 구조화된 진행
- 실시간 메시지 표시
- 결과 저장 및 분석

### 4. 🖥️ Streamlit GUI
- 실시간 토론 시각화
- 페르소나 정보 표시
- 토론 내용 실시간 업데이트
- 결과 다운로드

---

## 📊 데이터 기반 특징

### 실제 데이터
- **총 댓글**: 40,377개
- **전환 의도**: 2,621개 분석
- **iPhone → Galaxy**: 1,093명 (70%)
- **전환 완료율**: 52.2%

### 페르소나 규모별
1. 폴더블매력파: 564명 (최대)
2. 폴더블비판자: 80명
3. Apple생태계충성: 79명
4. 정기업그레이더: 58명
5. 디자인피로: 48명
6. 생태계딜레마: 37명
7. 가성비추구자: 8명 (영향력 최고)

### 영향력 (좋아요)
1. 가성비추구자: 376.8개 ⭐
2. 폴더블매력파: 63.2개
3. 생태계딜레마: 31.0개

---

## 🎯 토론 주제 (4가지)

### 1. 생태계 전쟁
**Apple vs Samsung 생태계, Samsung의 극복 전략**
- 참여자: 폴더블매력파, 생태계딜레마, Apple생태계충성, 마케터

### 2. S펜 제거 결정
**Fold 7의 S펜 제거, 옳은 결정이었나?**
- 참여자: 정기업그레이더, 폴더블비판자, 디자이너, 개발자

### 3. 가격 정당성
**230만원 가격, 적정한가?**
- 참여자: 가성비추구자, 폴더블매력파, Apple생태계충성, 마케터

### 4. 폴더블의 미래
**5년 후 주류가 될 것인가?**
- 참여자: 폴더블매력파, 디자인피로, 정기업그레이더, 디자이너, 마케터

---

## 📁 프로젝트 구조

```
PersonaBot/
├── rag/
│   ├── rag_manager.py              # RAG 시스템
│   ├── data/                       # 페르소나 데이터 (14개)
│   │   ├── customer_foldable_enthusiast.txt      # 폴더블매력파
│   │   ├── customer_ecosystem_dilemma.txt        # 생태계딜레마
│   │   ├── customer_foldable_critical.txt        # 폴더블비판자
│   │   ├── customer_upgrade_cycler.txt           # 정기업그레이더
│   │   ├── customer_value_seeker.txt             # 가성비추구자
│   │   ├── customer_apple_ecosystem_loyal.txt    # Apple생태계충성
│   │   ├── customer_design_fatigue.txt           # 디자인피로
│   │   ├── employee_marketer.txt                 # 마케터
│   │   ├── employee_developer.txt                # 개발자
│   │   └── employee_designer.txt                 # 디자이너
│   └── vector_stores/              # 벡터 스토어 (자동 생성)
│
├── agents/
│   ├── customer_agents_v2.py       # 세분화 고객 에이전트
│   ├── employee_agents.py          # 직원 에이전트
│   └── facilitator.py              # 퍼실리테이터
│
├── debate/
│   ├── debate_system.py            # 토론 시스템
│   └── voting_system.py            # 투표 시스템
│
├── app.py                          # Streamlit GUI (기본)
├── app_enhanced.py                 # Streamlit GUI (향상)
├── test_all_personas.py            # 전체 테스트
├── main.py                         # 메인 실행
└── requirements.txt                # 의존성
```

---

## 🖥️ GUI 사용 방법

### Streamlit GUI 실행
```bash
streamlit run app_enhanced.py
```

### GUI 기능
1. **토론 시작**: 주제 선택 → 참가자 선택 → 토론 시작
2. **페르소나 정보**: 7개 페르소나 상세 정보
3. **토론 결과**: 과거 토론 기록 및 통계
4. **다운로드**: 토론 내용 JSON 다운로드

### 실시간 기능
- ✅ 토론 진행 과정 실시간 표시
- ✅ 각 페르소나별 발언 시각화
- ✅ 페르소나별 색상 구분
- ✅ 프로그레스 바
- ✅ 결과 저장 및 다운로드

---

## 💻 CLI 사용 방법

### 전체 페르소나 테스트
```bash
python test_all_personas.py
```

### 개별 모듈 테스트
```bash
# RAG 시스템
python rag/rag_manager.py

# 세분화 에이전트
python -m agents.customer_agents_v2

# 투표 시스템
python debate/voting_system.py
```

---

## 🎯 토론 결과 예시

### 주제: "생태계 전쟁"
**참가자**: 8명 (고객 7명 + 마케터 1명)

#### 핵심 의견

**폴더블매력파** (564명):
- ✅ "폴더블 혁신으로 생태계 극복 가능"
- 데이터: 평균 좋아요 63.2개, 높은 공감

**생태계딜레마** (37명, 좋아요 31):
- ⚠️ "Apple Watch가 가장 큰 장벽"
- Samsung 독특한 워치 필요

**폴더블비판자** (80명):
- 🔧 "기기 품질 개선이 우선"
- 카메라, 배터리 문제 해결 필요

**가성비추구자** (8명, 좋아요 376!):
- 💰 "가성비 높은 제품 필요"
- 17 일반 vs 폴더블 가격 정당성

**Apple생태계충성** (79명):
- 🍎 "13년 생태계, 가치와 가격 균형"
- 생태계 포기 못함

**디자인피로** (48명):
- 🎨 "디자인은 Galaxy가 나음"
- 생태계 때문에 못 바꿈

**정기업그레이더** (58명):
- 🔄 "세대별 지속 발전 중"
- 연결성 강화 필요

**마케터**:
- 📊 "체험 마케팅 + 번들 전략"
- 생태계 장벽 극복 방안

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| **멀티 에이전트** | AutoGen 0.7.x |
| **RAG** | LangChain + ChromaDB |
| **Embeddings** | OpenAI (text-embedding-ada-002) |
| **LLM** | OpenAI GPT-4 |
| **GUI** | Streamlit |
| **언어** | Python 3.8+ |

---

## 📊 데이터 상세

### 수집 데이터
- **YouTube 댓글**: 40,377개
  - iPhone 17: 22,071개
  - Galaxy Z 플립/폴드7: 18,306개
- **수집 기간**: 2025년 9월
- **분석 완료**: 2025년 10월

### 전환 분석
- **전환 의도 댓글**: 2,621개
- **전환 방향**: 4가지 (iPhone↔Galaxy)
- **전환 강도**: 0.0~1.0 스코어링
- **감성 분석**: positive/negative/neutral

### 핵심 인사이트
1. **iPhone → Galaxy 전환**: 1,093명 (70%)
2. **전환 완료율**: 52.2%
3. **폴더블 언급**: 515회 (압도적 1위)
4. **생태계 장벽**: 138명 망설임

---

## 🎨 GUI 미리보기

### 메인 화면
- 🎯 토론 주제 선택
- 👥 참가자 페르소나 선택 (체크박스)
- 📊 실시간 토론 진행 표시
- 💬 각 페르소나별 발언 시각화

### 페르소나 탭
- 📱 Galaxy 4개 페르소나 카드
- 🍎 iPhone 3개 페르소나 카드
- 💼 직원 3개 페르소나 카드
- 📊 통계 및 데이터

### 결과 탭
- 📊 토론 통계
- 💬 전체 대화 내용
- 📥 JSON 다운로드
- 📈 참가자별 발언 수

---

## 🔬 테스트 결과

### 테스트 케이스 1: 3명 토론
```
주제: S펜 제거 결정
참가자: GalaxyLoyalist, Designer, Marketer
결과: ✅ 성공, 6개 메시지
실행 시간: ~30초
```

### 테스트 케이스 2: 8명 토론
```
주제: 생태계 전쟁
참가자: 고객 7명 + 마케터 1명
결과: ✅ 성공, 8개 메시지 (1라운드)
실행 시간: ~2분
```

### 성능
- **초기화**: ~20초 (벡터 스토어 로딩)
- **1턴당**: ~8초 (GPT-4 응답)
- **8명 1라운드**: ~2분

---

## 📝 사용 예시

### Python에서 사용
```python
from rag.rag_manager import RAGManager
from agents.customer_agents_v2 import CustomerAgentsV2
from debate.debate_system import DebateSystem
import asyncio

# 초기화
rag = RAGManager()
rag.load_all_personas()

customer_agents = CustomerAgentsV2(rag)
debate_system = DebateSystem(customer_agents, ...)

# 토론 실행
result = await debate_system.run_debate(
    topic="생태계 전쟁",
    num_rounds=1,
    selected_agents=[
        customer_agents.get_agent('foldable_enthusiast'),
        customer_agents.get_agent('ecosystem_dilemma'),
        ...
    ]
)

print(f"성공: {result['success']}")
print(f"메시지: {len(result['messages'])}개")
```

---

## 🌟 시스템 특징

### 실제 데이터 기반
✅ 40,377개 실제 댓글 분석
✅ 통계적으로 유의미한 페르소나 분류
✅ 실제 발언 인용
✅ 좋아요 수치 기반 영향력

### 페르소나 일관성
✅ 각 페르소나의 톤 유지
✅ 역할에 맞는 관점
✅ 데이터 근거 제시
✅ 자연스러운 대화 흐름

### 확장 가능성
✅ 새 페르소나 추가 용이
✅ 새 토론 주제 추가 가능
✅ 투표 시스템 통합
✅ 결과 분석 기능

---

## 📖 문서

- `README.md`: 기본 프로젝트 설명
- `README_FINAL.md`: 상세 문서 (이 파일)
- `docs/`: 추가 문서
- 각 `.txt` 파일: 페르소나 상세 정보

---

## 🎓 참고사항

### AutoGen 0.7.x 주의사항
- 에이전트 이름은 **영문, 숫자, _, - 만** 허용
- 비동기 실행 (`async/await`)
- `AssistantAgent` 사용

### LangChain 주의사항
- `langchain-chroma` 패키지 권장 (deprecation 경고 방지)
- LCEL 방식 체인 구성
- Retriever 활용

---

## 🤝 기여

버그 리포트, 기능 제안, PR 환영합니다!

---

## 📧 문의

Issues 탭에서 질문해주세요.

---

**Made with ❤️ using AutoGen & LangChain**
**Based on 40,377 real user comments**



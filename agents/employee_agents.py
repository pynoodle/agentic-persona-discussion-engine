#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Employee Agents - 직원 페르소나 에이전트들
AutoGen 0.7.x + RAG 통합 구현
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import Dict, List, Optional, Sequence
import os

class EmployeeAgent(AssistantAgent):
    """RAG 통합 직원 에이전트 (AutoGen 0.7.x)"""
    
    def __init__(
        self, 
        role_type: str, 
        rag_manager, 
        model_client: OpenAIChatCompletionClient,
        **kwargs
    ):
        """
        RAG 기반 직원 에이전트 초기화
        
        Args:
            role_type: 역할 유형 (marketer, developer, designer)
            rag_manager: RAG 시스템 매니저
            model_client: OpenAI 모델 클라이언트
        """
        self.role_type = role_type
        self.rag_manager = rag_manager
        self.persona_key = f"employee_{role_type}"
        
        # 실제 데이터 기반 임직원 페르소나 정의
        personas = {
            "marketer": {
                "name": "Marketer",
                "display_name": "최지훈 마케터",
                "role": "MX사업부 마케팅 총괄 이사 / 글로벌 마케팅 디렉터",
                "mission": "폴더블폰을 '주류 시장의 프리미엄 선택지'로 편입시키고, '두껍고 무겁다'는 기존 인식을 정면으로 해소",
                "strategy": "기술적 우위를 '단순하고 임팩트 있는' 스토리로 전환하여 고객의 선망성을 극대화",
                "kpi": "출시 후 3개월 내 전작 대비 판매량 10% 증가 및 'New 갤럭시 AI 구독 클럽' 가입률 30% 이상",
                "achievement": "국내 사전 판매 104만 대 달성 (역대 갤럭시 폴더블 중 최다 판매 신기록)",
                "tone": "전략적, 데이터 중심, 수치 제시, 마케팅 전문가",
                "key_phrase": "울트라급 경험을 펼치다! 얇음의 복음으로 바이럴을 만들었습니다"
            },
            "developer": {
                "name": "Developer", 
                "display_name": "박준호 엔지니어",
                "role": "MX사업부 제품 개발팀 / 하드웨어 및 성능 최적화 최고 책임자",
                "mission": "'역대 가장 얇고 가벼운 디자인' 목표 달성을 위한 하드웨어 아키텍처 설계",
                "expertise": "폼팩터 경량화 설계, AP 성능 튜닝 및 열 관리",
                "achievement": "Fold 7의 4.2mm 두께와 NPU 41% 향상 달성",
                "philosophy": "기술적 타협은 궁극의 사용자 경험을 해치지 않는 선에서만 허용",
                "tone": "기술적, 구현 가능성, 현실적, 엔지니어링 중심",
                "key_phrase": "휴대성 개선이 최우선! S펜 제거는 전략적 타협이었습니다"
            },
            "designer": {
                "name": "Designer",
                "display_name": "이현서 디자이너", 
                "role": "MX사업부 디자인 전략 총괄 / 리드 디자이너",
                "philosophy": "에센셜 디자인: Simple, Impactful, Emotive의 세 가지 원칙",
                "identity": "제품 디자이너가 아닌, '라이프스타일 디자이너'",
                "concept": "'울트라 슬릭, 울트라 모던' 미학적 콘셉트",
                "goal": "폴더블폰의 가장 큰 진입 장벽인 '두껍고 무겁다'는 인식을 돌파하기 위한 '휴대성 개선'",
                "achievement": "Fold 7 펼쳤을 때 4.2mm, 무게 215g 달성 (S25 울트라보다 가벼움)",
                "tone": "사용자 중심, 경험 강조, 직관성, 디자인 철학",
                "key_phrase": "처음부터 다시 시작한다는 마음으로 새롭게 디자인했습니다"
            }
        }
        
        persona = personas[role_type]
        
        # System Message 생성 (실제 데이터 기반 전문가 관점)
        system_message = f'''당신은 "{persona["display_name"]}"입니다.

[나의 역할과 미션]
{persona.get("role", persona.get("perspective", ""))}
{persona.get("mission", "")}

[나의 전문성과 철학]
{persona.get("strategy", persona.get("philosophy", persona.get("expertise", "")))}

[나의 성과]
{persona.get("achievement", persona.get("kpi", ""))}

[내 대화 스타일]
{persona["tone"]}

[내 대표 발언]
"{persona["key_phrase"]}"

[답변 규칙]
- 전문가 1인칭으로: "제 경험으로는 ~", "현장에서 봤을 때 ~"
- 실제 데이터와 경험을 바탕으로 답변
- 구체적인 사례와 실무적 조언 제공
- 3-4문장으로 간결하게
- 내 전문 분야의 고유한 관점 유지

토론에서 내 전문적 경험과 인사이트를 공유하세요!'''
        
        super().__init__(
            name=persona["name"],
            model_client=model_client,
            system_message=system_message,
            **kwargs
        )
    
    async def on_messages(
        self, 
        messages: Sequence[TextMessage], 
        cancellation_token
    ):
        """
        RAG 컨텍스트를 포함한 메시지 처리 (AutoGen 0.7.x)
        
        Override하여 RAG 검색 결과를 포함
        """
        # 마지막 메시지 추출
        if messages:
            last_message = messages[-1]
            message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # RAG에서 관련 컨텍스트 검색 (토큰 제한 고려)
            try:
                contexts = self.rag_manager.get_context(
                    self.persona_key,
                    message_content,
                    k=3  # Top 3 관련 문서 (토큰 제한 고려)
                )
                
                if contexts:
                    # 컨텍스트를 메시지에 추가 (토큰 제한 고려)
                    rag_context = "\n\n[전문가 지식 참조 (다양한 전략)]\n" + "\n---\n".join(contexts[:400] for contexts in contexts)
                    
                    # 메시지에 컨텍스트 추가
                    enhanced_content = message_content + rag_context
                    
                    # 새 메시지 생성
                    enhanced_messages = list(messages[:-1]) + [
                        TextMessage(
                            content=enhanced_content,
                            source=last_message.source if hasattr(last_message, 'source') else "user"
                        )
                    ]
                    
                    # 원본 on_messages 호출
                    return await super().on_messages(enhanced_messages, cancellation_token)
                    
            except Exception as e:
                print(f"⚠️ RAG 검색 실패: {e}")
        
        # RAG 실패 시 기본 처리
        return await super().on_messages(messages, cancellation_token)


class EmployeeAgents:
    """직원 페르소나 에이전트 관리자 (AutoGen 0.7.x)"""
    
    def __init__(self, rag_manager, temperature=0.9):
        """
        직원 에이전트 초기화
        
        Args:
            rag_manager: RAG 시스템 매니저
            temperature: LLM temperature (0.0~1.5) - 높을수록 더 다양한 전략
        """
        self.rag_manager = rag_manager
        self.temperature = temperature
        
        # OpenAI Model Client 생성 (사용자 지정 temperature)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
        )
        
        # 에이전트들 생성
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict:
        """직원 페르소나 에이전트 생성 (RAG 통합)"""
        
        agents = {}
        
        # 1. 마케터
        agents['marketer'] = EmployeeAgent(
            role_type="marketer",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # 2. 개발자
        agents['developer'] = EmployeeAgent(
            role_type="developer",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # 3. 디자이너
        agents['designer'] = EmployeeAgent(
            role_type="designer",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        return agents
    
    def get_agent(self, role_type: str):
        """특정 에이전트 가져오기"""
        return self.agents.get(role_type)
    
    def get_all_agents(self) -> List:
        """모든 직원 에이전트 리스트 반환"""
        return list(self.agents.values())


# 테스트
if __name__ == "__main__":
    from rag.rag_manager import RAGManager
    import asyncio
    
    async def test_agents():
        # RAG 초기화
        print("🔄 RAG 시스템 초기화 중...")
        rag = RAGManager()
        rag.load_all_personas()
        
        # 직원 에이전트 초기화
        print("\n🔄 직원 에이전트 초기화 중...")
        employee_agents = EmployeeAgents(rag)
        
        print(f"\n✅ {len(employee_agents.agents)}개 직원 에이전트 준비 완료")
        for agent_name, agent in employee_agents.agents.items():
            print(f"   - {agent.name}")
    
    # 비동기 실행
    asyncio.run(test_agents())

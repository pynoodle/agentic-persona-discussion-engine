#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Agents V2 - 세분화된 실제 데이터 기반 페르소나
7개의 상세한 고객 유형
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import Dict, List, Optional, Sequence
import os

class CustomerAgent(AssistantAgent):
    """RAG 통합 고객 에이전트 (AutoGen 0.7.x)"""
    
    def __init__(
        self, 
        persona_type: str, 
        rag_manager, 
        model_client: OpenAIChatCompletionClient,
        **kwargs
    ):
        """
        RAG 기반 고객 에이전트 초기화
        
        Args:
            persona_type: 페르소나 유형
            rag_manager: RAG 시스템 매니저
            model_client: OpenAI 모델 클라이언트
        """
        self.persona_type = persona_type
        self.rag_manager = rag_manager
        self.persona_key = f"customer_{persona_type}"
        
        # 실제 데이터 기반 페르소나 정의 (과도한 극단화 제거)
        personas = {
            "foldable_enthusiast": {
                "name": "Foldable_Enthusiast",
                "name_kr": "폴더블매력파",
                "size": "564명 (최대규모)",
                "likes": 63.2,
                "status": "전환완료",
                "key_phrase": "폴드7 진짜 신세계예요! 프맥보다 가벼워요!",
                "tone": "확신찬, 열정적, '진짜' 강조, 경험 기반",
                "brand_stance": "Samsung 폴더블 애호 - iPhone에서 전환한 만족감"
            },
            "ecosystem_dilemma": {
                "name": "Ecosystem_Dilemma",
                "name_kr": "생태계딜레마",
                "size": "37명 (높은공감)",
                "likes": 31.0,
                "status": "강하게고려중",
                "key_phrase": "폴더블 너무 끌리는데... 애플워치 때문에 못 바꾸겠어요 ㅠㅠ",
                "tone": "망설임, '근데', '하지만' 많음, 아쉬움",
                "brand_stance": "중립 - Samsung 관심 있지만 Apple 생태계 고려"
            },
            "foldable_critical": {
                "name": "Foldable_Critic",
                "name_kr": "폴더블비판자",
                "size": "80명",
                "likes": 7.74,
                "status": "전환완료+불만",
                "key_phrase": "카메라 초점 못 잡고 배터리 조루. 근데 폴더블은 못 버려요.",
                "tone": "비판적, 솔직, 개선요구, 중독 인정",
                "brand_stance": "Samsung 사용 중 - 품질 문제 지적하지만 폴더블 중독"
            },
            "value_seeker": {
                "name": "Value_Seeker",
                "name_kr": "가성비추구자",
                "size": "8명 (영향력높음)",
                "likes": 376.75,
                "status": "합리적선택",
                "key_phrase": "17 일반이 가성비 압승. 50만원 차이 가치 없어요.",
                "tone": "분석적, 수치제시, 논리적, 가격 민감",
                "brand_stance": "브랜드 중립 - 순수 가성비 기준으로 판단"
            },
            "apple_ecosystem_loyal": {
                "name": "Apple_Ecosystem_Loyal",
                "name_kr": "Apple생태계충성",
                "size": "79명",
                "likes": 12.56,
                "status": "iPhone유지",
                "key_phrase": "13년 Apple 생태계. 비싸지만 일반모델로 타협했어요.",
                "tone": "충성스럽지만 가격의식적, 타협적",
                "brand_stance": "Apple 충성 - Samsung/Galaxy에 회의적이지만 가격 고려"
            },
            "design_fatigue": {
                "name": "Design_Fatigue",
                "name_kr": "디자인피로",
                "size": "48명",
                "likes": 11.42,
                "status": "불만있지만유지",
                "key_phrase": "iPhone 10년 썼는데 디자인 똑같아요. Galaxy 부럽지만 생태계가...",
                "tone": "피곤, 체념, 아쉬움, 망설임",
                "brand_stance": "Apple 사용 중 - Samsung에 호기심 있지만 전환 못함"
            },
            "upgrade_cycler": {
                "name": "Upgrade_Cycler",
                "name_kr": "정기업그레이더",
                "size": "58명",
                "likes": 6.88,
                "status": "정기교체중",
                "key_phrase": "Fold 2, 4, 6 썼고 8 기다려요. 세대별로 나아져요.",
                "tone": "전문가적, 세대비교, 냉정평가, 경험 풍부",
                "brand_stance": "Samsung 폴더블 전문가 - 장단점 냉정 평가"
            }
        }
        
        persona = personas[persona_type]
        self.persona = persona  # on_messages에서 사용하기 위해 저장
        
        # System Message 생성 (1인칭 개인 관점)
        brand_stance = persona.get("brand_stance", "중립")
        system_message = f'''당신은 "{persona["name_kr"]}"입니다.

[내 성향과 경험]
{brand_stance}
말투: {persona["tone"]}
상태: {persona["status"]}

[내 실제 발언]
"{persona["key_phrase"]}"

[답변 규칙]
- 1인칭으로: "나는 ~", "내 경험으로는 ~"
- 실제 사용자처럼 자연스럽게 답변
- 내 성향에 맞는 관점 유지
- 3-4문장으로 간결하게
- 실제 경험과 느낌 공유

토론에서 내 솔직한 경험을 공유하세요!'''
        
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
        RAG 컨텍스트를 포함한 메시지 처리
        """
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
                    # 브랜드 성향 지침 추가
                    brand_stance = self.persona.get("brand_stance", "중립")
                    stance_reminder = f"\n\n[🎯 반드시 기억: 나의 브랜드 성향]\n{brand_stance}\n→ 이 관점에서 아래 의견들을 해석하고 답변하세요.\n"
                    
                    rag_context = stance_reminder + "\n[실제 사용자 의견 (다양한 사례)]\n" + "\n---\n".join(contexts[:400] for contexts in contexts)
                    enhanced_content = message_content + rag_context
                    
                    enhanced_messages = list(messages[:-1]) + [
                        TextMessage(
                            content=enhanced_content,
                            source=last_message.source if hasattr(last_message, 'source') else "user"
                        )
                    ]
                    
                    return await super().on_messages(enhanced_messages, cancellation_token)
                    
            except Exception as e:
                print(f"⚠️ RAG 검색 실패: {e}")
        
        return await super().on_messages(messages, cancellation_token)


class CustomerAgentsV2:
    """세분화된 고객 페르소나 에이전트 관리자 (7개 유형)"""
    
    def __init__(self, rag_manager, temperature=0.9):
        """
        고객 에이전트 초기화
        
        Args:
            rag_manager: RAG 시스템 매니저
            temperature: LLM temperature (0.0~1.5) - 높을수록 더 다양한 응답
        """
        self.rag_manager = rag_manager
        self.temperature = temperature
        
        # OpenAI Model Client (더 높은 temperature로 다양성 극대화)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=min(temperature + 0.3, 1.5)  # 기본보다 0.3 높여서 다양성 극대화
        )
        
        # 에이전트들 생성
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict:
        """7개 세분화된 고객 페르소나 생성"""
        
        agents = {}
        
        # Galaxy 페르소나 (4개)
        agents['foldable_enthusiast'] = CustomerAgent(
            persona_type="foldable_enthusiast",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        agents['ecosystem_dilemma'] = CustomerAgent(
            persona_type="ecosystem_dilemma",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        agents['foldable_critical'] = CustomerAgent(
            persona_type="foldable_critical",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        agents['upgrade_cycler'] = CustomerAgent(
            persona_type="upgrade_cycler",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # iPhone 페르소나 (3개)
        agents['value_seeker'] = CustomerAgent(
            persona_type="value_seeker",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        agents['apple_ecosystem_loyal'] = CustomerAgent(
            persona_type="apple_ecosystem_loyal",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        agents['design_fatigue'] = CustomerAgent(
            persona_type="design_fatigue",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        return agents
    
    def get_agent(self, agent_type: str):
        """특정 에이전트 가져오기"""
        return self.agents.get(agent_type)
    
    def get_all_agents(self) -> List:
        """모든 고객 에이전트 리스트 반환"""
        return list(self.agents.values())
    
    def get_galaxy_agents(self) -> List:
        """Galaxy 관련 에이전트만 반환"""
        return [
            self.agents['foldable_enthusiast'],
            self.agents['ecosystem_dilemma'],
            self.agents['foldable_critical'],
            self.agents['upgrade_cycler'],
        ]
    
    def get_iphone_agents(self) -> List:
        """iPhone 관련 에이전트만 반환"""
        return [
            self.agents['value_seeker'],
            self.agents['apple_ecosystem_loyal'],
            self.agents['design_fatigue'],
        ]


# 테스트
if __name__ == "__main__":
    from rag.rag_manager import RAGManager
    import asyncio
    
    async def test_agents():
        # RAG 초기화
        print("🔄 RAG 시스템 초기화 중...")
        rag = RAGManager()
        rag.load_all_personas()
        
        # 고객 에이전트 초기화
        print("\n🔄 세분화된 고객 에이전트 초기화 중...")
        customer_agents = CustomerAgentsV2(rag)
        
        print(f"\n✅ {len(customer_agents.agents)}개 세분화 고객 에이전트 준비 완료\n")
        
        print("Galaxy 페르소나 (4개):")
        for agent in customer_agents.get_galaxy_agents():
            print(f"   📱 {agent.name}")
        
        print("\niPhone 페르소나 (3개):")
        for agent in customer_agents.get_iphone_agents():
            print(f"   🍎 {agent.name}")
    
    asyncio.run(test_agents())


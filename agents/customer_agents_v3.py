#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Agents V3 - 실제 리뷰 데이터 기반 페르소나
실제 사용자 리뷰를 RAG로 사용하여 더 진정성 있는 토론 구현
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import Dict, List, Optional, Sequence
import os

class RealReviewCustomerAgent(AssistantAgent):
    """실제 리뷰 데이터 기반 고객 에이전트"""
    
    def __init__(
        self, 
        persona_type: str, 
        real_review_rag_manager, 
        model_client: OpenAIChatCompletionClient,
        **kwargs
    ):
        """
        실제 리뷰 데이터 기반 고객 에이전트 초기화
        
        Args:
            persona_type: 페르소나 유형
            real_review_rag_manager: 실제 리뷰 RAG 시스템 매니저
            model_client: OpenAI 모델 클라이언트
        """
        self.persona_type = persona_type
        self.real_review_rag_manager = real_review_rag_manager
        self.persona_key = f"customer_{persona_type}"
        
        # 실제 데이터 기반 페르소나 정의 (간소화)
        personas = {
            "foldable_enthusiast": {
                "name": "Foldable_Enthusiast",
                "name_kr": "폴더블매력파",
                "description": "iPhone에서 Galaxy 폴더블로 전환한 만족한 사용자",
                "tone": "확신찬, 열정적, 경험 기반",
                "brand_stance": "Samsung 폴더블 애호 - iPhone에서 전환한 만족감"
            },
            "ecosystem_dilemma": {
                "name": "Ecosystem_Dilemma", 
                "name_kr": "생태계딜레마",
                "description": "Galaxy 관심 있지만 Apple 생태계 때문에 망설이는 사용자",
                "tone": "망설임, 아쉬움, 고민",
                "brand_stance": "중립 - Samsung 관심 있지만 Apple 생태계 고려"
            },
            "foldable_critical": {
                "name": "Foldable_Critic",
                "name_kr": "폴더블비판자", 
                "description": "Galaxy 폴더블 사용 중이지만 문제점을 지적하는 사용자",
                "tone": "비판적, 솔직, 개선요구",
                "brand_stance": "Samsung 사용 중 - 품질 문제 지적하지만 폴더블 중독"
            },
            "value_seeker": {
                "name": "Value_Seeker",
                "name_kr": "가성비추구자",
                "description": "가격 대비 성능을 중시하는 합리적 소비자",
                "tone": "분석적, 수치제시, 논리적",
                "brand_stance": "브랜드 중립 - 순수 가성비 기준으로 판단"
            },
            "apple_ecosystem_loyal": {
                "name": "Apple_Ecosystem_Loyal",
                "name_kr": "Apple생태계충성",
                "description": "Apple 생태계에 충성하지만 가격을 고려하는 사용자",
                "tone": "충성스럽지만 현실적, 타협적",
                "brand_stance": "Apple 충성 - Samsung/Galaxy에 회의적이지만 가격 고려"
            },
            "design_fatigue": {
                "name": "Design_Fatigue",
                "name_kr": "디자인피로",
                "description": "iPhone 디자인에 피로감을 느끼는 장기 사용자",
                "tone": "피곤, 체념, 아쉬움",
                "brand_stance": "Apple 사용 중 - Samsung에 호기심 있지만 전환 못함"
            },
            "upgrade_cycler": {
                "name": "Upgrade_Cycler",
                "name_kr": "정기업그레이더",
                "description": "정기적으로 기기를 업그레이드하는 사용자",
                "tone": "경험적, 비교적, 트렌드 민감",
                "brand_stance": "브랜드 중립 - 최신 기술과 트렌드 추구"
            }
        }
        
        if persona_type not in personas:
            raise ValueError(f"Unknown persona type: {persona_type}")
        
        self.persona = personas[persona_type]
        
        # 시스템 프롬프트 생성
        system_prompt = f"""당신은 {self.persona['name_kr']} ({self.persona['name']}) 페르소나입니다.

**페르소나 특성:**
- {self.persona['description']}
- 말투: {self.persona['tone']}
- 브랜드 성향: {self.persona['brand_stance']}

**중요한 지침:**
1. 실제 사용자 리뷰 데이터를 기반으로 답변하세요
2. 자신의 경험과 의견을 솔직하게 표현하세요
3. 다른 페르소나와 토론할 때는 자신의 입장을 명확히 하세요
4. 감정적이거나 극단적인 표현보다는 현실적인 관점을 유지하세요
5. 구체적인 사용 경험이나 사례를 들어 설명하세요

**응답 스타일:**
- 자연스러운 대화체 사용
- 개인적 경험과 의견 중심
- 감정과 논리를 균형있게 표현
- 다른 의견에 대한 존중과 반박을 적절히 조화

실제 사용자로서의 진정성 있는 의견을 표현하세요."""

        super().__init__(
            name=self.persona['name'],
            model_client=model_client,
            system_message=system_prompt,
            **kwargs
        )
    
    async def on_messages(
        self, 
        messages: Sequence[TextMessage], 
        cancellation_token
    ):
        """
        실제 리뷰 데이터를 포함한 메시지 처리
        """
        if messages:
            last_message = messages[-1]
            message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # 실제 리뷰에서 관련 컨텍스트 검색
            try:
                contexts = self.real_review_rag_manager.get_context(
                    self.persona_type,
                    message_content,
                    k=3  # Top 3 관련 리뷰
                )
                
                if contexts:
                    # 브랜드 성향 지침 추가
                    brand_stance = self.persona.get("brand_stance", "중립")
                    stance_reminder = f"\n\n[🎯 나의 브랜드 성향]\n{brand_stance}\n→ 이 관점에서 아래 실제 사용자 의견들을 참고하여 답변하세요.\n"
                    
                    rag_context = stance_reminder + "\n[실제 사용자 리뷰 참고자료]\n" + "\n---\n".join(contexts)
                    enhanced_content = message_content + rag_context
                    
                    enhanced_messages = list(messages[:-1]) + [
                        TextMessage(
                            content=enhanced_content,
                            source=last_message.source if hasattr(last_message, 'source') else "user"
                        )
                    ]
                    
                    return await super().on_messages(enhanced_messages, cancellation_token)
                    
            except Exception as e:
                print(f"⚠️ Real review search failed: {e}")
        
        return await super().on_messages(messages, cancellation_token)


class RealReviewCustomerAgentsV3:
    """실제 리뷰 데이터 기반 고객 페르소나 에이전트 관리자"""
    
    def __init__(self, real_review_rag_manager, temperature=0.9):
        """
        실제 리뷰 데이터 기반 고객 에이전트 초기화
        
        Args:
            real_review_rag_manager: 실제 리뷰 RAG 시스템 매니저
            temperature: 모델 온도 설정
        """
        self.real_review_rag_manager = real_review_rag_manager
        
        # OpenAI 모델 클라이언트 설정
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature
        )
        
        # 에이전트들 생성
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict:
        """7개 세분화된 고객 페르소나 생성"""
        
        agents = {}
        
        # Galaxy 페르소나 (4개)
        agents['foldable_enthusiast'] = RealReviewCustomerAgent(
            persona_type="foldable_enthusiast",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        agents['ecosystem_dilemma'] = RealReviewCustomerAgent(
            persona_type="ecosystem_dilemma",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        agents['foldable_critical'] = RealReviewCustomerAgent(
            persona_type="foldable_critical",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        agents['upgrade_cycler'] = RealReviewCustomerAgent(
            persona_type="upgrade_cycler",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        # iPhone 페르소나 (3개)
        agents['value_seeker'] = RealReviewCustomerAgent(
            persona_type="value_seeker",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        agents['apple_ecosystem_loyal'] = RealReviewCustomerAgent(
            persona_type="apple_ecosystem_loyal",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        agents['design_fatigue'] = RealReviewCustomerAgent(
            persona_type="design_fatigue",
            real_review_rag_manager=self.real_review_rag_manager,
            model_client=self.model_client,
        )
        
        return agents
    
    def get_agent(self, persona_type: str) -> Optional[RealReviewCustomerAgent]:
        """특정 페르소나 에이전트 반환"""
        return self.agents.get(persona_type)
    
    def get_all_agents(self) -> Dict[str, RealReviewCustomerAgent]:
        """모든 에이전트 반환"""
        return self.agents
    
    def get_agent_names(self) -> List[str]:
        """에이전트 이름 목록 반환"""
        return list(self.agents.keys())
    
    def get_persona_stats(self) -> Dict[str, Dict]:
        """페르소나별 통계 정보"""
        stats = {}
        for persona_name in self.agents.keys():
            stats[persona_name] = self.real_review_rag_manager.get_persona_stats(persona_name)
        return stats

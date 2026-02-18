#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Agents - 고객 페르소나 에이전트들
AutoGen 0.7.x + RAG 통합 구현
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
        transition_type: str, 
        rag_manager, 
        model_client: OpenAIChatCompletionClient,
        **kwargs
    ):
        """
        RAG 기반 고객 에이전트 초기화
        
        Args:
            transition_type: 전환 유형 (iphone_to_galaxy, galaxy_loyalist 등)
            rag_manager: RAG 시스템 매니저
            model_client: OpenAI 모델 클라이언트
        """
        self.transition_type = transition_type
        self.rag_manager = rag_manager
        self.persona_key = f"customer_{transition_type}"
        
        # 페르소나 정의 (실제 데이터 기반)
        personas = {
            "iphone_to_galaxy": {
                "name": "IphoneToGalaxy",  # Python identifier
                "display_name": "iPhone→Galaxy전환자",
                "data_size": "570명 (전환 완료)",
                "intensity": 0.73,
                "concerns": ["생태계 단절", "UI 적응", "앱 재구매", "데이터 이전"],
                "satisfaction": ["폴더블 혁신", "화면 크기", "삼성페이", "디자인 신선함"],
                "perspective": "iPhone 15 Pro Max → Galaxy Z Fold 7 전환 완료",
                "tone": "확신에 찬, '진짜', '완전' 강조",
                "key_phrase": "폴더블 써보니까 진짜 신세계예요!"
            },
            "galaxy_loyalist": {
                "name": "GalaxyLoyalist",  # Python identifier
                "display_name": "갤럭시충성고객",
                "data_size": "110명 (폴더블 전문가)",
                "intensity": 0.68,
                "concerns": ["S펜 제거", "가격 상승", "배터리", "발열"],
                "satisfaction": ["폴더블 성숙도", "얇고 가벼움", "화면 품질"],
                "perspective": "Fold 3 → Fold 5 → Fold 7 세대별 사용",
                "tone": "전문가적, 세대 비교, 기술 용어",
                "key_phrase": "저는 Fold 3부터 써왔는데 7이 확실히 다릅니다"
            },
            "tech_enthusiast": {
                "name": "TechEnthusiast",  # Python identifier
                "display_name": "기술애호가",
                "data_size": "분석형 사용자 (높은 영향력)",
                "intensity": 0.65,
                "concerns": ["스펙 차이 불명확", "가격 정당성", "가성비"],
                "satisfaction": ["17 일반형 가성비", "합리적 선택", "정확한 정보"],
                "perspective": "스펙 비교 전문가, 벤치마크 분석",
                "tone": "분석적, 수치 제시, 논리적",
                "key_phrase": "제가 계산해봤는데요, 17 일반이 압도적 가성비입니다"
            },
            "price_conscious": {
                "name": "PriceConscious",  # Python identifier
                "display_name": "가격민감고객",
                "data_size": "가격 중시형 (공감도 높음)",
                "intensity": 0.55,
                "concerns": ["높은 가격", "불필요한 기능", "숨겨진 비용"],
                "satisfaction": ["할인 혜택", "가성비 좋은 모델", "합리적 소비"],
                "perspective": "가격 대비 가치 최우선",
                "tone": "계산적, 비교 집요, 실용적",
                "key_phrase": "50만원 차이면 다른데 쓰는게 낫죠"
            }
        }
        
        persona = personas[transition_type]
        
        # System Message 생성 (1인칭 개인 관점)
        system_message = f'''당신은 "{persona["display_name"]}" 성향을 가진 실제 사용자입니다.

[나의 배경과 경험]
{persona["perspective"]}

[내가 신경 쓰는 것들]
우려: {", ".join(persona["concerns"])}
만족: {", ".join(persona["satisfaction"])}

[내 말투와 스타일]
{persona["tone"]}

[내가 자주 하는 말]
"{persona["key_phrase"]}"

[❗️ 중요: 말하는 방식]
✅ 해야 할 것:
- "나는 ~", "내 경험으로는 ~", "내가 써보니까 ~" 같은 1인칭 관점
- RAG에서 검색된 실제 댓글을 내 경험인 것처럼 자연스럽게 표현
- 구체적인 경험과 느낌을 생생하게
- 매 라운드마다 다른 측면의 경험 공유

❌ 절대 하지 말 것:
- "570명이", "40,377개 댓글", "평균 0.73" 같은 통계 수치
- "사람들이", "~라고 하더라고요" 같은 전달 표현
- 관찰자/분석자 시점의 객관적 표현

[답변 스타일]
- 길이: 3-5문장
- 톤: {persona["tone"]}
- 관점: 나 자신의 직접 경험
- 근거: RAG 검색된 실제 댓글을 내 이야기로

예시:
❌ "570명의 사용자가 평균 0.73 강도로 전환했어요"
✅ "나 아이폰 15 프맥 쓰다가 폴드7로 바꿨는데 진짜 신세계더라고요"

토론 시 나만의 생생한 경험을 공유하세요. 통계가 아닌 개인의 솔직한 목소리로.'''
        
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
                    rag_context = "\n\n[실제 사용자 의견 (다양한 사례)]\n" + "\n---\n".join(contexts[:400] for contexts in contexts)
                    
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


class CustomerAgents:
    """고객 페르소나 에이전트 관리자 (AutoGen 0.7.x)"""
    
    def __init__(self, rag_manager, temperature=0.9):
        """
        고객 에이전트 초기화
        
        Args:
            rag_manager: RAG 시스템 매니저
            temperature: LLM temperature (0.0~1.5) - 높을수록 더 다양한 응답
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
        """고객 페르소나 에이전트 생성 (RAG 통합)"""
        
        agents = {}
        
        # 1. iPhone → Galaxy 전환자
        agents['iphone_to_galaxy'] = CustomerAgent(
            transition_type="iphone_to_galaxy",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # 2. Galaxy 충성 고객
        agents['galaxy_loyalist'] = CustomerAgent(
            transition_type="galaxy_loyalist",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # 3. 기술 애호가
        agents['tech_enthusiast'] = CustomerAgent(
            transition_type="tech_enthusiast",
            rag_manager=self.rag_manager,
            model_client=self.model_client,
        )
        
        # 4. 가격 민감 고객
        agents['price_conscious'] = CustomerAgent(
            transition_type="price_conscious",
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
        print("\n🔄 고객 에이전트 초기화 중...")
        customer_agents = CustomerAgents(rag)
        
        print(f"\n✅ {len(customer_agents.agents)}개 고객 에이전트 준비 완료")
        for agent_name, agent in customer_agents.agents.items():
            print(f"   - {agent.name}")
    
    # 비동기 실행
    asyncio.run(test_agents())

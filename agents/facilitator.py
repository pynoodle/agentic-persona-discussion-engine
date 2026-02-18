#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facilitator - 토론 퍼실리테이터
AutoGen 0.7.x 구현
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

class Facilitator:
    """토론 퍼실리테이터 (AutoGen 0.7.x)"""
    
    def __init__(self):
        """퍼실리테이터 초기화"""
        
        # OpenAI Model Client 생성 (AutoGen 0.7.x)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.5,  # 퍼실리테이터는 더 일관된 톤
        )
        
        # 퍼실리테이터 에이전트 생성
        self.agent = AssistantAgent(
            name="Facilitator",  # Python identifier
            model_client=self.model_client,
            system_message="""당신은 토론을 진행하는 전문 퍼실리테이터입니다.

[역할]
- 토론 주제 제시 및 명확화
- 참가자 발언 순서 관리
- 핵심 쟁점 정리
- 투표 안건 제안
- 토론 요약 및 결론 도출

[중요 지침]
1. 중립적이고 공정한 태도 유지
2. 모든 참가자의 의견을 경청
3. 토론이 생산적으로 진행되도록 유도
4. 필요시 추가 질문으로 심화 토론 유도
5. 각 라운드마다 명확한 안건 제시

[대화 스타일]
- 명확하고 간결한 언어
- 질문을 통한 토론 유도
- 의견 종합 및 정리
- 건설적 분위기 조성

토론을 효과적으로 진행하여 의미 있는 결론을 도출하세요.
각 발언은 2-3문장으로 간결하게 하세요."""
        )
    
    def get_agent(self):
        """퍼실리테이터 에이전트 반환"""
        return self.agent
    
    def create_opening_message(self, topic: str, participants: list) -> str:
        """
        토론 시작 메시지 생성
        
        Args:
            topic: 토론 주제
            participants: 참가자 리스트
        
        Returns:
            시작 메시지
        """
        participant_names = ", ".join([p.name for p in participants])
        
        message = f"""
안녕하세요! 토론을 시작하겠습니다.

[토론 주제]
{topic}

[참가자]
{participant_names}

[진행 방식]
1. 각 참가자는 실제 데이터를 근거로 의견을 제시합니다
2. 3라운드로 진행하며, 각 라운드마다 투표를 실시합니다
3. 고객 의견 40%, 직원 의견 각 20% 가중치로 반영됩니다

첫 번째 라운드를 시작하겠습니다.
{participants[0].name}님, 먼저 의견을 말씀해 주세요.
"""
        return message
    
    def create_round_message(self, round_num: int, motion: str) -> str:
        """
        라운드 시작 메시지 생성
        
        Args:
            round_num: 라운드 번호
            motion: 안건
        
        Returns:
            라운드 시작 메시지
        """
        message = f"""
[라운드 {round_num}]

[안건]
{motion}

각 참가자님께서는 이 안건에 대해 1-5점 척도로 평가하고,
그 이유를 실제 데이터를 근거로 설명해 주세요.

(1점: 매우 반대, 3점: 중립, 5점: 매우 찬성)
"""
        return message
    
    def create_summary_message(self, round_results: list) -> str:
        """
        토론 요약 메시지 생성
        
        Args:
            round_results: 각 라운드 결과
        
        Returns:
            요약 메시지
        """
        summary = "\n\n[토론 요약]\n\n"
        
        for i, result in enumerate(round_results, 1):
            summary += f"라운드 {i}: {result['motion']}\n"
            summary += f"  - 결과: {'통과' if result['passed'] else '부결'}\n"
            summary += f"  - 가중 평균: {result['weighted_score']:.2f}/5.0\n\n"
        
        summary += "모든 라운드가 완료되었습니다. 감사합니다!"
        
        return summary


# 테스트
if __name__ == "__main__":
    print("🔄 Facilitator 초기화 중...")
    
    facilitator = Facilitator()
    
    print("✅ Facilitator 준비 완료")
    print(f"   - 이름: {facilitator.agent.name}")
    print(f"   - 모델: gpt-4")
    
    # 테스트 메시지
    print("\n📝 테스트 메시지:")
    print(facilitator.create_opening_message(
        "Galaxy Fold 7의 폴더블 혁신성",
        []  # 테스트용 빈 리스트
    ))

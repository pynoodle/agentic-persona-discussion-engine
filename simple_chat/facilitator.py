#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
토론 진행자 (Facilitator)
멀티페르소나 토론을 조율하고 요약하는 역할
"""

import openai
from typing import List, Dict, Optional
import random

class Facilitator:
    def __init__(self, openai_api_key: str):
        """토론 진행자 초기화"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # 진행자 정보
        self.name = "김진수 (토론 진행자)"
        self.role = "삼성전자 MX사업부 전략 기획팀장"
        self.description = "갤럭시 Z 시리즈 전략 수립을 위한 토론을 조율하고 의견을 종합하는 역할"
        
        # 토론 단계 정의
        self.debate_phases = {
            "opening": "토론 시작 및 주제 소개",
            "discussion": "참가자들의 의견 교환",
            "conflict": "의견 충돌 및 논쟁",
            "synthesis": "의견 종합 및 합의점 모색",
            "conclusion": "최종 결론 및 액션 아이템 도출"
        }
    
    def get_facilitator_response(self, phase: str, topic: str, participants: List[str], 
                               recent_messages: List[Dict], turn_count: int) -> str:
        """토론 진행자의 응답 생성"""
        
        # 단계별 프롬프트 생성
        system_prompt = f"""당신은 {self.name}입니다.

역할: {self.role}
설명: {self.description}

현재 토론 상황:
- 주제: {topic}
- 참가자: {', '.join(participants)}
- 토론 단계: {self.debate_phases.get(phase, '일반 토론')}
- 진행 턴: {turn_count}번째

토론 진행자로서의 역할:
1. 토론을 체계적으로 진행하고 조율
2. 각 참가자의 의견을 균형있게 듣고 정리
3. 의견 충돌 시 중재하고 합의점 모색
4. 핵심 이슈를 정리하고 다음 단계 제시
5. 최종 결론 도출 및 액션 아이템 정리

지침:
- 객관적이고 중립적인 입장 유지
- 각 참가자의 전문성을 인정하고 존중
- 토론이 건설적으로 진행되도록 유도
- 구체적이고 실행 가능한 제안 제시
- 한국어로 자연스럽게 응답
- 3-5문장으로 간결하게 응답"""

        # 최근 메시지들을 컨텍스트로 포함
        context_messages = []
        for msg in recent_messages[-6:]:  # 최근 6개 메시지만 포함
            if msg.get("role") == "user":
                context_messages.append(f"사용자: {msg.get('content', '')}")
            elif msg.get("role") == "assistant":
                context_messages.append(f"참가자: {msg.get('content', '')}")
        
        context_text = "\n".join(context_messages) if context_messages else "토론 시작 전"
        
        # 단계별 맞춤 메시지 생성
        phase_prompts = {
            "opening": f"토론을 시작하겠습니다. 주제 '{topic}'에 대해 각자의 전문 분야 관점에서 의견을 말씀해 주세요.",
            "discussion": f"좋은 의견들이 나오고 있습니다. 더 구체적인 내용이나 다른 관점이 있으시면 말씀해 주세요.",
            "conflict": f"의견 차이가 있네요. 서로의 입장을 이해하고 공통점을 찾아보겠습니다.",
            "synthesis": f"지금까지의 의견들을 정리해보겠습니다. 핵심 이슈와 해결 방안을 도출해보죠.",
            "conclusion": f"토론을 마무리하겠습니다. 최종 결론과 실행 계획을 정리해보겠습니다."
        }
        
        user_message = phase_prompts.get(phase, f"토론을 계속 진행하겠습니다. {topic}에 대한 의견이 있으시면 말씀해 주세요.")
        
        # 채팅 히스토리 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"최근 토론 내용:\n{context_text}\n\n{user_message}"}
        ]
        
        try:
            # OpenAI API 호출
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating facilitator response: {e}")
            return "토론을 계속 진행하겠습니다. 각자의 의견을 말씀해 주세요."
    
    def determine_next_phase(self, turn_count: int, has_conflict: bool = False) -> str:
        """다음 토론 단계 결정"""
        if turn_count <= 2:
            return "opening"
        elif turn_count <= 8:
            return "discussion"
        elif has_conflict and turn_count <= 12:
            return "conflict"
        elif turn_count <= 16:
            return "synthesis"
        else:
            return "conclusion"
    
    def get_participant_order(self, participants: List[str]) -> List[str]:
        """참가자 발언 순서 결정"""
        # 랜덤하게 순서 섞기
        return random.sample(participants, len(participants))
    
    def summarize_discussion(self, all_messages: List[Dict]) -> str:
        """토론 전체 요약"""
        system_prompt = f"""당신은 {self.name}입니다.

토론을 종료하고 전체 내용을 요약해주세요.

요약 형식:
1. 주요 논의 사항
2. 핵심 의견들
3. 합의된 내용
4. 향후 액션 아이템

간결하고 명확하게 정리해주세요."""

        # 모든 메시지 내용 추출
        discussion_text = ""
        for msg in all_messages:
            if msg.get("content"):
                discussion_text += f"{msg.get('content')}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 토론 내용을 요약해주세요:\n\n{discussion_text}"}
        ]
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "토론이 완료되었습니다. 모든 참가자들의 의견이 수렴되었습니다."

def main():
    """테스트 함수"""
    import os
    from dotenv import load_dotenv
    
    # 환경 변수 로드
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("OpenAI API key not found!")
        return
    
    # 진행자 초기화
    facilitator = Facilitator(api_key)
    
    # 테스트 응답 생성
    test_participants = ["마케터", "엔지니어", "디자이너"]
    test_topic = "갤럭시 Z 폴드 7의 S펜 제거 결정에 대한 의견"
    
    response = facilitator.get_facilitator_response(
        phase="opening",
        topic=test_topic,
        participants=test_participants,
        recent_messages=[],
        turn_count=1
    )
    
    print(f"Facilitator Response: {response}")

if __name__ == "__main__":
    main()

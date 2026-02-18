#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debate System - 멀티 에이전트 토론 시스템
AutoGen 0.7.x + RAG 통합
"""

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from typing import List, Dict
import asyncio


def safe_print(msg):
    """Windows 인코딩 오류 방지용 안전한 print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 이모지 및 특수문자 제거 후 출력
        import re
        clean_msg = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean_msg)

class DebateSystem:
    """멀티 에이전트 토론 시스템 (AutoGen 0.7.x)"""
    
    def __init__(self, customer_agents, employee_agents, facilitator, voting_system=None):
        """
        토론 시스템 초기화
        
        Args:
            customer_agents: 고객 에이전트 관리자
            employee_agents: 직원 에이전트 관리자
            facilitator: 퍼실리테이터
            voting_system: 투표 시스템 (선택사항)
        """
        self.customer_agents = customer_agents
        self.employee_agents = employee_agents
        self.facilitator = facilitator
        self.voting_system = voting_system
        
        # 토론 주제 정의
        self.debate_topics = {
            1: "Galaxy Fold 7의 폴더블 혁신성이 iPhone 사용자 전환에 충분한가?",
            2: "생태계 장벽(Apple → Samsung)을 극복할 수 있는 실질적 방안은?",
            3: "가격 프리미엄(100만원+)이 정당화될 수 있는가?",
            4: "30일 무료 체험 + 번들 할인 전략의 효과는?",
            5: "커스텀 토론 (사용자 정의)",
        }
    
    async def run_debate_streaming(
        self, 
        topic: str, 
        num_rounds: int = 3,
        selected_agents: List = None
    ):
        """
        토론 실행 with 실시간 스트리밍 (제너레이터)
        
        Args:
            topic: 토론 주제
            num_rounds: 라운드 수
            selected_agents: 선택된 에이전트 리스트
        
        Yields:
            Dict: {'type': 'message/summary/vote', 'data': ...}
        """
        # 참가 에이전트 선택
        if selected_agents is None:
            participants = [
                self.customer_agents.get_agent('iphone_to_galaxy'),
                self.customer_agents.get_agent('tech_enthusiast'),
                self.employee_agents.get_agent('marketer'),
            ]
        else:
            participants = selected_agents
        
        # 시작 메시지
        yield {
            'type': 'start',
            'data': {
                'topic': topic,
                'participants': [agent.name for agent in participants],
                'num_rounds': num_rounds
            }
        }
        
        # RoundRobinGroupChat 생성 - 충분한 메시지 수 허용
        termination = MaxMessageTermination(max_messages=num_rounds * len(participants) * 2)
        
        group_chat = RoundRobinGroupChat(
            participants=participants,
            termination_condition=termination,
        )
        
        # 토론 시작 메시지
        initial_message = TextMessage(
            content=f"""[토론 주제]
{topic}

[진행 방식]
- {num_rounds}라운드로 진행
- 각자의 페르소나와 실제 데이터를 근거로 의견 제시
- 간단명료하게 3-5문장으로 답변

첫 번째 참가자부터 의견을 말씀해 주세요.""",
            source="facilitator"
        )
        
        try:
            all_messages = []
            message_count = 0
            round_messages = []
            
            # 스트리밍 실행
            async for message in group_chat.run_stream(
                task=initial_message,
                cancellation_token=CancellationToken()
            ):
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    message_count += 1
                    all_messages.append(message)
                    round_messages.append(message)
                    
                    # 실시간 메시지 yield
                    yield {
                        'type': 'message',
                        'data': {
                            'source': message.source,
                            'content': message.content,
                            'index': message_count
                        }
                    }
                    
                    # 라운드별 요약 (매 참가자 수만큼 메시지마다)
                    if message_count % len(participants) == 0 and message_count > 0:
                        round_num = message_count // len(participants)
                        
                        # 퍼실리테이터 요약
                        summary = self._generate_round_summary(round_messages, round_num)
                        yield {
                            'type': 'summary',
                            'data': {
                                'round': round_num,
                                'summary': summary
                            }
                        }
                        
                        # 중간 투표
                        if self.voting_system and round_num < num_rounds:
                            vote_result = self._conduct_round_vote(
                                participants, 
                                round_num, 
                                topic
                            )
                            yield {
                                'type': 'vote',
                                'data': vote_result
                            }
                        
                        round_messages = []
            
            # 최종 결과
            yield {
                'type': 'complete',
                'data': {
                    'topic': topic,
                    'num_rounds': num_rounds,
                    'participants': [agent.name for agent in participants],
                    'messages': all_messages,
                    'success': True
                }
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'data': {
                    'error': str(e)
                }
            }
    
    def _generate_round_summary(self, messages: List, round_num: int) -> str:
        """라운드 요약 생성"""
        summary_parts = []
        for msg in messages:
            if hasattr(msg, 'source') and hasattr(msg, 'content'):
                # 첫 문장만 추출
                first_sentence = msg.content.split('.')[0] if '.' in msg.content else msg.content[:50]
                summary_parts.append(f"- {msg.source}: {first_sentence}...")
        
        summary = f"""
📊 라운드 {round_num} 요약

{chr(10).join(summary_parts)}

주요 쟁점: {"가격 대비 가치" if round_num == 1 else "생태계 전환" if round_num == 2 else "최종 결론"}
"""
        return summary
    
    def _conduct_round_vote(self, participants: List, round_num: int, topic: str) -> Dict:
        """라운드별 중간 투표"""
        import random
        
        votes = {}
        for agent in participants:
            # 실제로는 LLM이 판단하지만 여기서는 간소화
            score = random.randint(2, 5)
            votes[agent.name] = {
                'score': score,
                'reason': f"라운드 {round_num} 논의 기반 평가"
            }
        
        # 투표 결과 계산
        result = self.voting_system.calculate_result(votes=votes) if self.voting_system else {}
        result['round'] = round_num
        result['motion'] = f"{topic} - 라운드 {round_num} 제안"
        
        return result
    
    async def run_debate(
        self, 
        topic: str, 
        num_rounds: int = 3,
        selected_agents: List = None
    ) -> Dict:
        """
        토론 실행 (AutoGen 0.7.x 비동기 방식)
        
        Args:
            topic: 토론 주제
            num_rounds: 라운드 수
            selected_agents: 선택된 에이전트 리스트 (없으면 전체)
        
        Returns:
            토론 결과 딕셔너리
        """
        safe_print("\n" + "="*80)
        safe_print(f"[*] Debate Start: {topic}")
        safe_print("="*80 + "\n")
        
        # 참가 에이전트 선택
        if selected_agents is None:
            # 기본: 2명 고객 + 1명 직원
            participants = [
                self.customer_agents.get_agent('iphone_to_galaxy'),
                self.customer_agents.get_agent('tech_enthusiast'),
                self.employee_agents.get_agent('marketer'),
            ]
        else:
            participants = selected_agents
        
        safe_print("[*] Participants:")
        for agent in participants:
            safe_print(f"   - {agent.name}")
        safe_print("")
        
        # RoundRobinGroupChat 생성 (AutoGen 0.7.x) - 충분한 메시지 수 허용
        termination = MaxMessageTermination(max_messages=num_rounds * len(participants) * 2)
        
        group_chat = RoundRobinGroupChat(
            participants=participants,
            termination_condition=termination,
        )
        
        # 토론 시작 메시지
        initial_message = TextMessage(
            content=f"""[토론 주제]
{topic}

[진행 방식]
- {num_rounds}라운드로 진행
- 각자의 페르소나와 실제 데이터를 근거로 의견 제시
- 간단명료하게 3-5문장으로 답변

첫 번째 참가자부터 의견을 말씀해 주세요.""",
            source="facilitator"
        )
        
        # 토론 실행
        safe_print("[*] Debate in progress...\n")
        safe_print("-"*80 + "\n")
        
        try:
            # 비동기 실행 with streaming
            all_messages = []
            
            async for message in group_chat.run_stream(
                task=initial_message,
                cancellation_token=CancellationToken()
            ):
                # 메시지 출력
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    safe_print(f"\n[{message.source}]")
                    safe_print(f"{message.content}\n")
                    safe_print("-"*80)
                    all_messages.append(message)
            
            safe_print("\n" + "-"*80)
            safe_print("\n[OK] Debate completed!")
            
            # 결과 정리
            debate_result = {
                'topic': topic,
                'num_rounds': num_rounds,
                'participants': [agent.name for agent in participants],
                'messages': all_messages,
                'success': True
            }
            
            return debate_result
            
        except Exception as e:
            safe_print(f"\n[ERROR] Debate error: {e}")
            return {
                'topic': topic,
                'success': False,
                'error': str(e)
            }
    
    async def run_full_debate_with_voting(
        self,
        topic: str,
        num_rounds: int = 3,
        selected_agents: List = None
    ) -> Dict:
        """
        투표 포함 전체 토론 실행
        
        Args:
            topic: 토론 주제
            num_rounds: 라운드 수
            selected_agents: 선택된 에이전트 리스트 (없으면 전체)
        
        Returns:
            토론 및 투표 결과
        """
        # 참가 에이전트 선택
        if selected_agents is None:
            # 전체 에이전트 참여
            participants = (
                self.customer_agents.get_all_agents() +
                self.employee_agents.get_all_agents()
            )
        else:
            participants = selected_agents
        
        # 토론 실행
        debate_result = await self.run_debate(
            topic=topic,
            num_rounds=num_rounds,
            selected_agents=participants
        )
        
        # 투표 시스템이 있으면 투표 진행
        if self.voting_system and debate_result['success']:
            safe_print("\n" + "="*80)
            safe_print("[*] Voting Start")
            safe_print("="*80 + "\n")
            
            # 라운드별 투표 (간소화된 버전)
            voting_results = []
            
            for round_num in range(1, num_rounds + 1):
                motion = f"{topic} - 라운드 {round_num} 안건"
                
                # 투표 제안
                round_id = self.voting_system.propose_motion(
                    motion_text=motion,
                    proposer="facilitator"
                )
                
                # 각 에이전트 투표 (임의 점수 - 실제로는 LLM 응답 기반)
                import random
                for agent in participants:
                    score = random.randint(3, 5)  # 간소화된 투표
                    reason = f"{agent.name}의 관점에서 평가"
                    
                    self.voting_system.cast_vote(
                        voter=agent.name,
                        score=score,
                        reason=reason,
                        round_id=round_id
                    )
                
                # 가중치 설정
                weights = {}
                for agent in participants:
                    if "고객" in agent.name or "전환자" in agent.name or "애호가" in agent.name:
                        weights[agent.name] = 0.4 / len(self.customer_agents.get_all_agents())
                    else:
                        weights[agent.name] = 0.2
                
                # 결과 계산
                result = self.voting_system.calculate_result(
                    votes=self.voting_system.voting_history[-1]['votes'],
                    weights=weights,
                    round_id=round_id
                )
                
                voting_results.append(result)
                
                safe_print(f"\nRound {round_num} voting result:")
                safe_print(f"  - Weighted average: {result['weighted_average']:.2f}/5.0")
                passed_status = "PASSED" if result['passed'] else "FAILED"
                safe_print(f"  - Result: {passed_status}\n")
            
            debate_result['voting_results'] = voting_results
        
        return debate_result
    
    def get_debate_topics(self) -> Dict:
        """토론 주제 목록 반환"""
        return self.debate_topics
    
    def save_debate_result(self, result: Dict, filename: str):
        """
        토론 결과 저장
        
        Args:
            result: 토론 결과
            filename: 저장할 파일명
        """
        import json
        from datetime import datetime
        
        # 타임스탬프 추가
        result['timestamp'] = datetime.now().isoformat()
        
        # JSON 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        safe_print(f"\n[OK] Debate result saved: {filename}")


# 테스트
if __name__ == "__main__":
    safe_print("[!] DebateSystem should be run from main.py with other components.")
    safe_print("\nUsage:")
    safe_print("  python main.py")

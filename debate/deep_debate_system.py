#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Debate System - 페이즈별 심층 토론 시스템
실제 회의처럼 페이즈별로 진행되는 토론 시스템
"""

import asyncio
import json
from typing import List, Dict, AsyncGenerator
from datetime import datetime
import openai
from agents.customer_agents_v2 import CustomerAgentsV2
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator

class DeepDebateSystem:
    """페이즈별 심층 토론 시스템"""
    
    def __init__(self, customer_agents, employee_agents, facilitator):
        self.customer_agents = customer_agents
        self.employee_agents = employee_agents
        self.facilitator = facilitator
        
        # 페이즈별 토론 주제 정의
        self.debate_phases = {
            "galaxy_strategy": {
                "title": "갤럭시 Z 시리즈 차기 전략 FGD: 애플 스위처 유치 방안",
                "phases": [
                    {
                        "name": "Phase I: 현상 진단 및 Switcher Pain Point 분석",
                        "description": "현재 상황 분석 및 애플 사용자 전환 장벽 파악",
                        "rounds": 3,
                        "facilitator_summary": True
                    },
                    {
                        "name": "Phase II: 기술/디자인/금융 전략 심화",
                        "description": "구체적인 기술적 해결방안 및 전략 논의",
                        "rounds": 4,
                        "facilitator_summary": True
                    },
                    {
                        "name": "Phase III: 디자인 완성도와 S펜 통합 심화",
                        "description": "디자인 완성도 및 핵심 기능 통합 방안",
                        "rounds": 3,
                        "facilitator_summary": True
                    },
                    {
                        "name": "Phase IV: 스위처 대상 IMC 및 실행 계획",
                        "description": "마케팅 전략 및 실행 계획 수립",
                        "rounds": 3,
                        "facilitator_summary": True
                    },
                    {
                        "name": "Phase V: 의사 결정 우선순위 최종 확정",
                        "description": "최종 우선순위 결정 및 후속 조치 계획",
                        "rounds": 2,
                        "facilitator_summary": True
                    }
                ]
            }
        }
    
    async def run_deep_debate_streaming(
        self, 
        topic_key: str = "galaxy_strategy",
        selected_agents: List[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """페이즈별 심층 토론 실행 (스트리밍)"""
        
        if topic_key not in self.debate_phases:
            yield {"type": "error", "data": {"message": f"Unknown topic: {topic_key}"}}
            return
        
        debate_config = self.debate_phases[topic_key]
        phases = debate_config["phases"]
        
        # 참가자 설정
        participants = []
        if selected_agents:
            for agent_name in selected_agents:
                if agent_name in ["Marketer", "Designer", "Developer"]:
                    participants.append(self.employee_agents.get_agent(agent_name))
                else:
                    participants.append(self.customer_agents.get_agent(agent_name))
        
        # 기본 참가자 (마케터, 디자이너, 개발자)
        if not participants:
            participants = [
                self.employee_agents.get_agent("Marketer"),
                self.employee_agents.get_agent("Designer"), 
                self.employee_agents.get_agent("Developer")
            ]
        
        yield {
            "type": "start",
            "data": {
                "title": debate_config["title"],
                "participants": [agent.name for agent in participants],
                "phases": len(phases)
            }
        }
        
        # 전체 토론 기록
        full_debate_log = []
        phase_summaries = []
        
        # 각 페이즈별 토론 진행
        for phase_idx, phase in enumerate(phases):
            yield {
                "type": "phase_start",
                "data": {
                    "phase_number": phase_idx + 1,
                    "phase_name": phase["name"],
                    "description": phase["description"],
                    "rounds": phase["rounds"]
                }
            }
            
            # 페이즈 내 라운드별 토론
            phase_messages = []
            for round_idx in range(phase["rounds"]):
                yield {
                    "type": "round_start",
                    "data": {
                        "phase_number": phase_idx + 1,
                        "round_number": round_idx + 1,
                        "total_rounds": phase["rounds"]
                    }
                }
                
                # 각 참가자 순차 발언
                for agent_idx, agent in enumerate(participants):
                    try:
                        # 이전 메시지들을 컨텍스트로 활용
                        context_messages = self._build_context_messages(
                            phase_messages, 
                            phase["name"], 
                            round_idx + 1
                        )
                        
                        # 에이전트 응답 생성
                        response = await self._get_agent_response(
                            agent, 
                            context_messages,
                            phase["name"],
                            round_idx + 1
                        )
                        
                        message_data = {
                            "source": agent.name,
                            "content": response,
                            "phase": phase_idx + 1,
                            "round": round_idx + 1,
                            "turn": agent_idx + 1,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        phase_messages.append(message_data)
                        full_debate_log.append(message_data)
                        
                        yield {
                            "type": "message",
                            "data": message_data
                        }
                        
                        # 메시지 간 간격
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        yield {
                            "type": "error",
                            "data": {"message": f"Agent {agent.name} error: {str(e)}"}
                        }
                
                yield {
                    "type": "round_end",
                    "data": {
                        "phase_number": phase_idx + 1,
                        "round_number": round_idx + 1,
                        "messages_count": len(phase_messages)
                    }
                }
            
            # 페이즈 요약 (퍼실리테이터)
            if phase["facilitator_summary"]:
                summary = await self._generate_phase_summary(
                    phase_messages, 
                    phase["name"],
                    phase_idx + 1
                )
                
                phase_summary = {
                    "phase_number": phase_idx + 1,
                    "phase_name": phase["name"],
                    "summary": summary,
                    "key_points": self._extract_key_points(phase_messages),
                    "decisions": self._extract_decisions(phase_messages)
                }
                
                phase_summaries.append(phase_summary)
                
                yield {
                    "type": "phase_summary",
                    "data": phase_summary
                }
            
            yield {
                "type": "phase_end",
                "data": {
                    "phase_number": phase_idx + 1,
                    "phase_name": phase["name"],
                    "messages_count": len(phase_messages)
                }
            }
        
        # 최종 회의록 생성
        final_report = await self._generate_final_report(
            full_debate_log, 
            phase_summaries,
            debate_config["title"]
        )
        
        yield {
            "type": "final_report",
            "data": final_report
        }
        
        yield {
            "type": "complete",
            "data": {
                "total_phases": len(phases),
                "total_messages": len(full_debate_log),
                "participants": [agent.name for agent in participants]
            }
        }
    
    def _build_context_messages(self, previous_messages: List[Dict], phase_name: str, round_num: int) -> List[Dict]:
        """이전 메시지들을 컨텍스트로 구성"""
        context = []
        
        # 최근 5개 메시지만 컨텍스트로 사용
        recent_messages = previous_messages[-5:] if len(previous_messages) > 5 else previous_messages
        
        for msg in recent_messages:
            context.append({
                "role": "user" if msg["source"] == "facilitator" else "assistant",
                "content": f"[{msg['source']}] {msg['content']}"
            })
        
        return context
    
    async def _get_agent_response(self, agent, context_messages: List[Dict], phase_name: str, round_num: int) -> str:
        """에이전트 응답 생성"""
        try:
            # 페이즈별 프롬프트 구성
            phase_prompt = self._get_phase_prompt(phase_name, round_num)
            
            # 컨텍스트와 함께 메시지 구성
            messages = [
                {"role": "system", "content": agent.system_message},
                {"role": "user", "content": phase_prompt}
            ]
            
            # 이전 대화 컨텍스트 추가
            if context_messages:
                messages.append({"role": "user", "content": "이전 토론 내용:"})
                messages.extend(context_messages)
            
            messages.append({
                "role": "user", 
                "content": f"위 내용을 참고하여 {phase_name}에서 당신의 역할에 맞는 의견을 제시해주세요. 구체적이고 실무적인 관점에서 답변해주세요."
            })
            
            # OpenAI API 호출
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _get_phase_prompt(self, phase_name: str, round_num: int) -> str:
        """페이즈별 프롬프트 생성"""
        prompts = {
            "Phase I: 현상 진단 및 Switcher Pain Point 분석": f"""
            현재 갤럭시 Z 시리즈의 애플 사용자 전환 현황을 분석하고 있습니다.
            당신의 전문 분야에서 애플 사용자들이 갤럭시로 전환하지 않는 근본적인 이유를 분석해주세요.
            구체적인 데이터와 실제 사례를 바탕으로 설명해주세요.
            """,
            "Phase II: 기술/디자인/금융 전략 심화": f"""
            애플 스위처 유치를 위한 구체적인 기술적 해결방안을 논의하고 있습니다.
            당신의 전문 분야에서 제시할 수 있는 실질적인 개선 방안을 제시해주세요.
            기술적 타협 없이 프리미엄 경험을 제공할 수 있는 방안을 중심으로 설명해주세요.
            """,
            "Phase III: 디자인 완성도와 S펜 통합 심화": f"""
            디자인 완성도와 핵심 기능 통합에 대해 논의하고 있습니다.
            당신의 관점에서 완벽한 프리미엄 경험을 위한 디자인과 기능적 요구사항을 제시해주세요.
            기술적 제약과 사용자 경험 사이의 균형점을 찾는 방안을 제안해주세요.
            """,
            "Phase IV: 스위처 대상 IMC 및 실행 계획": f"""
            애플 스위처를 대상으로 한 마케팅 전략과 실행 계획을 수립하고 있습니다.
            당신의 전문 분야에서 효과적인 커뮤니케이션 전략을 제시해주세요.
            구체적인 실행 방안과 예상 효과를 포함하여 설명해주세요.
            """,
            "Phase V: 의사 결정 우선순위 최종 확정": f"""
            최종 우선순위 결정과 후속 조치 계획을 수립하고 있습니다.
            지금까지의 논의를 바탕으로 당신의 전문 분야에서 가장 중요한 우선순위를 제시해주세요.
            구체적인 실행 일정과 담당 부서를 명시하여 제안해주세요.
            """
        }
        
        return prompts.get(phase_name, "토론에 참여하여 당신의 전문적인 의견을 제시해주세요.")
    
    async def _generate_phase_summary(self, phase_messages: List[Dict], phase_name: str, phase_num: int) -> str:
        """페이즈 요약 생성"""
        try:
            messages = [
                {"role": "system", "content": "당신은 회의 퍼실리테이터입니다. 토론 내용을 요약하고 핵심 포인트를 정리해주세요."},
                {"role": "user", "content": f"""
                {phase_name}에서 진행된 토론 내용을 요약해주세요.
                
                토론 내용:
                {self._format_messages_for_summary(phase_messages)}
                
                다음 형식으로 요약해주세요:
                1. 주요 논의 사항
                2. 핵심 의견
                3. 합의된 사항
                4. 다음 단계
                """}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"요약 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _format_messages_for_summary(self, messages: List[Dict]) -> str:
        """요약용 메시지 포맷팅"""
        formatted = []
        for msg in messages:
            formatted.append(f"[{msg['source']}] {msg['content']}")
        return "\n".join(formatted)
    
    def _extract_key_points(self, messages: List[Dict]) -> List[str]:
        """핵심 포인트 추출"""
        key_points = []
        for msg in messages:
            # 간단한 키워드 추출 (실제로는 더 정교한 NLP 필요)
            content = msg["content"]
            if len(content) > 50:  # 충분히 긴 메시지만
                key_points.append(f"{msg['source']}: {content[:100]}...")
        return key_points[:5]  # 최대 5개
    
    def _extract_decisions(self, messages: List[Dict]) -> List[str]:
        """결정사항 추출"""
        decisions = []
        for msg in messages:
            content = msg["content"]
            # 결정 관련 키워드가 포함된 메시지 찾기
            if any(keyword in content for keyword in ["결정", "합의", "승인", "확정", "진행"]):
                decisions.append(f"{msg['source']}: {content[:100]}...")
        return decisions[:3]  # 최대 3개
    
    async def _generate_final_report(self, full_log: List[Dict], phase_summaries: List[Dict], title: str) -> Dict:
        """최종 회의록 생성"""
        try:
            messages = [
                {"role": "system", "content": "당신은 회의록 작성 전문가입니다. 토론 결과를 체계적으로 정리해주세요."},
                {"role": "user", "content": f"""
                {title} 회의록을 작성해주세요.
                
                페이즈별 요약:
                {self._format_phase_summaries(phase_summaries)}
                
                다음 형식으로 회의록을 작성해주세요:
                
                ## 최종 의사 결정 및 후속 조치 계획
                
                ### 우선순위별 전략
                1. 1순위: [전략명] - [핵심 액션] - [담당 부서]
                2. 2순위: [전략명] - [핵심 액션] - [담당 부서]  
                3. 3순위: [전략명] - [핵심 액션] - [담당 부서]
                
                ### 추후 논의 사항
                - [주제]: [담당 부서] - [보고 기한]
                
                ### 마케팅 목표 및 KPI
                - [목표]: [측정 지표]
                """}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                "title": title,
                "report": response.choices[0].message.content.strip(),
                "total_phases": len(phase_summaries),
                "total_messages": len(full_log),
                "participants": list(set([msg["source"] for msg in full_log]))
            }
            
        except Exception as e:
            return {
                "title": title,
                "report": f"회의록 생성 중 오류가 발생했습니다: {str(e)}",
                "error": str(e)
            }
    
    def _format_phase_summaries(self, summaries: List[Dict]) -> str:
        """페이즈 요약 포맷팅"""
        formatted = []
        for summary in summaries:
            formatted.append(f"### {summary['phase_name']}\n{summary['summary']}\n")
        return "\n".join(formatted)

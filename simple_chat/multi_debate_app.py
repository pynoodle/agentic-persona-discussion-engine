#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
멀티페르소나 토론 시스템
고객 페르소나 + 임직원 페르소나 + 토론 진행자가 함께하는 토론
"""

import os
import gradio as gr
import openai
from typing import List, Dict, Optional
from datetime import datetime
import json
import random
import time

# 로컬 모듈 import
from simple_rag_manager import SimplePersonaRAGManager
from employee_rag_manager import EmployeePersonaRAGManager
from facilitator import Facilitator

class MultiPersonaDebateSystem:
    def __init__(self, openai_api_key: str):
        """멀티페르소나 토론 시스템 초기화"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # RAG 매니저들 초기화
        self.customer_rag = SimplePersonaRAGManager(openai_api_key)
        self.employee_rag = EmployeePersonaRAGManager(openai_api_key)
        
        # 토론 진행자 초기화
        self.facilitator = Facilitator(openai_api_key)
        
        # 페르소나 정의
        self.customer_personas = {
            "I_to_G": {
                "name": "iPhone to Galaxy Switcher",
                "emoji": "📱➡️📱",
                "description": "아이폰에서 갤럭시로 전환한 사용자",
                "personality": "전환 경험을 바탕으로 한 솔직한 의견, 갤럭시의 장점과 단점을 균형있게 평가"
            },
            "G_to_I": {
                "name": "Galaxy to iPhone Switcher",
                "emoji": "📱➡️🍎", 
                "description": "갤럭시에서 아이폰으로 전환한 사용자",
                "personality": "전환 경험을 바탕으로 한 솔직한 의견, 아이폰의 장점과 단점을 균형있게 평가"
            },
            "I_loyal": {
                "name": "iPhone Loyal User",
                "emoji": "🍎❤️",
                "description": "아이폰 생태계에 충성하는 사용자",
                "personality": "애플 생태계의 장점을 강조하며, 일관된 사용자 경험을 중시"
            },
            "G_loyal": {
                "name": "Galaxy Loyal User", 
                "emoji": "📱❤️",
                "description": "갤럭시 생태계에 충성하는 사용자",
                "personality": "삼성 생태계의 장점을 강조하며, 혁신과 다양성을 중시"
            }
        }
        
        self.employee_personas = {
            "marketer": {
                "name": "최지훈 (마케터)",
                "emoji": "📊",
                "description": "MX사업부 마케팅 총괄 이사",
                "personality": "기술적 우위를 단순하고 임팩트 있는 스토리로 전환, 고객의 선망성 극대화"
            },
            "engineer": {
                "name": "박준호 (엔지니어)",
                "emoji": "⚙️",
                "description": "MX사업부 제품 개발팀 최고 책임자",
                "personality": "폼팩터 경량화 설계, AP 성능 튜닝 및 열 관리 전문가"
            },
            "designer": {
                "name": "이현서 (디자이너)",
                "emoji": "🎨",
                "description": "MX사업부 디자인 전략 총괄",
                "personality": "Simple, Impactful, Emotive의 세 가지 원칙으로 울트라 슬릭 모던 디자인 구현"
            }
        }
        
        # 토론 상태
        self.debate_state = {
            "is_active": False,
            "current_phase": "opening",
            "turn_count": 0,
            "participants": [],
            "topic": "",
            "messages": []
        }
        
        # 시스템 초기화
        self.initialize_system()
    
    def initialize_system(self):
        """시스템 초기화"""
        print("Initializing Multi-Persona Debate System...")
        
        # RAG 매니저들 로드
        customer_loaded = self.customer_rag.load_all_personas()
        employee_loaded = self.employee_rag.load_all_personas()
        
        if customer_loaded and employee_loaded:
            print("All RAG systems loaded successfully!")
        else:
            print("Some RAG systems failed to load!")
    
    def get_persona_response(self, persona_type: str, persona_category: str, 
                           user_message: str, chat_history: List) -> str:
        """특정 페르소나의 응답 생성"""
        
        if persona_type == "customer":
            persona_info = self.customer_personas.get(persona_category, {})
            rag_manager = self.customer_rag
        elif persona_type == "employee":
            persona_info = self.employee_personas.get(persona_category, {})
            rag_manager = self.employee_rag
        else:
            return "죄송합니다. 해당 페르소나를 찾을 수 없습니다."
        
        if not persona_info:
            return "죄송합니다. 해당 페르소나를 찾을 수 없습니다."
        
        # RAG 컨텍스트 검색
        contexts = rag_manager.get_context(persona_category, user_message, k=2)
        
        # 컨텍스트를 프롬프트에 포함
        context_text = ""
        if contexts:
            context_text = "\n".join(contexts)
        
        # 페르소나 프롬프트 생성
        system_prompt = f"""당신은 {persona_info['name']} ({persona_info['emoji']})입니다.

역할: {persona_info['description']}
성격: {persona_info['personality']}

다음 실제 데이터를 참고하여 답변하세요:
{context_text}

토론 참가자로서의 지침:
1. 자신의 전문 분야와 경험을 바탕으로 한 솔직하고 개인적인 의견을 제시하세요
2. 다른 참가자들과 건설적으로 토론하고 의견을 교환하세요
3. 구체적인 근거와 예시를 들어 설명하세요
4. 너무 딱딱하지 않고 자연스러운 대화체로 답변하세요
5. 한국어로 답변하세요
6. 3-5문장 정도로 간결하게 답변하세요"""

        # 채팅 히스토리 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 채팅 히스토리 추가 (최대 8개)
        for msg in chat_history[-8:]:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
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
            print(f"Error generating response: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    def start_debate(self, topic: str, selected_personas: List[str]) -> tuple:
        """토론 시작"""
        if not topic.strip():
            return [], "토론 주제를 입력해주세요."
        
        if len(selected_personas) < 2:
            return [], "최소 2명 이상의 참가자를 선택해주세요."
        
        # 토론 상태 초기화
        self.debate_state = {
            "is_active": True,
            "current_phase": "opening",
            "turn_count": 0,
            "participants": selected_personas,
            "topic": topic,
            "messages": []
        }
        
        # 토론 시작 메시지
        initial_message = f"🎯 토론 주제: {topic}\n\n참가자: {', '.join(selected_personas)}\n\n토론을 시작하겠습니다!"
        
        # 진행자 시작 메시지
        facilitator_response = self.facilitator.get_facilitator_response(
            phase="opening",
            topic=topic,
            participants=selected_personas,
            recent_messages=[],
            turn_count=1
        )
        
        # 채팅 히스토리 초기화
        chat_history = [
            {"role": "user", "content": initial_message},
            {"role": "assistant", "content": f"🎤 {self.facilitator.name}: {facilitator_response}"}
        ]
        
        self.debate_state["messages"] = chat_history.copy()
        self.debate_state["turn_count"] = 1
        
        return chat_history, f"토론이 시작되었습니다! 주제: {topic}"
    
    def continue_debate(self, user_message: str, chat_history: List) -> tuple:
        """토론 계속 진행"""
        if not self.debate_state["is_active"]:
            return chat_history, "토론이 진행 중이 아닙니다. 새 토론을 시작해주세요."
        
        if not user_message.strip():
            return chat_history, ""
        
        # 현재 턴의 발언자 결정
        current_speaker = self.get_current_speaker()
        if not current_speaker:
            return chat_history, "발언자를 결정할 수 없습니다."
        
        # 발언자 정보 파싱
        speaker_type, speaker_category = self.parse_speaker(current_speaker)
        
        # 페르소나 응답 생성
        persona_response = self.get_persona_response(
            speaker_type, speaker_category, user_message, chat_history
        )
        
        # 응답 메시지 생성
        if speaker_type == "employee":
            persona_info = self.employee_personas.get(speaker_category, {})
        else:
            persona_info = self.customer_personas.get(speaker_category, {})
        
        response_message = f"{persona_info.get('emoji', '👤')} {persona_info.get('name', current_speaker)}: {persona_response}"
        
        # 채팅 히스토리 업데이트
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": response_message})
        
        # 토론 상태 업데이트
        self.debate_state["messages"] = chat_history.copy()
        self.debate_state["turn_count"] += 1
        
        # 다음 단계 결정
        next_phase = self.facilitator.determine_next_phase(
            self.debate_state["turn_count"],
            has_conflict=self.detect_conflict(chat_history)
        )
        
        # 진행자 응답 (필요시)
        if self.should_facilitator_speak():
            facilitator_response = self.facilitator.get_facilitator_response(
                phase=next_phase,
                topic=self.debate_state["topic"],
                participants=self.debate_state["participants"],
                recent_messages=chat_history[-4:],
                turn_count=self.debate_state["turn_count"]
            )
            
            facilitator_message = f"🎤 {self.facilitator.name}: {facilitator_response}"
            chat_history.append({"role": "assistant", "content": facilitator_message})
            self.debate_state["messages"] = chat_history.copy()
        
        self.debate_state["current_phase"] = next_phase
        
        return chat_history, ""
    
    def get_current_speaker(self) -> str:
        """현재 발언자 결정"""
        participants = self.debate_state["participants"]
        turn_count = self.debate_state["turn_count"]
        
        # 순환 방식으로 발언자 결정
        speaker_index = (turn_count - 1) % len(participants)
        return participants[speaker_index]
    
    def parse_speaker(self, speaker: str) -> tuple:
        """발언자 정보 파싱"""
        # 고객 페르소나 확인
        for category, info in self.customer_personas.items():
            if info["name"] in speaker or category in speaker:
                return "customer", category
        
        # 임직원 페르소나 확인
        for category, info in self.employee_personas.items():
            if info["name"] in speaker or category in speaker:
                return "employee", category
        
        # 기본값
        return "customer", "G_loyal"
    
    def detect_conflict(self, chat_history: List) -> bool:
        """의견 충돌 감지"""
        # 간단한 충돌 감지 로직
        recent_messages = chat_history[-6:]
        conflict_keywords = ["하지만", "그런데", "반대", "다르게", "아니", "틀렸", "문제"]
        
        for msg in recent_messages:
            if msg.get("role") == "assistant":
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in conflict_keywords):
                    return True
        
        return False
    
    def should_facilitator_speak(self) -> bool:
        """진행자가 발언해야 하는지 결정"""
        turn_count = self.debate_state["turn_count"]
        participants_count = len(self.debate_state["participants"])
        
        # 참가자들이 한 바퀴 돌 때마다 진행자 발언
        return turn_count % (participants_count + 1) == 0
    
    def end_debate(self) -> str:
        """토론 종료 및 요약"""
        if not self.debate_state["is_active"]:
            return "토론이 진행 중이 아닙니다."
        
        # 토론 요약 생성
        summary = self.facilitator.summarize_discussion(self.debate_state["messages"])
        
        # 토론 상태 초기화
        self.debate_state["is_active"] = False
        
        return summary

def create_gradio_interface():
    """Gradio 인터페이스 생성"""
    
    # 환경 변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return gr.Interface(
            fn=lambda x: "OpenAI API key not found!",
            inputs="text",
            outputs="text",
            title="Multi-Persona Debate System - Error"
        )
    
    # 토론 시스템 초기화
    debate_system = MultiPersonaDebateSystem(api_key)
    
    # 페르소나 선택 옵션
    customer_options = [
        ("📱➡️📱 iPhone to Galaxy Switcher", "I_to_G"),
        ("📱➡️🍎 Galaxy to iPhone Switcher", "G_to_I"), 
        ("🍎❤️ iPhone Loyal User", "I_loyal"),
        ("📱❤️ Galaxy Loyal User", "G_loyal")
    ]
    
    employee_options = [
        ("📊 최지훈 (마케터)", "marketer"),
        ("⚙️ 박준호 (엔지니어)", "engineer"),
        ("🎨 이현서 (디자이너)", "designer")
    ]
    
    with gr.Blocks(title="Multi-Persona Debate System") as interface:
        gr.Markdown("""
        # Multi-Persona Debate System
        
        **고객 페르소나 + 임직원 페르소나 + 토론 진행자가 함께하는 토론 시스템**
        
        ### 고객 페르소나
        - 📱➡️📱 **iPhone to Galaxy Switcher**: 아이폰에서 갤럭시로 전환한 사용자
        - 📱➡️🍎 **Galaxy to iPhone Switcher**: 갤럭시에서 아이폰으로 전환한 사용자  
        - 🍎❤️ **iPhone Loyal User**: 아이폰 생태계에 충성하는 사용자
        - 📱❤️ **Galaxy Loyal User**: 갤럭시 생태계에 충성하는 사용자
        
        ### 임직원 페르소나
        - 📊 **최지훈 (마케터)**: MX사업부 마케팅 총괄 이사
        - ⚙️ **박준호 (엔지니어)**: MX사업부 제품 개발팀 최고 책임자
        - 🎨 **이현서 (디자이너)**: MX사업부 디자인 전략 총괄
        
        ### 토론 진행자
        - 🎤 **김진수 (토론 진행자)**: 삼성전자 MX사업부 전략 기획팀장
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 토론 설정")
                
                topic_input = gr.Textbox(
                    placeholder="토론 주제를 입력하세요... (예: 갤럭시 Z 폴드 7의 S펜 제거 결정)",
                    label="토론 주제",
                    lines=2
                )
                
                gr.Markdown("### 고객 페르소나 선택")
                customer_checkboxes = gr.CheckboxGroup(
                    choices=customer_options,
                    value=["G_loyal"],
                    label="고객 페르소나",
                    info="토론에 참여할 고객 페르소나를 선택하세요"
                )
                
                gr.Markdown("### 임직원 페르소나 선택")
                employee_checkboxes = gr.CheckboxGroup(
                    choices=employee_options,
                    value=["marketer", "engineer", "designer"],
                    label="임직원 페르소나",
                    info="토론에 참여할 임직원 페르소나를 선택하세요"
                )
                
                with gr.Row():
                    start_debate_btn = gr.Button("토론 시작", variant="primary")
                    end_debate_btn = gr.Button("토론 종료", variant="secondary")
            
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="토론 진행 상황",
                    height=600,
                    show_label=True,
                    type="messages"
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="메시지를 입력하세요...",
                        label="메시지",
                        lines=2
                    )
                    send_btn = gr.Button("전송", variant="primary")
                
                status_text = gr.Textbox(
                    label="토론 상태",
                    value="토론을 시작하려면 주제와 참가자를 선택하고 '토론 시작' 버튼을 클릭하세요.",
                    interactive=False
                )
        
        # 이벤트 핸들러
        def start_debate_function(topic, customer_personas, employee_personas):
            all_participants = customer_personas + employee_personas
            return debate_system.start_debate(topic, all_participants)
        
        def continue_debate_function(user_message, chat_history):
            return debate_system.continue_debate(user_message, chat_history)
        
        def end_debate_function():
            summary = debate_system.end_debate()
            return summary
        
        start_debate_btn.click(
            fn=start_debate_function,
            inputs=[topic_input, customer_checkboxes, employee_checkboxes],
            outputs=[chatbot, status_text]
        )
        
        send_btn.click(
            fn=continue_debate_function,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            fn=continue_debate_function,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        end_debate_btn.click(
            fn=end_debate_function,
            outputs=[status_text]
        )
    
    return interface

def main():
    """메인 실행 함수"""
    print("Starting Multi-Persona Debate System...")
    
    # Gradio 인터페이스 생성 및 실행
    interface = create_gradio_interface()
    
    if interface:
        interface.launch(
            server_name="0.0.0.0",
            server_port=8001,
            share=False,
            debug=True
        )
    else:
        print("Failed to create interface!")

if __name__ == "__main__":
    main()


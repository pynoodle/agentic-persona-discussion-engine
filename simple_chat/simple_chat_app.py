#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순화된 페르소나 채팅 시스템
4개 페르소나 (I->G, G->I, I고수, G고수)와 대화
"""

import os
import gradio as gr
import openai
from typing import List, Dict, Optional
from datetime import datetime
import json
from simple_rag_manager import SimplePersonaRAGManager

class SimplePersonaChatSystem:
    def __init__(self, openai_api_key: str):
        """단순화된 페르소나 채팅 시스템 초기화"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # RAG 매니저 초기화
        self.rag_manager = SimplePersonaRAGManager(openai_api_key)
        
        # 페르소나 설정
        self.personas = {
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
        
        # 채팅 히스토리
        self.chat_history = []
        
        # 시스템 초기화
        self.initialize_system()
    
    def initialize_system(self):
        """시스템 초기화"""
        print("Initializing Simple Persona Chat System...")
        
        # RAG 매니저 로드
        if self.rag_manager.load_all_personas():
            print("All persona vector stores loaded successfully!")
        else:
            print("Failed to load persona vector stores!")
    
    def get_persona_response(self, persona_category: str, user_message: str, chat_history: List) -> str:
        """특정 페르소나의 응답 생성"""
        if persona_category not in self.personas:
            return "죄송합니다. 해당 페르소나를 찾을 수 없습니다."
        
        persona_info = self.personas[persona_category]
        
        # RAG 컨텍스트 검색
        contexts = self.rag_manager.get_context(persona_category, user_message, k=2)
        
        # 컨텍스트를 프롬프트에 포함
        context_text = ""
        if contexts:
            context_text = "\n".join(contexts)
        
        # 페르소나 프롬프트 생성
        system_prompt = f"""당신은 {persona_info['name']} ({persona_info['emoji']})입니다.

페르소나 특성:
- {persona_info['description']}
- 성격: {persona_info['personality']}

다음 실제 사용자 리뷰 데이터를 참고하여 답변하세요:
{context_text}

지침:
1. 실제 사용자 경험을 바탕으로 한 솔직하고 개인적인 답변을 제공하세요
2. 너무 딱딱하지 않고 자연스러운 대화체로 답변하세요
3. 구체적인 경험과 감정을 포함하여 답변하세요
4. 한국어로 답변하세요
5. 3-5문장 정도로 간결하게 답변하세요"""

        # 채팅 히스토리 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 채팅 히스토리 추가 (최대 6개)
        for msg in chat_history[-6:]:
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
    
    def chat_with_persona(self, persona_category: str, user_message: str, chat_history: List) -> tuple:
        """페르소나와 채팅"""
        if not user_message.strip():
            return chat_history, ""
        
        # 페르소나 응답 생성
        persona_response = self.get_persona_response(persona_category, user_message, chat_history)
        
        # 채팅 히스토리 업데이트
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": persona_response})
        
        return chat_history, ""

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
            title="Simple Persona Chat System - Error"
        )
    
    # 채팅 시스템 초기화
    chat_system = SimplePersonaChatSystem(api_key)
    
    # 페르소나 선택 옵션
    persona_options = [
        ("📱➡️📱 iPhone to Galaxy Switcher", "I_to_G"),
        ("📱➡️🍎 Galaxy to iPhone Switcher", "G_to_I"), 
        ("🍎❤️ iPhone Loyal User", "I_loyal"),
        ("📱❤️ Galaxy Loyal User", "G_loyal")
    ]
    
    with gr.Blocks(title="Simple Persona Chat System") as interface:
        gr.Markdown("""
        # Simple Persona Chat System
        
        **4개의 단순화된 페르소나와 대화해보세요!**
        
        - 📱➡️📱 **iPhone to Galaxy Switcher**: 아이폰에서 갤럭시로 전환한 사용자
        - 📱➡️🍎 **Galaxy to iPhone Switcher**: 갤럭시에서 아이폰으로 전환한 사용자  
        - 🍎❤️ **iPhone Loyal User**: 아이폰 생태계에 충성하는 사용자
        - 📱❤️ **Galaxy Loyal User**: 갤럭시 생태계에 충성하는 사용자
        
        각 페르소나는 실제 사용자 리뷰 데이터를 바탕으로 한 RAG 시스템을 사용합니다.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                persona_dropdown = gr.Dropdown(
                    choices=persona_options,
                    value="I_to_G",
                    label="페르소나 선택",
                    info="대화하고 싶은 페르소나를 선택하세요"
                )
                
                gr.Markdown("""
                ### 사용법
                1. 위에서 페르소나를 선택하세요
                2. 아래 채팅창에 메시지를 입력하세요
                3. 선택한 페르소나의 관점에서 답변을 받으세요
                """)
            
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="채팅",
                    height=500,
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
        
        # 이벤트 핸들러
        def chat_function(persona_category, user_message, chat_history):
            return chat_system.chat_with_persona(persona_category, user_message, chat_history)
        
        send_btn.click(
            fn=chat_function,
            inputs=[persona_dropdown, msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            fn=chat_function,
            inputs=[persona_dropdown, msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
    
    return interface

def main():
    """메인 실행 함수"""
    print("Starting Simple Persona Chat System...")
    
    # Gradio 인터페이스 생성 및 실행
    interface = create_gradio_interface()
    
    if interface:
        interface.launch(
            server_name="0.0.0.0",
            server_port=8000,
            share=False,
            debug=True
        )
    else:
        print("Failed to create interface!")

if __name__ == "__main__":
    main()

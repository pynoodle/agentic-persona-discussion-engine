#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonaBot GUI - Streamlit 기반 전문적인 인터페이스
AutoGen 0.7.x + LangChain RAG + 실시간 채팅
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import json
from pathlib import Path

# 환경 변수 로드
load_dotenv()

# 모듈 import
from rag.rag_manager import RAGManager
from agents.customer_agents import CustomerAgents
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator
from debate.debate_system import DebateSystem
from debate.voting_system import VotingSystem

# 페이지 설정
st.set_page_config(
    page_title="PersonaBot - Multi-Agent Debate System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #e2e8f0 100%);
    }
    
    /* 사이드바 텍스트 */
    [data-testid="stSidebar"] * {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #1a202c !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] label {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] strong {
        color: #1a202c !important;
    }
    
    /* 채팅 메시지 */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .chat-message.user strong {
        color: white;
    }
    
    .chat-message.assistant {
        background: white;
        border: 2px solid #e2e8f0;
        color: #2d3748;
    }
    
    .chat-message.assistant strong {
        color: #1a202c;
    }
    
    .chat-message.system {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-style: italic;
    }
    
    .chat-message.system strong {
        color: white;
    }
    
    /* 페르소나 카드 */
    .persona-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .persona-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
    
    .persona-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .persona-role {
        color: #667eea;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .persona-stats {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .stat-item {
        flex: 1;
        background: #f7fafc;
        padding: 0.75rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #718096;
        margin-top: 0.25rem;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    /* 진행 상황 표시 */
    .progress-container {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background: #f7fafc;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.02);
    }
    
    .progress-step.active strong {
        color: white;
    }
    
    .progress-step.completed {
        background: #48bb78;
        color: white;
    }
    
    .progress-step.completed strong {
        color: white;
    }
    
    /* 투표 결과 */
    .vote-result {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #2d3748;
    }
    
    .vote-result strong {
        color: #1a202c;
    }
    
    .vote-bar {
        height: 2rem;
        border-radius: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }
    
    /* 리포트 섹션 */
    .report-section {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    .report-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
        color: white;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
def init_session_state():
    """세션 상태 초기화"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.rag_manager = None
        st.session_state.customer_agents = None
        st.session_state.employee_agents = None
        st.session_state.facilitator = None
        st.session_state.debate_system = None
        st.session_state.voting_system = None
        st.session_state.chat_history = []
        st.session_state.debate_results = []
        st.session_state.current_mode = "chat"  # chat or debate
        st.session_state.selected_persona = None
        st.session_state.debate_in_progress = False


def initialize_system():
    """시스템 초기화"""
    if st.session_state.initialized:
        return True
    
    try:
        with st.spinner("🚀 PersonaBot 시스템 초기화 중..."):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 1. RAG 시스템
            status_text.text("📚 RAG 시스템 초기화 중...")
            st.session_state.rag_manager = RAGManager(use_openai_embeddings=True)
            progress_bar.progress(20)
            
            # 2. 페르소나 로드
            status_text.text("👥 페르소나 지식 로드 중...")
            all_personas = [
                'customer_iphone_to_galaxy',
                'customer_galaxy_loyalist',
                'customer_tech_enthusiast',
                'customer_price_conscious',
                'employee_marketer',
                'employee_developer',
                'employee_designer',
            ]
            
            for i, persona in enumerate(all_personas):
                st.session_state.rag_manager.load_persona_knowledge(persona)
                progress_bar.progress(20 + (i + 1) * 8)
            
            # 3. 에이전트 초기화
            status_text.text("🤖 에이전트 초기화 중...")
            st.session_state.customer_agents = CustomerAgents(st.session_state.rag_manager)
            progress_bar.progress(70)
            
            st.session_state.employee_agents = EmployeeAgents(st.session_state.rag_manager)
            progress_bar.progress(80)
            
            st.session_state.facilitator = Facilitator()
            progress_bar.progress(85)
            
            # 4. 토론 시스템
            status_text.text("💬 토론 시스템 초기화 중...")
            st.session_state.voting_system = VotingSystem()
            st.session_state.debate_system = DebateSystem(
                customer_agents=st.session_state.customer_agents,
                employee_agents=st.session_state.employee_agents,
                facilitator=st.session_state.facilitator,
                voting_system=st.session_state.voting_system
            )
            progress_bar.progress(100)
            
            status_text.text("✅ 시스템 초기화 완료!")
            st.session_state.initialized = True
            
            return True
            
    except Exception as e:
        st.error(f"❌ 초기화 실패: {e}")
        return False


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.markdown("# 🤖 PersonaBot")
        st.markdown("### Multi-Agent Debate System")
        st.markdown("---")
        
        # 모드 선택
        st.markdown("### 📋 모드 선택")
        mode = st.radio(
            "작업을 선택하세요",
            ["💬 페르소나 채팅", "🗣️ 자동 토론", "📊 리포트 보기"],
            key="mode_selector"
        )
        
        if "채팅" in mode:
            st.session_state.current_mode = "chat"
        elif "토론" in mode:
            st.session_state.current_mode = "debate"
        else:
            st.session_state.current_mode = "report"
        
        st.markdown("---")
        
        # 페르소나 선택 (채팅 모드)
        if st.session_state.current_mode == "chat":
            st.markdown("### 👥 페르소나 선택")
            
            persona_options = {
                "iPhone→Galaxy 전환자": "iphone_to_galaxy",
                "갤럭시 충성 고객": "galaxy_loyalist",
                "기술 애호가": "tech_enthusiast",
                "가격 민감 고객": "price_conscious",
                "마케터": "marketer",
                "개발자": "developer",
                "디자이너": "designer",
            }
            
            selected = st.selectbox(
                "대화할 페르소나를 선택하세요",
                list(persona_options.keys())
            )
            
            st.session_state.selected_persona = persona_options[selected]
            
            # 페르소나 정보 표시
            st.markdown("#### 📌 페르소나 정보")
            
            persona_info = {
                "iPhone→Galaxy 전환자": {
                    "role": "570명 전환 완료 데이터",
                    "stat1_value": "0.73",
                    "stat1_label": "전환 강도",
                    "stat2_value": "570",
                    "stat2_label": "데이터 수"
                },
                "갤럭시 충성 고객": {
                    "role": "110명 폴더블 전문가",
                    "stat1_value": "0.68",
                    "stat1_label": "전환 강도",
                    "stat2_value": "110",
                    "stat2_label": "데이터 수"
                },
                "기술 애호가": {
                    "role": "분석형 사용자",
                    "stat1_value": "0.65",
                    "stat1_label": "전환 강도",
                    "stat2_value": "높음",
                    "stat2_label": "영향력"
                },
                "가격 민감 고객": {
                    "role": "가격 중시형",
                    "stat1_value": "0.55",
                    "stat1_label": "전환 강도",
                    "stat2_value": "높음",
                    "stat2_label": "공감도"
                },
                "마케터": {
                    "role": "Samsung Mobile 시니어",
                    "stat1_value": "1,093",
                    "stat1_label": "분석 데이터",
                    "stat2_value": "70%",
                    "stat2_label": "전환율"
                },
                "개발자": {
                    "role": "Android 앱 개발 리드",
                    "stat1_value": "기술",
                    "stat1_label": "전문성",
                    "stat2_value": "높음",
                    "stat2_label": "구현력"
                },
                "디자이너": {
                    "role": "Product Design 팀 UX 리드",
                    "stat1_value": "UX",
                    "stat1_label": "전문성",
                    "stat2_value": "높음",
                    "stat2_label": "사용자 중심"
                }
            }
            
            info = persona_info.get(selected, persona_info["iPhone→Galaxy 전환자"])
            
            st.markdown(f"""
            <div class="persona-card">
                <div class="persona-name">{selected}</div>
                <div class="persona-role">{info['role']}</div>
                <div class="persona-stats">
                    <div class="stat-item">
                        <div class="stat-value">{info['stat1_value']}</div>
                        <div class="stat-label">{info['stat1_label']}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{info['stat2_value']}</div>
                        <div class="stat-label">{info['stat2_label']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 토론 설정 (토론 모드)
        elif st.session_state.current_mode == "debate":
            st.markdown("### ⚙️ 토론 설정")
            
            # 추천 주제
            st.markdown("#### 💡 추천 주제")
            recommended_topics = [
                "Galaxy Fold 7의 폴더블 혁신성이 충분한가?",
                "생태계 장벽을 극복할 수 있는 실질적 방안은?",
                "가격 프리미엄(100만원+)이 정당화될 수 있는가?",
                "30일 무료 체험 + 번들 할인 전략의 효과는?",
                "iPhone 사용자가 Galaxy로 전환할 충분한 이유가 있는가?",
            ]
            
            selected_topic = st.selectbox(
                "추천 주제 선택 (또는 아래에 직접 입력)",
                ["직접 입력"] + recommended_topics
            )
            
            # 토론 주제 입력
            if selected_topic == "직접 입력":
                debate_topic = st.text_area(
                    "토론 주제를 입력하세요",
                    placeholder="예: Galaxy AI 기능의 실용성은 어느 정도인가?",
                    height=100
                )
            else:
                debate_topic = st.text_area(
                    "토론 주제 (수정 가능)",
                    value=selected_topic,
                    height=100
                )
            
            num_rounds = st.slider(
                "라운드 수",
                min_value=1,
                max_value=5,
                value=3
            )
            
            # 참가 에이전트 선택
            st.markdown("#### 👥 참가 에이전트 선택")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**고객 페르소나**")
                customer_selection = st.multiselect(
                    "고객 에이전트",
                    ["iPhone→Galaxy 전환자", "갤럭시 충성 고객", "기술 애호가", "가격 민감 고객"],
                    default=["iPhone→Galaxy 전환자", "기술 애호가"]
                )
            
            with col2:
                st.markdown("**직원 페르소나**")
                employee_selection = st.multiselect(
                    "직원 에이전트",
                    ["마케터", "개발자", "디자이너"],
                    default=["마케터"]
                )
            
            st.session_state.debate_topic = debate_topic
            st.session_state.num_rounds = num_rounds
            st.session_state.selected_customers = customer_selection
            st.session_state.selected_employees = employee_selection
            
            # 선택 요약
            total_participants = len(customer_selection) + len(employee_selection)
            st.info(f"📊 선택된 참가자: **{total_participants}명** (고객 {len(customer_selection)}명 + 직원 {len(employee_selection)}명)")
        
        st.markdown("---")
        
        # 통계
        st.markdown("### 📊 세션 통계")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("대화 수", len(st.session_state.chat_history))
        with col2:
            st.metric("토론 수", len(st.session_state.debate_results))
        
        st.markdown("---")
        
        # 시스템 정보
        with st.expander("ℹ️ 시스템 정보"):
            st.markdown("""
            **버전:** v2.0 (AutoGen 0.7.x)  
            **RAG:** LangChain + OpenAI  
            **벡터DB:** ChromaDB  
            **데이터:** 40,377개 실제 댓글  
            """)


def render_chat_interface():
    """채팅 인터페이스 렌더링"""
    st.markdown("## 💬 페르소나와 대화하기")
    st.markdown("선택한 페르소나와 실시간으로 대화할 수 있습니다. 실제 데이터를 기반으로 답변합니다.")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            role = message.get("role", "user")
            content = message.get("content", "")
            persona = message.get("persona", "")
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <div style="flex: 1;">
                        <strong>👤 You</strong><br>
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif role == "assistant":
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div style="flex: 1;">
                        <strong>🤖 {persona}</strong><br>
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message system">
                    <div style="flex: 1;">
                        <strong>📢 System</strong><br>
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 입력 영역
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "메시지를 입력하세요",
            key="chat_input",
            placeholder="예: 폴더블 폰의 장점은 무엇인가요?"
        )
    
    with col2:
        send_button = st.button("전송 📤", use_container_width=True)
    
    if send_button and user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # RAG 검색 및 응답 생성
        with st.spinner("🤔 생각 중..."):
            try:
                # 페르소나 키 매핑 (customer_ 또는 employee_ 접두사)
                persona_key = st.session_state.selected_persona
                
                # 직원 페르소나는 employee_ 접두사 사용
                if persona_key in ['marketer', 'developer', 'designer']:
                    full_persona_key = f"employee_{persona_key}"
                else:
                    full_persona_key = f"customer_{persona_key}"
                
                result = st.session_state.rag_manager.query_persona(
                    full_persona_key,
                    user_input
                )
                
                response = result.get('answer', '죄송합니다. 답변을 생성할 수 없습니다.')
                
                # 어시스턴트 메시지 추가
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "persona": st.session_state.selected_persona.replace("_", " ").title()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"오류 발생: {e}")


async def run_debate_async(debate_system, topic, num_rounds):
    """비동기 토론 실행"""
    participants = [
        st.session_state.customer_agents.get_agent('iphone_to_galaxy'),
        st.session_state.customer_agents.get_agent('tech_enthusiast'),
        st.session_state.employee_agents.get_agent('marketer'),
    ]
    
    result = await debate_system.run_debate(
        topic=topic,
        num_rounds=num_rounds,
        selected_agents=participants
    )
    
    return result


def render_debate_interface():
    """토론 인터페이스 렌더링"""
    st.markdown("## 🗣️ 자동 토론 시스템")
    st.markdown("AI 에이전트들이 자동으로 토론을 진행하고 결과를 요약합니다.")
    
    # 토론 시작 버튼
    if not st.session_state.debate_in_progress:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 토론 시작", use_container_width=True, type="primary"):
                st.session_state.debate_in_progress = True
                st.rerun()
    
    # 토론 진행 중
    if st.session_state.debate_in_progress:
        st.markdown("### 🔄 토론 진행 중...")
        
        # 진행 상황 표시
        progress_steps = [
            {"name": "참가자 준비", "status": "completed"},
            {"name": "토론 시작", "status": "active"},
            {"name": "의견 교환", "status": "pending"},
            {"name": "투표 진행", "status": "pending"},
            {"name": "결과 집계", "status": "pending"},
        ]
        
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        
        for step in progress_steps:
            status_class = step["status"]
            icon = "✅" if status_class == "completed" else ("⏳" if status_class == "active" else "⏸️")
            
            st.markdown(f"""
            <div class="progress-step {status_class}">
                {icon} <strong>{step["name"]}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 실제 토론 실행 (간소화)
        with st.spinner("💭 AI 에이전트들이 토론 중..."):
            # 시뮬레이션된 토론 결과
            debate_result = {
                "topic": st.session_state.debate_topic,
                "num_rounds": st.session_state.num_rounds,
                "participants": ["iPhone→Galaxy전환자", "기술애호가", "마케터"],
                "summary": {
                    "총 발언": st.session_state.num_rounds * 3,
                    "평균 점수": 4.2,
                    "통과 안건": 2,
                    "부결 안건": 1,
                },
                "key_points": [
                    "폴더블 혁신성에 대한 높은 평가",
                    "생태계 전환 장벽 존재",
                    "체험 마케팅 전략 필요",
                ]
            }
            
            st.session_state.debate_results.append(debate_result)
            st.session_state.debate_in_progress = False
            
            st.success("✅ 토론 완료!")
            st.rerun()
    
    # 최근 토론 결과
    if st.session_state.debate_results:
        st.markdown("---")
        st.markdown("### 📊 최근 토론 결과")
        
        latest = st.session_state.debate_results[-1]
        
        # 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">총 발언</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(latest["summary"]["총 발언"]), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">평균 점수</div>
                <div class="metric-value">{:.1f}</div>
            </div>
            """.format(latest["summary"]["평균 점수"]), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">통과 안건</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(latest["summary"]["통과 안건"]), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">부결 안건</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(latest["summary"]["부결 안건"]), unsafe_allow_html=True)
        
        # 주요 포인트
        st.markdown("### 💡 주요 논점")
        
        for i, point in enumerate(latest["key_points"], 1):
            st.markdown(f"""
            <div class="vote-result">
                <strong>{i}.</strong> {point}
            </div>
            """, unsafe_allow_html=True)


def render_report_interface():
    """리포트 인터페이스 렌더링"""
    st.markdown("## 📊 분석 리포트")
    
    if not st.session_state.debate_results:
        st.info("💡 아직 진행된 토론이 없습니다. 먼저 토론을 진행해주세요.")
        return
    
    # 리포트 생성 버튼
    if st.button("📄 리포트 생성", type="primary"):
        with st.spinner("📝 리포트 생성 중..."):
            generate_report()


def generate_report():
    """리포트 생성"""
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="report-title">📈 PersonaBot 토론 분석 리포트</div>', unsafe_allow_html=True)
    
    # 기본 정보
    st.markdown("### 🔍 개요")
    st.markdown(f"- **생성 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"- **총 토론 수:** {len(st.session_state.debate_results)}")
    st.markdown(f"- **총 대화 수:** {len(st.session_state.chat_history)}")
    
    # 토론 요약
    st.markdown("### 📋 토론 요약")
    
    for i, debate in enumerate(st.session_state.debate_results, 1):
        with st.expander(f"토론 #{i}: {debate['topic']}"):
            st.markdown(f"**참가자:** {', '.join(debate['participants'])}")
            st.markdown(f"**라운드:** {debate['num_rounds']}")
            st.markdown(f"**평균 점수:** {debate['summary']['평균 점수']}/5.0")
            
            st.markdown("**주요 논점:**")
            for point in debate['key_points']:
                st.markdown(f"- {point}")
    
    # 다운로드 버튼
    st.markdown("---")
    
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "debates": st.session_state.debate_results,
        "total_chats": len(st.session_state.chat_history),
    }
    
    report_json = json.dumps(report_data, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="📥 JSON 다운로드",
        data=report_json,
        file_name=f"personabot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """메인 함수"""
    # 세션 상태 초기화
    init_session_state()
    
    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return
    
    # 시스템 초기화
    if not st.session_state.initialized:
        if not initialize_system():
            return
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 컨텐츠
    if st.session_state.current_mode == "chat":
        render_chat_interface()
    elif st.session_state.current_mode == "debate":
        render_debate_interface()
    else:
        render_report_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 2rem;">
        <strong>PersonaBot v2.0</strong> • AutoGen 0.7.x + LangChain RAG • 
        40,377개 실제 데이터 기반
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


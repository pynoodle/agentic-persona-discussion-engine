#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Multi-Agent Debate System GUI
Real-time debate visualization with Streamlit
"""

import streamlit as st
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

from rag.rag_manager import RAGManager
from agents.customer_agents_v2 import CustomerAgentsV2
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator
from debate.debate_system import DebateSystem

# Page config
st.set_page_config(
    page_title="🎭 멀티 에이전트 토론",
    page_icon="🎭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.big-title {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
}
.persona-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 1rem;
    margin: 0.2rem;
    font-size: 0.9rem;
}
.galaxy-badge { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.iphone-badge { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.employee-badge { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }

.message-card {
    padding: 1.5rem;
    border-radius: 1rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.galaxy-msg { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }
.iphone-msg { background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%); }
.employee-msg { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.debate_results = []

def init_system():
    """Initialize system"""
    if not os.getenv("OPENAI_API_KEY"):
        return False
    
    try:
        st.session_state.rag = RAGManager()
        st.session_state.rag.load_all_personas()
        st.session_state.customer_agents = CustomerAgentsV2(st.session_state.rag)
        st.session_state.employee_agents = EmployeeAgents(st.session_state.rag)
        st.session_state.facilitator = Facilitator()
        st.session_state.debate_system = DebateSystem(
            st.session_state.customer_agents,
            st.session_state.employee_agents,
            st.session_state.facilitator
        )
        st.session_state.initialized = True
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Main UI
st.markdown('<div class="big-title">🎭 멀티 에이전트 토론 시스템</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>실제 데이터 기반 40,377개 댓글 분석 페르소나</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=PersonaBot", use_container_width=True)
    
    st.markdown("## ⚙️ 시스템")
    
    if not st.session_state.initialized:
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        if st.button("🚀 시스템 초기화", type="primary", use_container_width=True):
            with st.spinner("초기화 중..."):
                if init_system():
                    st.success("✅ 완료!")
                    st.rerun()
    else:
        st.success("✅ 시스템 준비완료")
        
        st.markdown("---")
        st.metric("고객 페르소나", "7명")
        st.metric("직원 페르소나", "3명")
        st.metric("총 벡터 스토어", f"{len(st.session_state.rag.vector_stores)}개")
        
        if st.button("🔄 시스템 재시작", use_container_width=True):
            st.session_state.initialized = False
            st.rerun()

# Main content
if not st.session_state.initialized:
    # Welcome screen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 핵심 기능
        - **7개 세분화 페르소나**
        - **실시간 토론 시각화**
        - **데이터 기반 RAG**
        - **투표 시스템**
        """)
    
    with col2:
        st.markdown("""
        ### 📊 데이터 규모
        - **총 댓글**: 40,377개
        - **전환 의도**: 2,621개
        - **평균 만족도**: 4.2/5
        - **전환 완료율**: 52.2%
        """)
    
    with col3:
        st.markdown("""
        ### 🛠️ 기술 스택
        - **AutoGen** 0.7.x
        - **LangChain** + ChromaDB
        - **OpenAI** GPT-4
        - **Streamlit** UI
        """)
    
    st.info("👈 사이드바에서 API 키를 입력하고 시스템을 초기화하세요.")

else:
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎬 토론", "👥 페르소나", "📊 결과"])
    
    with tab1:
        st.header("🎬 토론 시작")
        
        # Topic selection
        topics = {
            "생태계 전쟁": "Apple vs Samsung 생태계, Samsung의 극복 전략은?",
            "S펜 제거": "Fold 7의 S펜 제거, 옳은 결정이었나?",
            "가격 정당성": "230만원 가격, 적정한가?",
            "폴더블 미래": "5년 후 폴더블이 주류가 될까?"
        }
        
        selected_topic = st.selectbox("📌 토론 주제", list(topics.keys()))
        st.info(topics[selected_topic])
        
        # Participant selection
        st.markdown("### 참가자 선택")
        
        col1, col2, col3 = st.columns(3)
        
        selected_personas = []
        
        with col1:
            st.markdown("**📱 Galaxy**")
            if st.checkbox("폴더블매력파 (564명)", key="p1"):
                selected_personas.append("foldable_enthusiast")
            if st.checkbox("생태계딜레마 (37명)", key="p2"):
                selected_personas.append("ecosystem_dilemma")
            if st.checkbox("폴더블비판자 (80명)", key="p3"):
                selected_personas.append("foldable_critical")
            if st.checkbox("정기업그레이더 (58명)", key="p4"):
                selected_personas.append("upgrade_cycler")
        
        with col2:
            st.markdown("**🍎 iPhone**")
            if st.checkbox("가성비추구자 (좋아요376!)", key="p5"):
                selected_personas.append("value_seeker")
            if st.checkbox("Apple생태계충성 (79명)", key="p6"):
                selected_personas.append("apple_ecosystem_loyal")
            if st.checkbox("디자인피로 (48명)", key="p7"):
                selected_personas.append("design_fatigue")
        
        with col3:
            st.markdown("**💼 직원**")
            selected_employees = []
            if st.checkbox("마케터", key="e1"):
                selected_employees.append("marketer")
            if st.checkbox("개발자", key="e2"):
                selected_employees.append("developer")
            if st.checkbox("디자이너", key="e3"):
                selected_employees.append("designer")
        
        # Settings
        num_rounds = st.slider("라운드 수", 1, 3, 1)
        
        # Start button
        if st.button("🚀 토론 시작", type="primary", use_container_width=True):
            if not selected_personas and not selected_employees:
                st.warning("⚠️ 최소 1명의 참가자를 선택하세요!")
            else:
                # Prepare participants
                participants = []
                for p_type in selected_personas:
                    agent = st.session_state.customer_agents.get_agent(p_type)
                    if agent:
                        participants.append(agent)
                
                for e_type in selected_employees:
                    agent = st.session_state.employee_agents.get_agent(e_type)
                    if agent:
                        participants.append(agent)
                
                # Show debate info
                st.markdown("---")
                st.markdown(f"### 🎬 토론: {selected_topic}")
                st.markdown(f"**참가자**: {len(participants)}명")
                
                # Progress
                progress = st.progress(0)
                status = st.empty()
                
                # Messages display
                msg_container = st.container()
                
                # Run debate
                async def run():
                    status.info("🔄 토론 시작 중...")
                    
                    result = await st.session_state.debate_system.run_debate(
                        topic=f"{selected_topic}: {topics[selected_topic]}",
                        num_rounds=num_rounds,
                        selected_agents=participants
                    )
                    
                    return result
                
                result = asyncio.run(run())
                
                if result and result.get('success'):
                    progress.progress(100)
                    status.success("✅ 토론 완료!")
                    
                    # Save result
                    st.session_state.debate_results.append(result)
                    
                    # Display messages
                    messages = result.get('messages', [])
                    
                    with msg_container:
                        st.markdown("### 💬 토론 내용")
                        
                        for i, msg in enumerate(messages, 1):
                            if i == 1:
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            # Icon and style
                            if source in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                                icon = "📱"
                                style = "galaxy-msg"
                            elif source in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                                icon = "🍎"
                                style = "iphone-msg"
                            else:
                                icon = "💼"
                                style = "employee-msg"
                            
                            st.markdown(f"""
                            <div class="message-card {style}">
                                <strong>{icon} {source}</strong><br><br>
                                {content}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            progress.progress(int((i / len(messages)) * 100))
    
    with tab2:
        st.header("👥 페르소나 상세 정보")
        
        # Galaxy personas
        st.markdown("## 📱 Galaxy 페르소나 (4명)")
        
        galaxy_data = [
            {
                "name": "폴더블매력파",
                "size": "564명",
                "likes": "63.2",
                "emoji": "💚",
                "quote": "폴드7 진짜 신세계! 프맥보다 가벼워요!",
                "features": ["전환 완료", "열성팬", "높은 만족도", "적극 추천"]
            },
            {
                "name": "생태계딜레마",
                "size": "37명",
                "likes": "31.0",
                "emoji": "💔",
                "quote": "폴더블 너무 끌리는데... 애플워치 때문에...",
                "features": ["강하게 고려", "높은 공감", "생태계 고민", "망설임"]
            },
            {
                "name": "폴더블비판자",
                "size": "80명",
                "likes": "7.7",
                "emoji": "😤",
                "quote": "카메라 초점 못 잡고 배터리 조루. 근데 폴더블은 못 버려.",
                "features": ["사용 중", "불만 多", "개선 요구", "현실적 피드백"]
            },
            {
                "name": "정기업그레이더",
                "size": "58명",
                "likes": "6.9",
                "emoji": "🔄",
                "quote": "Fold 2, 4, 6 썼고 8 기다려요.",
                "features": ["폴더블 전문가", "정기 교체", "세대 비교", "얼리어답터"]
            }
        ]
        
        cols = st.columns(2)
        for i, data in enumerate(galaxy_data):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="message-card galaxy-msg">
                    <h3>{data['emoji']} {data['name']}</h3>
                    <p><strong>규모:</strong> {data['size']} | <strong>평균 좋아요:</strong> {data['likes']}개</p>
                    <p><em>"{data['quote']}"</em></p>
                    <p>{'  '.join([f'<span class="persona-badge galaxy-badge">{f}</span>' for f in data['features']])}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # iPhone personas
        st.markdown("## 🍎 iPhone 페르소나 (3명)")
        
        iphone_data = [
            {
                "name": "가성비추구자",
                "size": "8명",
                "likes": "376.8",
                "emoji": "🎯",
                "quote": "17 일반이 가성비 압승. 50만원 차이 가치 없어요.",
                "features": ["높은 영향력", "합리적", "수치 분석", "커뮤니티 리더"]
            },
            {
                "name": "Apple생태계충성",
                "size": "79명",
                "likes": "12.6",
                "emoji": "🏆",
                "quote": "13년 Apple 생태계. 비싸지만 유지.",
                "features": ["장기 사용", "충성 고객", "생태계 가치", "가격 고려"]
            },
            {
                "name": "디자인피로",
                "size": "48명",
                "likes": "11.4",
                "emoji": "😴",
                "quote": "iPhone 10년 썼는데 디자인 똑같아요.",
                "features": ["변화 갈망", "혁신 부족", "Galaxy 부러움", "유지"]
            }
        ]
        
        cols = st.columns(3)
        for i, data in enumerate(iphone_data):
            with cols[i]:
                st.markdown(f"""
                <div class="message-card iphone-msg">
                    <h4>{data['emoji']} {data['name']}</h4>
                    <p><strong>{data['size']}</strong></p>
                    <p>좋아요: <strong>{data['likes']}</strong></p>
                    <p><em>"{data['quote']}"</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Employees
        st.markdown("## 💼 직원 페르소나 (3명)")
        
        employee_data = [
            {"name": "마케터", "role": "전략 수립", "icon": "📊", "insight": "전환율 52.2%"},
            {"name": "개발자", "role": "기술 구현", "icon": "⚙️", "insight": "화면전환 버그 우선"},
            {"name": "디자이너", "role": "UX/UI", "icon": "🎨", "insight": "만족도 17.5%"}
        ]
        
        cols = st.columns(3)
        for i, data in enumerate(employee_data):
            with cols[i]:
                st.markdown(f"""
                <div class="message-card employee-msg">
                    <h4>{data['icon']} {data['name']}</h4>
                    <p>{data['role']}</p>
                    <p><em>{data['insight']}</em></p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.header("📊 토론 결과 및 통계")
        
        if st.session_state.debate_results:
            st.markdown(f"### 총 {len(st.session_state.debate_results)}개 토론 완료")
            
            for i, result in enumerate(reversed(st.session_state.debate_results), 1):
                with st.expander(f"#{i}: {result.get('topic', 'Unknown')}", expanded=(i==1)):
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("참가자", f"{len(result.get('participants', []))}명")
                    with col2:
                        st.metric("메시지", f"{len(result.get('messages', []))}개")
                    with col3:
                        status_icon = "✅" if result.get('success') else "❌"
                        st.metric("상태", f"{status_icon} {'성공' if result.get('success') else '실패'}")
                    
                    # Messages
                    if result.get('messages'):
                        st.markdown("#### 💬 대화 내용")
                        
                        for j, msg in enumerate(result['messages'], 1):
                            if j == 1:
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            with st.chat_message(source):
                                st.markdown(f"**{source}**")
                                st.write(content)
                    
                    # Download
                    st.download_button(
                        "📥 이 토론 다운로드",
                        data=json.dumps(result, ensure_ascii=False, indent=2, default=str),
                        file_name=f"debate_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key=f"download_{i}"
                    )
        else:
            st.info("아직 진행된 토론이 없습니다.")

if __name__ == "__main__":
    pass



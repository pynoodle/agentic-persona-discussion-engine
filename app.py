#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
멀티 에이전트 토론 시스템 GUI
Streamlit 기반 실시간 토론 시각화
"""

import streamlit as st
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import modules
from rag.rag_manager import RAGManager
from agents.customer_agents_v2 import CustomerAgentsV2
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator
from debate.debate_system import DebateSystem

# Page config
st.set_page_config(
    page_title="멀티 에이전트 토론 시스템",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.persona-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid;
}
.galaxy-card { border-left-color: #1e88e5; background-color: #e3f2fd; }
.iphone-card { border-left-color: #757575; background-color: #f5f5f5; }
.employee-card { border-left-color: #43a047; background-color: #e8f5e9; }
.message-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #ccc;
}
.stats-box {
    padding: 1rem;
    background-color: #fff3e0;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.rag = None
    st.session_state.customer_agents = None
    st.session_state.employee_agents = None
    st.session_state.facilitator = None
    st.session_state.debate_system = None
    st.session_state.debate_history = []
    st.session_state.debate_running = False

def initialize_system():
    """시스템 초기화"""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다!")
        st.info("사이드바에서 API 키를 입력하거나 .env 파일에 설정해주세요.")
        return False
    
    try:
        with st.spinner("🔄 RAG 시스템 초기화 중..."):
            st.session_state.rag = RAGManager()
            st.session_state.rag.load_all_personas()
        
        with st.spinner("🔄 에이전트 생성 중..."):
            st.session_state.customer_agents = CustomerAgentsV2(st.session_state.rag)
            st.session_state.employee_agents = EmployeeAgents(st.session_state.rag)
            st.session_state.facilitator = Facilitator()
        
        with st.spinner("🔄 토론 시스템 설정 중..."):
            st.session_state.debate_system = DebateSystem(
                st.session_state.customer_agents,
                st.session_state.employee_agents,
                st.session_state.facilitator
            )
        
        st.session_state.initialized = True
        return True
    
    except Exception as e:
        st.error(f"❌ 초기화 실패: {e}")
        return False

def display_persona_info(agents, title, card_class):
    """페르소나 정보 표시"""
    st.markdown(f"### {title}")
    
    for agent_type, agent in agents.items():
        with st.expander(f"📱 {agent.name}", expanded=False):
            # Get persona info from agent's system message
            st.markdown(f"**Agent Type**: `{agent_type}`")
            st.markdown(f"**Name**: {agent.name}")

def main():
    """메인 함수"""
    
    # Title
    st.title("🎭 멀티 에이전트 토론 시스템")
    st.markdown("**AutoGen + LangChain 기반 실시간 페르소나 토론**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password"
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.markdown("---")
        
        # Initialize button
        if st.button("🚀 시스템 초기화", type="primary", use_container_width=True):
            success = initialize_system()
            if success:
                st.success("✅ 초기화 완료!")
        
        if st.session_state.initialized:
            st.success("✅ 시스템 준비 완료")
            
            st.markdown("---")
            st.markdown("### 📊 시스템 정보")
            st.metric("고객 페르소나", f"{len(st.session_state.customer_agents.agents)}명")
            st.metric("직원 페르소나", f"{len(st.session_state.employee_agents.agents)}명")
            st.metric("벡터 스토어", f"{len(st.session_state.rag.vector_stores)}개")
    
    # Main content
    if not st.session_state.initialized:
        st.info("👈 사이드바에서 시스템을 초기화해주세요.")
        
        # Show system overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 주요 기능")
            st.markdown("""
            - 7개 세분화 페르소나
            - 실제 데이터 기반 RAG
            - 실시간 토론 시각화
            - 투표 시스템
            """)
        
        with col2:
            st.markdown("### 📱 고객 페르소나")
            st.markdown("""
            - 폴더블매력파 (564명)
            - 생태계딜레마 (37명)
            - 폴더블비판자 (80명)
            - 정기업그레이더 (58명)
            - 가성비추구자 (8명)
            - Apple생태계충성 (79명)
            - 디자인피로 (48명)
            """)
        
        with col3:
            st.markdown("### 💼 직원 페르소나")
            st.markdown("""
            - 마케터
            - 개발자
            - 디자이너
            """)
        
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 토론 시작", "👥 페르소나", "📊 토론 기록", "⚙️ 설정"])
    
    with tab1:
        st.header("🎯 토론 시작")
        
        # Debate topic selection
        debate_topics = {
            "생태계 전쟁": {
                "title": "Apple vs Samsung 생태계 전쟁",
                "description": "Samsung은 어떻게 Apple 생태계 장벽을 극복할 수 있을까?",
                "participants": ["foldable_enthusiast", "ecosystem_dilemma", "apple_ecosystem_loyal", "marketer"]
            },
            "S펜 제거": {
                "title": "Galaxy Fold 7의 S펜 제거 결정",
                "description": "얇고 가벼움 vs S펜 기능, 옳은 결정이었나?",
                "participants": ["upgrade_cycler", "foldable_critical", "designer", "developer"]
            },
            "가격 전략": {
                "title": "Galaxy Fold 7 가격 230만원의 적정성",
                "description": "혁신 기술의 프리미엄 vs 대중화 전략",
                "participants": ["value_seeker", "foldable_enthusiast", "apple_ecosystem_loyal", "marketer"]
            },
            "폴더블 미래": {
                "title": "폴더블 폰의 미래",
                "description": "5년 후 주류가 될 것인가?",
                "participants": ["foldable_enthusiast", "design_fatigue", "upgrade_cycler", "designer", "marketer"]
            }
        }
        
        topic_choice = st.selectbox(
            "토론 주제 선택",
            list(debate_topics.keys())
        )
        
        selected_topic = debate_topics[topic_choice]
        
        st.markdown(f"### {selected_topic['title']}")
        st.info(selected_topic['description'])
        
        # Participant selection
        st.markdown("#### 참가자 선택")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Galaxy 페르소나**")
            galaxy_selections = []
            if st.checkbox("폴더블매력파 (564명, 좋아요 63)", value="foldable_enthusiast" in selected_topic['participants']):
                galaxy_selections.append("foldable_enthusiast")
            if st.checkbox("생태계딜레마 (37명, 좋아요 31)", value="ecosystem_dilemma" in selected_topic['participants']):
                galaxy_selections.append("ecosystem_dilemma")
            if st.checkbox("폴더블비판자 (80명)", value="foldable_critical" in selected_topic['participants']):
                galaxy_selections.append("foldable_critical")
            if st.checkbox("정기업그레이더 (58명)", value="upgrade_cycler" in selected_topic['participants']):
                galaxy_selections.append("upgrade_cycler")
            
            st.markdown("**iPhone 페르소나**")
            if st.checkbox("가성비추구자 (8명, 좋아요 376!)", value="value_seeker" in selected_topic['participants']):
                galaxy_selections.append("value_seeker")
            if st.checkbox("Apple생태계충성 (79명)", value="apple_ecosystem_loyal" in selected_topic['participants']):
                galaxy_selections.append("apple_ecosystem_loyal")
            if st.checkbox("디자인피로 (48명)", value="design_fatigue" in selected_topic['participants']):
                galaxy_selections.append("design_fatigue")
        
        with col2:
            st.markdown("**직원 페르소나**")
            employee_selections = []
            if st.checkbox("마케터", value="marketer" in selected_topic['participants']):
                employee_selections.append("marketer")
            if st.checkbox("개발자", value="developer" in selected_topic['participants']):
                employee_selections.append("developer")
            if st.checkbox("디자이너", value="designer" in selected_topic['participants']):
                employee_selections.append("designer")
        
        # Rounds selection
        num_rounds = st.slider("토론 라운드 수", min_value=1, max_value=3, value=1)
        
        st.markdown("---")
        
        # Start debate button
        if st.button("🚀 토론 시작", type="primary", use_container_width=True):
            if not galaxy_selections and not employee_selections:
                st.warning("⚠️ 최소 1명의 참가자를 선택해주세요!")
            else:
                st.session_state.debate_running = True
                
                # Collect participants
                participants = []
                for agent_type in galaxy_selections:
                    agent = st.session_state.customer_agents.get_agent(agent_type)
                    if agent:
                        participants.append(agent)
                
                for agent_type in employee_selections:
                    agent = st.session_state.employee_agents.get_agent(agent_type)
                    if agent:
                        participants.append(agent)
                
                st.markdown("### 🎬 토론 진행 중...")
                st.markdown(f"**주제**: {selected_topic['title']}")
                st.markdown(f"**참가자**: {len(participants)}명")
                
                # Progress container
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Messages container
                messages_container = st.container()
                
                # Run debate
                async def run_debate_async():
                    try:
                        with status_text:
                            st.info("🔄 토론 시작 중...")
                        
                        result = await st.session_state.debate_system.run_debate(
                            topic=selected_topic['title'],
                            num_rounds=num_rounds,
                            selected_agents=participants
                        )
                        
                        st.session_state.debate_history.append(result)
                        st.session_state.debate_running = False
                        
                        return result
                    
                    except Exception as e:
                        st.error(f"❌ 토론 중 오류: {e}")
                        return None
                
                # Run async debate
                result = asyncio.run(run_debate_async())
                
                if result and result.get('success'):
                    progress_bar.progress(100)
                    status_text.success("✅ 토론 완료!")
                    
                    # Display messages
                    with messages_container:
                        st.markdown("### 💬 토론 내용")
                        
                        messages = result.get('messages', [])
                        total_messages = len(messages)
                        
                        for i, msg in enumerate(messages, 1):
                            if i == 1:  # Skip system message
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            # Determine card style
                            if source in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                                card_style = "galaxy-card"
                                icon = "📱"
                            elif source in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                                card_style = "iphone-card"
                                icon = "🍎"
                            elif source in ['Marketer', 'Developer', 'Designer']:
                                card_style = "employee-card"
                                icon = "💼"
                            else:
                                card_style = "message-box"
                                icon = "💬"
                            
                            # Display message
                            st.markdown(f"""
                            <div class="persona-card {card_style}">
                                <strong>{icon} {source}</strong>
                                <p>{content}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Update progress
                            progress = int((i / total_messages) * 100)
                            progress_bar.progress(progress)
    
    with tab2:
        st.header("👥 페르소나 정보")
        
        if st.session_state.initialized:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📱 Galaxy 페르소나 (4명)")
                
                personas_info = [
                    ("폴더블매력파", "564명", "63.2", "전환완료", "💚", "폴드7 진짜 신세계!"),
                    ("생태계딜레마", "37명", "31.0", "강하게고려중", "💔", "애플워치 때문에..."),
                    ("폴더블비판자", "80명", "7.7", "불만多", "😤", "카메라 못 잡음"),
                    ("정기업그레이더", "58명", "6.9", "정기교체", "🔄", "Fold 2, 4, 6..."),
                ]
                
                for name, size, likes, status, icon, phrase in personas_info:
                    st.markdown(f"""
                    <div class="persona-card galaxy-card">
                        <strong>{icon} {name}</strong><br>
                        규모: {size} | 좋아요: {likes} | 상태: {status}<br>
                        <em>"{phrase}"</em>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 🍎 iPhone 페르소나 (3명)")
                
                iphone_personas = [
                    ("가성비추구자", "8명", "376.8", "합리적선택", "🎯", "17 일반 가성비 압승"),
                    ("Apple생태계충성", "79명", "12.6", "충성고객", "🏆", "13년 생태계"),
                    ("디자인피로", "48명", "11.4", "불만유지", "😴", "디자인 똑같아"),
                ]
                
                for name, size, likes, status, icon, phrase in iphone_personas:
                    st.markdown(f"""
                    <div class="persona-card iphone-card">
                        <strong>{icon} {name}</strong><br>
                        규모: {size} | 좋아요: {likes} | 상태: {status}<br>
                        <em>"{phrase}"</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 💼 직원 페르소나 (3명)")
                
                employee_info = [
                    ("마케터", "전략수립", "💡", "전환율 52.2% 데이터"),
                    ("개발자", "기술구현", "⚙️", "화면전환 버그 우선"),
                    ("디자이너", "UX/UI", "🎨", "디자인 만족도 17.5%"),
                ]
                
                for name, role, icon, insight in employee_info:
                    st.markdown(f"""
                    <div class="persona-card employee-card">
                        <strong>{icon} {name}</strong><br>
                        역할: {role}<br>
                        <em>"{insight}"</em>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 📊 데이터 통계")
                st.markdown("""
                <div class="stats-box">
                    <strong>실제 데이터 기반</strong><br>
                    • 총 댓글: 40,377개<br>
                    • 전환 의도: 2,621개<br>
                    • iPhone → Galaxy: 1,093명 (70%)<br>
                    • 전환 완료율: 52.2%<br>
                    • 평균 만족도: 4.2/5
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.header("📊 토론 기록")
        
        if st.session_state.debate_history:
            st.markdown(f"**총 토론 수**: {len(st.session_state.debate_history)}개")
            
            for i, debate in enumerate(reversed(st.session_state.debate_history), 1):
                with st.expander(f"토론 #{i}: {debate.get('topic', 'Unknown')}", expanded=(i==1)):
                    st.markdown(f"**참가자**: {', '.join(debate.get('participants', []))}")
                    st.markdown(f"**성공 여부**: {'✅ 성공' if debate.get('success') else '❌ 실패'}")
                    
                    if debate.get('messages'):
                        st.markdown("**토론 내용**:")
                        
                        for j, msg in enumerate(debate['messages'], 1):
                            if j == 1:
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            with st.chat_message(source):
                                st.markdown(content)
        else:
            st.info("아직 진행된 토론이 없습니다. '토론 시작' 탭에서 토론을 시작해주세요.")
    
    with tab4:
        st.header("⚙️ 고급 설정")
        
        st.markdown("### 🔧 RAG 설정")
        if st.session_state.rag:
            st.metric("로드된 페르소나", len(st.session_state.rag.vector_stores))
            
            with st.expander("페르소나 목록"):
                for persona_name in sorted(st.session_state.rag.vector_stores.keys()):
                    st.text(f"✓ {persona_name}")
        
        st.markdown("### 📥 데이터 다운로드")
        
        if st.session_state.debate_history:
            # Download debate history as JSON
            import json
            
            debate_json = json.dumps(
                st.session_state.debate_history,
                ensure_ascii=False,
                indent=2,
                default=str
            )
            
            st.download_button(
                label="📥 토론 기록 다운로드 (JSON)",
                data=debate_json,
                file_name=f"debate_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()


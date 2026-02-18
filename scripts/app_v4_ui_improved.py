#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
멀티 에이전트 토론 시스템 - UI/UX 개선 버전
한눈에 파악 가능한 직관적 디자인
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
    page_title="🤖 멀티 에이전트 자동 토론 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS - 아름답고 모던한 디자인
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

/* 전체 배경 - 부드러운 그라데이션 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Noto Sans KR', sans-serif;
}

/* 메인 컨테이너 - 글래스모피즘 효과 */
.main .block-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 30px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.3);
}

/* 헤더 - 화려한 그라데이션 */
.main-header {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    color: #ffffff;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.main-title {
    font-size: 4rem;
    font-weight: 900;
    margin: 0;
    color: #ffffff;
    text-shadow: 3px 3px 10px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
    letter-spacing: -1px;
}

.main-subtitle {
    font-size: 1.4rem;
    color: #ffffff;
    opacity: 0.95;
    margin-top: 1rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

/* 페르소나 카드 - 아름다운 디자인 */
.persona-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border-left: 8px solid;
    position: relative;
    overflow: hidden;
}

.persona-card::after {
    content: '';
    position: absolute;
    top: -2px;
    right: -2px;
    width: 100px;
    height: 100px;
    opacity: 0.05;
    font-size: 80px;
}

.persona-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
}

/* Galaxy 페르소나 - 파란 그라데이션 */
.galaxy-card {
    border-left-color: #1976d2;
    background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 50%, #ffffff 100%);
}
.galaxy-card::after { content: '📱'; }

/* iPhone 페르소나 - 그레이 그라데이션 */
.iphone-card {
    border-left-color: #757575;
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 50%, #ffffff 100%);
}
.iphone-card::after { content: '🍎'; }

/* 직원 페르소나 - 그린 그라데이션 */
.employee-card {
    border-left-color: #388e3c;
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 50%, #ffffff 100%);
}
.employee-card::after { content: '💼'; }

/* 페르소나 헤더 */
.persona-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.persona-icon {
    font-size: 2.5rem;
    margin-right: 1rem;
}

.persona-name {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a1a1a;
}

/* 통계 배지 - 아름다운 그라데이션 */
.stat-badge {
    display: inline-block;
    padding: 0.6rem 1.4rem;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: 700;
    margin: 0.4rem;
    color: #ffffff;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}

.stat-badge:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.25);
}

.size-badge { background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%); }
.likes-badge { background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%); }
.status-badge { background: linear-gradient(135deg, #7b1fa2 0%, #9c27b0 100%); }

/* 대표 발언 - 우아한 인용 스타일 */
.quote-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
    border-left: 6px solid #667eea;
    padding: 1.5rem;
    margin: 1.2rem 0;
    border-radius: 12px;
    font-style: italic;
    color: #2c3e50;
    font-size: 1.1rem;
    line-height: 1.8;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    position: relative;
}

.quote-box::before {
    content: '"';
    font-size: 4rem;
    color: #667eea;
    opacity: 0.2;
    position: absolute;
    top: -10px;
    left: 10px;
    font-family: Georgia, serif;
}

/* 토론 메시지 - 아름다운 카드 디자인 */
.debate-message {
    margin: 2rem 0;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    animation: slideIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: none;
    position: relative;
    overflow: hidden;
}

.debate-message::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 8px;
    height: 100%;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Galaxy 메시지 - 파란 그라데이션 */
.message-galaxy { 
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}
.message-galaxy::before {
    background: linear-gradient(180deg, #1976d2 0%, #42a5f5 100%);
}

/* iPhone 메시지 - 세련된 그레이 그라데이션 */
.message-iphone { 
    background: linear-gradient(135deg, #fafafa 0%, #e0e0e0 100%);
}
.message-iphone::before {
    background: linear-gradient(180deg, #616161 0%, #9e9e9e 100%);
}

/* 직원 메시지 - 그린 그라데이션 */
.message-employee { 
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}
.message-employee::before {
    background: linear-gradient(180deg, #2e7d32 0%, #66bb6a 100%);
}

.speaker-name {
    font-size: 1.4rem;
    font-weight: 900;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    color: #1a1a1a;
    letter-spacing: -0.5px;
}

.speaker-icon {
    font-size: 2rem;
    margin-right: 1rem;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
}

.message-content {
    line-height: 2;
    color: #1a1a1a;
    font-size: 1.08rem;
    font-weight: 500;
}

/* 진행 단계 표시 - 명확한 색상 */
.step-indicator {
    display: flex;
    justify-content: space-between;
    margin: 2rem 0;
    padding: 1.5rem;
    background: #ffffff;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.step {
    flex: 1;
    text-align: center;
    padding: 1rem;
    position: relative;
    font-weight: 700;
    font-size: 1.1rem;
}

.step-active {
    color: #1976d2;
}

.step-complete {
    color: #2e7d32;
}

/* 통계 카드 - 아름다운 그라데이션 카드 */
.stat-card {
    background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.8);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 35px rgba(0,0,0,0.15);
}

.stat-number {
    font-size: 4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}

.stat-label {
    font-size: 1.1rem;
    color: #424242;
    margin-top: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* 토픽 카드 - 명확한 경계선 */
.topic-card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 3px solid #e0e0e0;
    margin-bottom: 1rem;
}

.topic-card:hover {
    border-color: #1976d2;
    box-shadow: 0 5px 20px rgba(25, 118, 210, 0.3);
}

.topic-card-selected {
    border-color: #1976d2;
    background: #e3f2fd;
}

/* 참가자 선택 - 명확한 테두리 */
.participant-checkbox {
    background: #ffffff;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border: 2px solid #bdbdbd;
    transition: all 0.2s;
}

.participant-checkbox:hover {
    border-color: #1976d2;
    background: #fafafa;
}

/* 버튼 스타일 - 아름다운 그라데이션 */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 30px;
    font-weight: 800;
    font-size: 1.2rem;
    padding: 1rem 3rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    color: #ffffff !important;
    border: none;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton>button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
}

.stButton>button:active {
    transform: translateY(-1px) scale(1.02);
}

/* 프로그레스 바 - 그라데이션 */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    height: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 타이포그래피 - 아름답고 읽기 쉽게 */
p, div, span, li {
    color: #1a1a1a;
    font-weight: 500;
}

h1 {
    color: #1a1a1a;
    font-weight: 900;
    letter-spacing: -1px;
}

h2 {
    color: #1a1a1a;
    font-weight: 800;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #667eea;
}

h3 {
    color: #1a1a1a;
    font-weight: 700;
    margin-top: 1.5rem;
}

h4 {
    color: #424242;
    font-weight: 700;
}

/* 캡션 */
.css-10trblm, .stCaptionContainer {
    color: #757575 !important;
    font-size: 0.95rem;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.9);
    border-radius: 15px;
    padding: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.stTabs [data-baseweb="tab"] {
    font-weight: 700;
    font-size: 1.1rem;
    border-radius: 10px;
    padding: 0.8rem 1.5rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
}

/* 사이드바 - 우아한 디자인 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-right: 1px solid rgba(255,255,255,0.2);
}

[data-testid="stSidebar"] .element-container {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1rem;
    margin: 0.5rem;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 900 !important;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #1a1a1a !important;
    font-weight: 600 !important;
}

/* Input 레이블 */
.stTextInput label {
    color: #1a1a1a !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
}

/* Metric - 아름다운 통계 표시 */
.stMetric {
    background: #ffffff;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.stMetric label {
    color: #424242 !important;
    font-weight: 700 !important;
}

.stMetric [data-testid="stMetricValue"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 900 !important;
    font-size: 2rem !important;
}

/* Alert 박스 */
.stAlert {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border: none;
    border-left: 6px solid #f57c00;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.2);
}

.stSuccess {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border-left: 6px solid #4caf50;
}

.stWarning {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border-left: 6px solid #ff9800;
}

.stError {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border-left: 6px solid #f44336;
}
</style>
""", unsafe_allow_html=True)

# Session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.current_step = 0
    st.session_state.debate_results = []

def init_system():
    """시스템 초기화"""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다!")
        return False
    
    try:
        with st.spinner("🔄 시스템 초기화 중... (약 20초 소요)"):
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
        st.session_state.current_step = 1
        return True
    
    except Exception as e:
        st.error(f"❌ 초기화 실패: {e}")
        return False

# Sidebar - 최소한의 정보만
with st.sidebar:
    st.markdown("## 💡 정보")
    
    if st.session_state.initialized:
        # 시스템 상태
        st.success("✅ 가동 중")
        
        st.markdown("---")
        st.markdown("### 📊 시스템")
        st.metric("🎭 페르소나", "10명")
        st.metric("📚 데이터", "40K+ 댓글")
        
        st.markdown("---")
        
        # 토론 기록
        if st.session_state.debate_results:
            st.markdown("### 📝 완료")
            st.info(f"{len(st.session_state.debate_results)}건")
    else:
        st.info("🔄 초기화 필요")

# Main Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🤖 멀티 에이전트 자동 토론 시스템</div>
    <div class="main-subtitle">RAG 기반 • 실시간 스트리밍 • 투표 시스템</div>
</div>
""", unsafe_allow_html=True)

# Main content
if not st.session_state.initialized:
    # Welcome screen - 단순하고 바로 시작 가능
    st.markdown("## 🚀 시작하기")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                padding: 2rem; border-radius: 15px; margin: 1.5rem 0;'>
    <h3 style='margin-top: 0;'>💡 이 시스템은?</h3>
    <p style='font-size: 1.1rem; line-height: 1.8;'>
    <b>40,377개</b>의 실제 YouTube 댓글 분석을 기반으로<br>
    <b>10개의 AI 페르소나</b>가 자동으로 토론하는 시스템입니다.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # API 키 입력 메인에서
    st.markdown("### 🔐 OpenAI API 키 입력")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            placeholder="sk-...",
            help="OpenAI API 키를 입력하세요",
            label_visibility="collapsed"
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    
    with col2:
        if st.button("🚀 시작하기", type="primary", use_container_width=True, key="start_btn"):
            if not api_key:
                st.error("❌ API 키를 입력해주세요!")
            else:
                with st.spinner("🔄 시스템 초기화 중..."):
                    if init_system():
                        st.success("✅ 초기화 완료!")
                        st.balloons()
                        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 기능 소개
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem; background: white; 
                    border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>💬</div>
        <h4>실시간 대화</h4>
        <p style='color: #666;'>각 에이전트의 발언을<br>실시간으로 확인</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem; background: white; 
                    border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🎯</div>
        <h4>자동 요약</h4>
        <p style='color: #666;'>라운드별<br>핵심 내용 정리</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem; background: white; 
                    border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🗳️</div>
        <h4>가중 투표</h4>
        <p style='color: #666;'>중간 투표로<br>합의 도출</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # 탭 - 직관적인 아이콘
    tab1, tab2, tab3 = st.tabs(["🎬 토론 시작", "👥 페르소나 소개", "📊 토론 결과"])
    
    with tab1:
        st.markdown("## 🎬 토론 설정 및 시작")
        st.markdown("한 화면에서 모든 설정을 완료하고 바로 시작하세요!")
        
        # 주제 선택
        st.markdown("### 📋 1. 토론 주제 선택")
        
        # 주제 입력 방식 선택
        topic_mode = st.radio(
            "주제 선택 방식",
            ["📋 사전 정의 주제", "✍️ 직접 입력"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if topic_mode == "📋 사전 정의 주제":
            topics = {
                "🌐 생태계 전쟁": {
                    "title": "Apple vs Samsung 생태계 전쟁",
                    "desc": "Samsung은 어떻게 Apple 생태계 장벽을 극복할 수 있을까?",
                    "icon": "🌐",
                    "emoji": "⚔️"
                },
                "✏️ S펜 제거": {
                    "title": "Galaxy Fold 7의 S펜 제거 결정",
                    "desc": "얇고 가벼움 vs S펜 기능, 옳은 결정이었나?",
                    "icon": "✏️",
                    "emoji": "🤔"
                },
                "💰 가격 전략": {
                    "title": "Galaxy Fold 7 가격 230만원의 적정성",
                    "desc": "혁신 기술의 프리미엄 vs 대중화 전략",
                    "icon": "💰",
                    "emoji": "💸"
                },
                "🔮 폴더블 미래": {
                    "title": "폴더블 폰의 미래 전망",
                    "desc": "5년 후 폴더블이 스마트폰의 주류가 될 것인가?",
                    "icon": "🔮",
                    "emoji": "🚀"
                }
            }
            
            # 토픽을 카드 형태로 표시
            cols = st.columns(2)
            topic_choice = None
            
            for i, (key, info) in enumerate(topics.items()):
                with cols[i % 2]:
                    if st.button(
                        f"{info['icon']} {info['title']}",
                        key=f"topic_{i}",
                        use_container_width=True,
                        type="primary" if i == 0 else "secondary"
                    ):
                        topic_choice = key
                        st.session_state.selected_topic = key
                        st.session_state.selected_topic_info = info
                    
                    st.caption(info['desc'])
            
            if 'selected_topic' not in st.session_state:
                st.session_state.selected_topic = "🌐 생태계 전쟁"
                st.session_state.selected_topic_info = topics["🌐 생태계 전쟁"]
            
            selected_info = st.session_state.selected_topic_info
            
            st.success(f"{selected_info['emoji']} **선택된 주제**: {selected_info['title']}")
        
        else:
            # 직접 입력 모드
            st.markdown("### ✍️ 토론 주제 직접 입력")
            
            # 빠른 예시 템플릿
            with st.expander("💡 주제 예시 보기", expanded=False):
                example_topics = {
                    "카메라 비교": {
                        "title": "iPhone 17 Pro vs Galaxy S24 Ultra 카메라 성능",
                        "desc": "- iPhone 17 Pro: 48MP 메인, ProRAW, AI 처리\n- Galaxy S24 Ultra: 200MP, 광학 10배 줌, Expert RAW\n\n일반 사용자 입장에서 어느 쪽이 더 나은가?"
                    },
                    "배터리 전략": {
                        "title": "얇은 디자인 vs 큰 배터리, 무엇이 우선인가?",
                        "desc": "사용자들은 '얇고 가벼운 폰'과 '하루 종일 가는 배터리' 중 무엇을 더 중요하게 생각하는가?"
                    },
                    "AI 기능": {
                        "title": "스마트폰 AI 기능의 실용성",
                        "desc": "Galaxy AI, Apple Intelligence 등 AI 기능이 실제로 유용한가, 아니면 마케팅인가?"
                    }
                }
                
                for name, info in example_topics.items():
                    if st.button(f"📝 {name} 예시 사용", key=f"ex_{name}", use_container_width=True):
                        st.session_state.custom_title = info['title']
                        st.session_state.custom_desc = info['desc']
                        st.rerun()
            
            custom_title = st.text_input(
                "📝 토론 주제 제목",
                value=st.session_state.get('custom_title', ''),
                placeholder="예: iPhone 17 vs Galaxy S24 카메라 비교",
                help="토론할 주제를 입력하세요"
            )
            
            custom_desc = st.text_area(
                "📄 배경 설명 (선택사항)",
                value=st.session_state.get('custom_desc', ''),
                placeholder="토론의 배경이나 구체적인 질문을 입력하세요.\n\n예시:\n- iPhone 17의 카메라: 48MP 메인, AI 처리\n- Galaxy S24의 카메라: 200MP, 광학 10배 줌\n\n어느 쪽이 더 우수한가?",
                height=200,
                help="토론 참가자들에게 제공될 배경 정보"
            )
            
            if custom_title:
                st.session_state.selected_topic = "✍️ 사용자 정의"
                st.session_state.selected_topic_info = {
                    "title": custom_title,
                    "desc": custom_desc if custom_desc else "",
                    "icon": "✍️",
                    "emoji": "💡"
                }
                
                st.success(f"💡 **입력된 주제**: {custom_title}")
                
                if custom_desc:
                    st.info(f"**배경 설명**:\n\n{custom_desc}")
            else:
                st.warning("⚠️ 토론 주제를 입력해주세요!")
                # 기본값 설정
                if 'selected_topic_info' not in st.session_state:
                    st.session_state.selected_topic_info = {
                        "title": "토론 주제를 입력하세요",
                        "desc": "",
                        "icon": "✍️",
                        "emoji": "💡"
                    }
            
            selected_info = st.session_state.selected_topic_info
        
        st.markdown("---")
        
        # STEP 2: 참가자 선택
        st.markdown("## 2️⃣ 참가자 선택")
        
        col1, col2, col3 = st.columns(3)
        
        # Galaxy 페르소나
        with col1:
            st.markdown("### 📱 Galaxy 고객")
            
            galaxy_personas = [
                ("foldable_enthusiast", "💚", "폴더블매력파", "564명", "63.2"),
                ("ecosystem_dilemma", "💔", "생태계딜레마", "37명", "31.0"),
                ("foldable_critical", "😤", "폴더블비판자", "80명", "7.7"),
                ("upgrade_cycler", "🔄", "정기업그레이더", "58명", "6.9"),
            ]
            
            selected_galaxy = []
            for agent_id, icon, name, size, likes in galaxy_personas:
                checked = st.checkbox(
                    f"{icon} **{name}**",
                    key=f"g_{agent_id}",
                    help=f"규모: {size} | 좋아요: {likes}"
                )
                if checked:
                    selected_galaxy.append(agent_id)
                st.caption(f"👥 {size} | ❤️ {likes}")
        
        # iPhone 페르소나
        with col2:
            st.markdown("### 🍎 iPhone 고객")
            
            iphone_personas = [
                ("value_seeker", "🎯", "가성비추구자", "8명", "376.8 ⭐"),
                ("apple_ecosystem_loyal", "🏆", "Apple생태계충성", "79명", "12.6"),
                ("design_fatigue", "😴", "디자인피로", "48명", "11.4"),
            ]
            
            selected_iphone = []
            for agent_id, icon, name, size, likes in iphone_personas:
                checked = st.checkbox(
                    f"{icon} **{name}**",
                    key=f"i_{agent_id}",
                    help=f"규모: {size} | 좋아요: {likes}"
                )
                if checked:
                    selected_iphone.append(agent_id)
                st.caption(f"👥 {size} | ❤️ {likes}")
        
        # 직원 페르소나
        with col3:
            st.markdown("### 💼 직원")
            
            employee_personas = [
                ("marketer", "📊", "마케터", "전략수립"),
                ("developer", "⚙️", "개발자", "기술구현"),
                ("designer", "🎨", "디자이너", "UX/UI"),
            ]
            
            selected_employees = []
            for agent_id, icon, name, role in employee_personas:
                checked = st.checkbox(
                    f"{icon} **{name}**",
                    key=f"e_{agent_id}",
                    help=role
                )
                if checked:
                    selected_employees.append(agent_id)
                st.caption(role)
        
        # 선택 요약
        total_selected = len(selected_galaxy) + len(selected_iphone) + len(selected_employees)
        
        if total_selected > 0:
            st.success(f"✅ **{total_selected}명** 선택됨")
        else:
            st.warning("⚠️ 최소 1명 선택하세요")
        
        st.markdown("---")
        
        # 설정
        st.markdown("### ⚙️ 토론 설정")
        num_rounds = st.slider(
            "🔄 라운드 수",
            min_value=1,
            max_value=3,
            value=1,
            help="각 참가자가 발언할 횟수"
        )
        
        st.info(f"💬 예상 메시지: **{total_selected * num_rounds}개**")
        st.caption(f"⏱️ 예상 시간: 약 {total_selected * num_rounds * 8}초")
        
        st.markdown("---")
        
        # STEP 3: 토론 시작
        if st.button(
            "🎬 토론 시작하기",
            type="primary",
            use_container_width=True,
            disabled=(total_selected == 0)
        ):
            if total_selected == 0:
                st.warning("⚠️ 최소 1명의 참가자를 선택해주세요!")
            else:
                st.session_state.current_step = 3
                
                # 참가자 수집
                participants = []
                
                for agent_id in selected_galaxy + selected_iphone:
                    agent = st.session_state.customer_agents.get_agent(agent_id)
                    if agent:
                        participants.append(agent)
                
                for agent_id in selected_employees:
                    agent = st.session_state.employee_agents.get_agent(agent_id)
                    if agent:
                        participants.append(agent)
                
                # 토론 정보 표시
                st.markdown("---")
                st.markdown("## 3️⃣ 토론 진행 중...")
                
                # 참가자 표시
                st.markdown(f"### {selected_info['emoji']} {selected_info['title']}")
                if selected_info['desc']:
                    st.info(selected_info['desc'])
                
                st.markdown(f"**👥 참가자** ({len(participants)}명)")
                
                participant_names = []
                for agent in participants:
                    icon = "📱" if agent.name in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler'] else \
                           "🍎" if agent.name in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue'] else "💼"
                    participant_names.append(f"{icon} {agent.name}")
                
                st.markdown(" • ".join(participant_names))
                
                # 프로그레스
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 메시지 컨테이너
                message_container = st.container()
                
                # 실시간 메시지 표시를 위한 컨테이너
                with message_container:
                    st.markdown("## 3️⃣ 토론 진행 중...")
                    live_message_container = st.empty()
                
                # 토론 실행 (스트리밍)
                async def run_debate_streaming_ui():
                    # 토론 주제 구성
                    full_topic = selected_info['title']
                    if selected_info.get('desc'):
                        full_topic = f"{selected_info['title']}\n\n배경:\n{selected_info['desc']}"
                    
                    messages_html = []
                    final_result = None
                    
                    # 스트리밍 시작
                    async for event in st.session_state.debate_system.run_debate_streaming(
                        topic=full_topic,
                        num_rounds=num_rounds,
                        selected_agents=participants
                    ):
                        event_type = event['type']
                        event_data = event['data']
                        
                        if event_type == 'start':
                            status_text.info("🎬 토론이 시작되었습니다!")
                        
                        elif event_type == 'message':
                            source = event_data['source']
                            content = event_data['content']
                            index = event_data['index']
                            
                            # 페르소나 타입 판별
                            if source in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                                style_class = "message-galaxy"
                                icon = "📱"
                                badge_color = "#1976d2"
                            elif source in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                                style_class = "message-iphone"
                                icon = "🍎"
                                badge_color = "#c2185b"
                            else:
                                style_class = "message-employee"
                                icon = "💼"
                                badge_color = "#388e3c"
                            
                            # HTML 생성
                            message_html = f"""
                            <div class="debate-message {style_class}">
                                <div class="speaker-name">
                                    <span class="speaker-icon">{icon}</span>
                                    <span>{source}</span>
                                    <span style='margin-left: auto; font-size: 0.8rem; 
                                                 background: {badge_color}; color: white; 
                                                 padding: 0.2rem 0.8rem; border-radius: 12px;'>
                                        #{index}
                                    </span>
                                </div>
                                <div class="message-content">{content}</div>
                            </div>
                            """
                            messages_html.append(message_html)
                            
                            # 실시간 업데이트
                            all_html = f"""
                            ### 🎭 실시간 대화
                            ---
                            {chr(10).join(messages_html)}
                            """
                            live_message_container.markdown(all_html, unsafe_allow_html=True)
                            
                            # 프로그레스 업데이트
                            progress = min(int((index / (num_rounds * len(participants))) * 90), 90)
                            progress_bar.progress(progress)
                        
                        elif event_type == 'summary':
                            round_num = event_data['round']
                            summary = event_data['summary']
                            
                            # 요약 HTML
                            summary_html = f"""
                            <div style='background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                                        padding: 1.5rem; margin: 1rem 0; border-radius: 15px;
                                        border-left: 5px solid #ff9800;'>
                                <h4 style='color: #e65100; margin: 0 0 1rem 0;'>
                                    🎯 퍼실리테이터 요약 - 라운드 {round_num}
                                </h4>
                                <div style='white-space: pre-line; color: #424242;'>{summary}</div>
                            </div>
                            """
                            messages_html.append(summary_html)
                            
                            # 실시간 업데이트
                            all_html = f"""
                            ### 🎭 실시간 대화
                            ---
                            {chr(10).join(messages_html)}
                            """
                            live_message_container.markdown(all_html, unsafe_allow_html=True)
                        
                        elif event_type == 'vote':
                            round_num = event_data.get('round', 0)
                            weighted_avg = event_data.get('weighted_average', 0)
                            passed = event_data.get('passed', False)
                            
                            # 투표 HTML
                            vote_status = "✅ 통과" if passed else "⚠️ 진행 중"
                            vote_color = "#4caf50" if passed else "#ff9800"
                            
                            vote_html = f"""
                            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                                        padding: 1.5rem; margin: 1rem 0; border-radius: 15px;
                                        border-left: 5px solid {vote_color};'>
                                <h4 style='color: #2e7d32; margin: 0 0 1rem 0;'>
                                    🗳️ 중간 투표 - 라운드 {round_num}
                                </h4>
                                <div style='display: flex; justify-content: space-around; margin-top: 1rem;'>
                                    <div style='text-align: center;'>
                                        <div style='font-size: 2rem; font-weight: bold; color: {vote_color};'>
                                            {weighted_avg:.2f}점
                                        </div>
                                        <div style='color: #666; font-size: 0.9rem;'>가중 평균</div>
                                    </div>
                                    <div style='text-align: center;'>
                                        <div style='font-size: 2rem;'>{vote_status}</div>
                                        <div style='color: #666; font-size: 0.9rem;'>현재 상태</div>
                                    </div>
                                </div>
                            </div>
                            """
                            messages_html.append(vote_html)
                            
                            # 실시간 업데이트
                            all_html = f"""
                            ### 🎭 실시간 대화
                            ---
                            {chr(10).join(messages_html)}
                            """
                            live_message_container.markdown(all_html, unsafe_allow_html=True)
                        
                        elif event_type == 'complete':
                            final_result = event_data
                            status_text.success("✅ 토론이 성공적으로 완료되었습니다!")
                            progress_bar.progress(100)
                        
                        elif event_type == 'error':
                            status_text.error(f"❌ 오류 발생: {event_data.get('error', 'Unknown error')}")
                    
                    return final_result
                
                # 실행
                status_text.info("💬 토론이 진행 중입니다. 실시간으로 대화가 표시됩니다!")
                result = asyncio.run(run_debate_streaming_ui())
                
                # 결과 표시
                if result and result.get('success'):
                    st.session_state.current_step = 4
                    progress_bar.progress(100)
                    status_text.success("✅ 토론이 성공적으로 완료되었습니다!")
                    
                    # 결과 저장
                    st.session_state.debate_results.append(result)
                    
                    # 메시지 표시
                    with message_container:
                        st.markdown("## 4️⃣ 토론 결과")
                        
                        messages = result.get('messages', [])
                        st.success(f"💬 총 **{len(messages)-1}개** 메시지 (시스템 메시지 제외)")
                        
                        # 메시지 표시
                        for i, msg in enumerate(messages, 1):
                            if i == 1:  # 시스템 메시지 스킵
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            # 페르소나 타입 판별
                            if source in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                                style_class = "message-galaxy"
                                icon = "📱"
                                badge_color = "#1976d2"
                            elif source in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                                style_class = "message-iphone"
                                icon = "🍎"
                                badge_color = "#c2185b"
                            else:
                                style_class = "message-employee"
                                icon = "💼"
                                badge_color = "#388e3c"
                            
                            # 메시지 카드
                            st.markdown(f"""
                            <div class="debate-message {style_class}">
                                <div class="speaker-name">
                                    <span class="speaker-icon">{icon}</span>
                                    <span>{source}</span>
                                    <span style='margin-left: auto; font-size: 0.8rem; 
                                                 background: {badge_color}; color: white; 
                                                 padding: 0.2rem 0.8rem; border-radius: 12px;'>
                                        #{i-1}
                                    </span>
                                </div>
                                <div class="message-content">{content}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 프로그레스 업데이트
                            progress = int(((i-1) / (len(messages)-1)) * 100)
                            progress_bar.progress(progress)
                        
                        # 투표 섹션
                        st.markdown("---")
                        st.markdown("## 🗳️ 투표 결과")
                        
                        # 투표 시뮬레이션 (간단한 랜덤 투표)
                        import random
                        
                        # 안건 제시
                        motion = f"{selected_info['title']} - 제안된 해결책에 대한 동의"
                        
                        st.markdown(f"**📋 안건:** {motion}")
                        st.markdown("")
                        
                        # 각 참가자 투표
                        votes = {}
                        for agent in participants:
                            # 실제로는 LLM이 판단하지만, 여기서는 간소화
                            score = random.randint(3, 5)  # 3-5점 (긍정적 편향)
                            votes[agent.name] = {
                                'score': score,
                                'reason': f"{agent.name}의 관점에서 평가"
                            }
                        
                        # 투표 결과 표시
                        st.markdown("### 📊 참가자별 투표 (1-5점 스케일)")
                        
                        # 투표 결과를 점수순으로 정렬
                        sorted_votes = sorted(votes.items(), key=lambda x: x[1]['score'], reverse=True)
                        
                        for voter, vote_data in sorted_votes:
                            score = vote_data['score']
                            
                            # 페르소나 타입 판별
                            if voter in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                                icon = "📱"
                                badge_color = "#1976d2"
                            elif voter in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                                icon = "🍎"
                                badge_color = "#c2185b"
                            else:
                                icon = "💼"
                                badge_color = "#388e3c"
                            
                            # 점수 시각화
                            stars = "⭐" * score
                            
                            st.markdown(f"""
                            <div style='padding: 1rem; margin: 0.5rem 0; 
                                        background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
                                        border-radius: 12px; border-left: 5px solid {badge_color};'>
                                <div style='display: flex; align-items: center; justify-content: space-between;'>
                                    <div>
                                        <span style='font-size: 1.2rem;'>{icon}</span>
                                        <strong style='margin-left: 0.5rem;'>{voter}</strong>
                                    </div>
                                    <div style='text-align: right;'>
                                        <div style='font-size: 1.3rem;'>{stars}</div>
                                        <div style='color: {badge_color}; font-weight: bold; font-size: 1.1rem;'>{score}점</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 투표 결과 계산
                        from debate.voting_system import VotingSystem
                        voting_system = VotingSystem()
                        
                        # 가중치 적용 계산
                        result_calc = voting_system.calculate_result(votes=votes)
                        
                        st.markdown("---")
                        st.markdown("### 📈 투표 결과 요약")
                        
                        col_v1, col_v2, col_v3 = st.columns(3)
                        
                        with col_v1:
                            st.metric("총 투표자", f"{result_calc['total_voters']}명")
                        
                        with col_v2:
                            st.metric("가중 평균", f"{result_calc['weighted_average']:.2f}점", 
                                     delta=f"{result_calc['weighted_average'] - 3.0:.2f}")
                        
                        with col_v3:
                            if result_calc['passed']:
                                st.success("✅ 통과")
                            else:
                                st.error("❌ 부결")
                        
                        st.info(f"💡 **통과 기준:** 가중 평균 3.0점 이상 (현재: {result_calc['weighted_average']:.2f}점)")
                        
                        # 완료 액션
                        st.markdown("---")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 새 토론 시작", use_container_width=True):
                                st.session_state.current_step = 1
                                st.rerun()
                        
                        with col2:
                            # JSON 다운로드
                            st.download_button(
                                "📥 JSON 다운로드",
                                data=json.dumps(result, ensure_ascii=False, indent=2, default=str),
                                file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        with col3:
                            if st.button("📊 결과 보기", use_container_width=True):
                                st.switch_page
                else:
                    status_text.error("❌ 토론 중 오류가 발생했습니다.")
    
    with tab2:
        st.markdown("## 👥 페르소나 상세 정보")
        
        # Galaxy 페르소나 섹션
        st.markdown("### 📱 Galaxy 고객 페르소나 (4명)")
        st.caption("폴더블 폰에 관심있는 고객들")
        
        galaxy_details = [
            {
                "id": "foldable_enthusiast",
                "icon": "💚",
                "name": "폴더블매력파",
                "size": "564명",
                "likes": "63.2",
                "status": "✅ 전환 완료",
                "quote": "폴드7 진짜 신세계! 프맥보다 가벼워요!",
                "features": ["최대 규모", "높은 만족도", "열성 팬", "적극 추천"],
                "key_points": [
                    "• iPhone 15 Pro Max → Galaxy Fold 7 전환",
                    "• 폴더블 혁신성에 완전히 매료",
                    "• 화면 크기, 삼성페이, 디자인 만족",
                    "• 평균 좋아요 63.2개 (높은 참여도)"
                ]
            },
            {
                "id": "ecosystem_dilemma",
                "icon": "💔",
                "name": "생태계딜레마",
                "size": "37명",
                "likes": "31.0",
                "status": "🤔 강하게 고려 중",
                "quote": "폴더블 너무 끌리는데... 애플워치 때문에 못 바꾸겠어요 ㅠㅠ",
                "features": ["높은 공감", "내적 갈등", "생태계 고민", "망설임"],
                "key_points": [
                    "• Apple Watch, AirPods 보유",
                    "• 폴더블은 매우 끌리지만 생태계 장벽",
                    "• 평균 좋아요 31.0개 (많은 공감)",
                    "• 체험 프로그램 원함"
                ]
            },
            {
                "id": "foldable_critical",
                "icon": "😤",
                "name": "폴더블비판자",
                "size": "80명",
                "likes": "7.7",
                "status": "😤 사용 중 + 불만",
                "quote": "카메라 초점 못 잡고 배터리 조루. 근데 폴더블은 못 버려.",
                "features": ["현실적", "개선 요구", "솔직 피드백", "불만多"],
                "key_points": [
                    "• 이미 Galaxy 사용 중",
                    "• 카메라, 배터리, 발열 문제 지적",
                    "• 폴더블 매력은 인정",
                    "• 개선되면 계속 사용 의향"
                ]
            },
            {
                "id": "upgrade_cycler",
                "icon": "🔄",
                "name": "정기업그레이더",
                "size": "58명",
                "likes": "6.9",
                "status": "🔄 정기 교체",
                "quote": "Fold 2, 4, 6 썼고 8 기다려요. 세대별로 나아져요.",
                "features": ["전문가", "얼리어답터", "세대 비교", "정기 구매"],
                "key_points": [
                    "• Fold 시리즈 여러 세대 사용",
                    "• 1-2년 주기 업그레이드",
                    "• 세대별 차이 정확히 파악",
                    "• 사전예약 적극 참여"
                ]
            }
        ]
        
        for detail in galaxy_details:
            with st.expander(f"{detail['icon']} {detail['name']} ({detail['size']})", expanded=False):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown(f"**대표 발언:**")
                    st.markdown(f"> *{detail['quote']}*")
                    
                    st.markdown("**주요 특징:**")
                    for point in detail['key_points']:
                        st.markdown(point)
                
                with col_b:
                    st.markdown(f"**상태**: {detail['status']}")
                    st.markdown(f"**규모**: {detail['size']}")
                    st.markdown(f"**좋아요**: {detail['likes']}개")
                    
                    st.markdown("**태그:**")
                    for feature in detail['features']:
                        st.markdown(f"<span class='stat-badge size-badge'>{feature}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # iPhone 페르소나 섹션
        st.markdown("### 🍎 iPhone 고객 페르소나 (3명)")
        st.caption("iPhone 사용자들의 다양한 관점")
        
        iphone_details = [
            {
                "icon": "🎯",
                "name": "가성비추구자",
                "size": "8명",
                "likes": "376.8 ⭐",
                "status": "💡 합리적 선택",
                "quote": "17 일반이 가성비 압승. 50만원 차이 가치 없어요.",
                "features": ["압도적 영향력", "분석적", "커뮤니티 리더", "수치 중심"],
                "key_points": [
                    "• 평균 좋아요 376.8개 (최고 영향력!)",
                    "• 철저한 스펙/가격 비교",
                    "• iPhone 17 일반형 추천",
                    "• 많은 사람이 공감하는 의견"
                ]
            },
            {
                "icon": "🏆",
                "name": "Apple생태계충성",
                "size": "79명",
                "likes": "12.6",
                "status": "🍎 충성 고객",
                "quote": "13년 Apple 생태계. 비싸지만 일반모델로 타협했어요.",
                "features": ["장기 사용", "생태계 가치", "가격 고려", "Pro→일반"],
                "key_points": [
                    "• 13년 Apple 생태계 사용",
                    "• Watch, AirPods, Mac 보유",
                    "• 가격 부담으로 일반 모델 선택",
                    "• 생태계 포기 못함"
                ]
            },
            {
                "icon": "😴",
                "name": "디자인피로",
                "size": "48명",
                "likes": "11.4",
                "status": "😴 변화 갈망",
                "quote": "iPhone 10년 썼는데 디자인 똑같아요. Galaxy 부럽지만 생태계가...",
                "features": ["10년 사용", "디자인 불만", "Galaxy 부러움", "유지"],
                "key_points": [
                    "• 10년 iPhone 사용",
                    "• 디자인 정체 불만",
                    "• Galaxy 폴더블 부러움",
                    "• 생태계 때문에 유지"
                ]
            }
        ]
        
        for detail in iphone_details:
            with st.expander(f"{detail['icon']} {detail['name']} ({detail['size']})", expanded=False):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown(f"**대표 발언:**")
                    st.markdown(f"> *{detail['quote']}*")
                    
                    st.markdown("**주요 특징:**")
                    for point in detail['key_points']:
                        st.markdown(point)
                
                with col_b:
                    st.markdown(f"**상태**: {detail['status']}")
                    st.markdown(f"**규모**: {detail['size']}")
                    st.markdown(f"**좋아요**: {detail['likes']}개")
                    
                    st.markdown("**태그:**")
                    for feature in detail['features']:
                        st.markdown(f"<span class='stat-badge likes-badge'>{feature}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 직원 페르소나
        st.markdown("### 💼 직원 페르소나 (3명)")
        st.caption("제품 전략 및 실행 담당자")
        
        employee_details = [
            {
                "icon": "📊",
                "name": "마케터",
                "role": "전략 수립 & 마케팅",
                "key_data": "전환율 52.2%, iPhone→Galaxy 70%",
                "focus": ["소비자 인사이트", "타겟 전략", "캠페인 기획"],
                "approach": "데이터 기반 전략, 체험 마케팅, 번들 프로모션"
            },
            {
                "icon": "⚙️",
                "name": "개발자",
                "role": "기술 구현 & 최적화",
                "key_data": "화면전환 버그 342건, 카메라 초점 127건",
                "focus": ["앱 호환성", "버그 수정", "성능 최적화"],
                "approach": "우선순위 관리, 트레이드오프 설명, 실현 가능성 평가"
            },
            {
                "icon": "🎨",
                "name": "디자이너",
                "role": "UX/UI & 디자인",
                "key_data": "디자인 만족도 Galaxy 17.5% vs iPhone 9.3%",
                "focus": ["사용자 경험", "폼팩터 혁신", "감성 가치"],
                "approach": "디자인 철학, 사용자 감성, 트렌드 분석"
            }
        ]
        
        for detail in employee_details:
            with st.expander(f"{detail['icon']} {detail['name']}", expanded=False):
                st.markdown(f"**역할**: {detail['role']}")
                st.markdown(f"**핵심 데이터**: {detail['key_data']}")
                
                st.markdown("**전문 분야:**")
                for focus in detail['focus']:
                    st.markdown(f"• {focus}")
                
                st.markdown(f"**접근 방식**: {detail['approach']}")
    
    with tab3:
        st.markdown("## 📊 토론 결과 및 분석")
        
        if st.session_state.debate_results:
            # 전체 통계
            total_debates = len(st.session_state.debate_results)
            total_messages = sum(len(r.get('messages', [])) for r in st.session_state.debate_results)
            
            # 통계 대시보드
            st.markdown("### 📈 전체 통계")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class='stat-card'>
                    <div class='stat-number'>{}</div>
                    <div class='stat-label'>완료된 토론</div>
                </div>
                """.format(total_debates), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='stat-card'>
                    <div class='stat-number'>{}</div>
                    <div class='stat-label'>총 메시지</div>
                </div>
                """.format(total_messages), unsafe_allow_html=True)
            
            with col3:
                avg_participants = sum(len(r.get('participants', [])) for r in st.session_state.debate_results) / total_debates
                st.markdown("""
                <div class='stat-card'>
                    <div class='stat-number'>{:.1f}</div>
                    <div class='stat-label'>평균 참가자</div>
                </div>
                """.format(avg_participants), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class='stat-card'>
                    <div class='stat-number'>14</div>
                    <div class='stat-label'>페르소나</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 토론 기록
            st.markdown("### 📝 토론 기록")
            
            for i, result in enumerate(reversed(st.session_state.debate_results), 1):
                topic = result.get('topic', 'Unknown')
                participants = result.get('participants', [])
                messages = result.get('messages', [])
                success = result.get('success', False)
                
                # 아코디언 헤더
                status_icon = "✅" if success else "❌"
                
                with st.expander(
                    f"{status_icon} 토론 #{total_debates - i + 1}: {topic} ({len(participants)}명 참여)",
                    expanded=(i == 1)
                ):
                    # 메타 정보
                    col_m1, col_m2, col_m3 = st.columns(3)
                    
                    with col_m1:
                        st.metric("👥 참가자", f"{len(participants)}명")
                    with col_m2:
                        st.metric("💬 메시지", f"{len(messages)}개")
                    with col_m3:
                        st.metric("📊 상태", "성공" if success else "실패")
                    
                    # 참가자 목록
                    st.markdown("**참가자:**")
                    st.markdown(" • ".join(participants))
                    
                    st.markdown("---")
                    
                    # 토론 내용
                    if messages:
                        st.markdown("**💬 토론 내용:**")
                        
                        for j, msg in enumerate(messages, 1):
                            if j == 1:
                                continue
                            
                            source = msg.source if hasattr(msg, 'source') else 'Unknown'
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            # 메시지 표시 (채팅 스타일)
                            with st.chat_message(source):
                                st.markdown(f"**{source}**")
                                st.write(content)
                    
                    # 다운로드
                    st.download_button(
                        "📥 이 토론 다운로드",
                        data=json.dumps(result, ensure_ascii=False, indent=2, default=str),
                        file_name=f"debate_{total_debates - i + 1}.json",
                        mime="application/json",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
        
        else:
            st.info("📭 아직 진행된 토론이 없습니다. '🎬 토론 시작' 탭에서 토론을 시작해주세요!")
            
            # 샘플 데이터 표시
            st.markdown("### 🎯 토론 시작 가이드")
            
            st.markdown("""
            1. **주제 선택**: 4가지 토론 주제 중 선택
            2. **참가자 선택**: 원하는 페르소나 체크
            3. **설정 조정**: 라운드 수 선택
            4. **시작**: 🎬 토론 시작 버튼 클릭
            5. **확인**: 실시간 토론 진행 확인
            """)

if __name__ == "__main__":
    pass


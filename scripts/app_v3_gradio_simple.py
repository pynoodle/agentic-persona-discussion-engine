import gradio as gr
import os
import logging
from datetime import datetime, timedelta
import sqlite3
import shutil
import threading
import time
import random
from openai import OpenAI

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 전역 변수
initialized = False
temperature = 1.2
SESSION_TIMEOUT = 30  # 분
user_sessions = {}
api_usage_stats = {
    'total_calls': 0,
    'total_tokens': 0,
    'cost_estimate': 0.0
}

# 페르소나 정의
PERSONAS = {
    "foldable_enthusiast": {
        "name": "[I→G] 폴더블매력파",
        "short_name": "폴더블매력파",
        "direction": "I2G",
        "icon": "📱",
        "size": "564명",
        "type": "galaxy",
        "color": "#1976d2",
        "description": "Samsung 폴더블 폰을 사랑하는 사용자",
        "key_phrase": "폴드7 진짜 신세계예요! 프랙보다 가벼워요!"
    },
    "ecosystem_dilemma": {
        "name": "[I→G?] 생태계딜레마",
        "short_name": "생태계딜레마",
        "direction": "I2G?",
        "icon": "💔",
        "size": "37명",
        "type": "galaxy",
        "color": "#1976d2",
        "description": "iPhone에서 Galaxy로 전환을 고민하는 사용자",
        "key_phrase": "아이폰은 편하지만 갤럭시가 더 혁신적이에요"
    },
    "foldable_critical": {
        "name": "[I→G] 폴더블비판자",
        "short_name": "폴더블비판자",
        "direction": "I2G",
        "icon": "😤",
        "size": "80명",
        "type": "galaxy",
        "color": "#1976d2",
        "description": "폴더블 폰의 단점을 지적하는 사용자",
        "key_phrase": "폴더블은 아직 완성도가 부족해요"
    },
    "upgrade_cycler": {
        "name": "[G] 정기업그레이더",
        "short_name": "정기업그레이더",
        "direction": "G",
        "icon": "🔄",
        "size": "58명",
        "type": "galaxy",
        "color": "#1976d2",
        "description": "정기적으로 Galaxy를 업그레이드하는 사용자",
        "key_phrase": "매년 새 갤럭시가 나오는 게 기대돼요"
    },
    "value_seeker": {
        "name": "[I/G] 가성비추구자",
        "short_name": "가성비추구자",
        "direction": "I/G",
        "icon": "🎯",
        "size": "8명",
        "type": "iphone",
        "color": "#c2185b",
        "description": "가격 대비 성능을 중시하는 사용자",
        "key_phrase": "가격이 너무 비싸면 안 되죠"
    },
    "apple_ecosystem_loyal": {
        "name": "[I] Apple생태계충성",
        "short_name": "Apple생태계충성",
        "direction": "I",
        "icon": "🏆",
        "size": "79명",
        "type": "iphone",
        "color": "#c2185b",
        "description": "Apple 생태계에 충성하는 사용자",
        "key_phrase": "아이폰이 최고예요, 다른 건 필요 없어요"
    },
    "design_fatigue": {
        "name": "[I] 디자인피로",
        "short_name": "디자인피로",
        "direction": "I",
        "icon": "😴",
        "size": "48명",
        "type": "iphone",
        "color": "#c2185b",
        "description": "iPhone 디자인에 피로감을 느끼는 사용자",
        "key_phrase": "아이폰 디자인이 너무 똑같아요"
    },
    "marketer": {
        "name": "[직원] 마케터",
        "short_name": "마케터",
        "direction": "EMP",
        "icon": "📊",
        "role": "전략수립",
        "type": "employee",
        "color": "#388e3c",
        "description": "Samsung 마케팅 전문가",
        "key_phrase": "울트라급 경험을 펼치다! 얇음의 복음으로 바이럴을 만들었습니다"
    },
    "developer": {
        "name": "[직원] 개발자",
        "short_name": "개발자",
        "direction": "EMP",
        "icon": "⚙️",
        "role": "기술구현",
        "type": "employee",
        "color": "#388e3c",
        "description": "Samsung 개발 전문가",
        "key_phrase": "기술적으로 완벽한 제품을 만들었습니다"
    },
    "designer": {
        "name": "[직원] 디자이너",
        "short_name": "디자이너",
        "direction": "EMP",
        "icon": "🎨",
        "role": "UX/UI",
        "type": "employee",
        "color": "#388e3c",
        "description": "Samsung 디자인 전문가",
        "key_phrase": "사용자 경험을 최우선으로 고려했습니다"
    }
}

# 토론 주제
TOPICS = {
    "생태계 전쟁": {
        "title": "Apple vs Samsung 생태계 전쟁",
        "desc": "Samsung은 어떻게 Apple 생태계 장벽을 극복할 수 있을까?"
    },
    "S펜 제거": {
        "title": "Galaxy Fold 7의 S펜 제거 결정",
        "desc": "S펜을 제거한 것이 올바른 선택이었을까?"
    },
    "플립의 장점": {
        "title": "플립의 장점",
        "desc": "갤럭시 Z 플립 7의 주요 장점에 대해 토론합니다."
    },
    "폴드 vs 아이폰": {
        "title": "폴드 vs 아이폰",
        "desc": "갤럭시 Z 폴드 7과 아이폰의 비교 토론입니다."
    },
    "가격 정책": {
        "title": "폴더블 폰 가격 정책",
        "desc": "폴더블 폰의 가격이 적절한지 토론합니다."
    },
    "디자인 혁신": {
        "title": "디자인 혁신의 방향",
        "desc": "폴더블 폰 디자인의 미래 방향에 대해 토론합니다."
    }
}

def init_log_database():
    """로그 데이터베이스 초기화"""
    os.makedirs('logs', exist_ok=True)
    
    conn = sqlite3.connect('logs/user_activity.db')
    cursor = conn.cursor()
    
    # 사용자 활동 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            activity_type TEXT,
            timestamp DATETIME,
            details TEXT
        )
    ''')
    
    # 토론 세션 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debate_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            topic TEXT,
            topic_mode TEXT,
            selected_personas TEXT,
            num_rounds INTEGER,
            enable_voting BOOLEAN,
            start_time DATETIME,
            end_time DATETIME,
            duration REAL,
            total_messages INTEGER
        )
    ''')
    
    # 페르소나 응답 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persona_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            persona_id TEXT,
            persona_name TEXT,
            round_number INTEGER,
            response_content TEXT,
            response_time DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def log_user_activity_to_db(session_id, activity_type, **details):
    """사용자 활동을 데이터베이스에 기록"""
    try:
        conn = sqlite3.connect('logs/user_activity.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activities (session_id, activity_type, timestamp, details)
            VALUES (?, ?, ?, ?)
        ''', (session_id, activity_type, datetime.now(), str(details)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database logging error: {str(e)}")

def log_debate_session_to_db(session_id, topic, topic_mode, selected_personas, 
                            num_rounds, enable_voting, start_time, 
                            end_time=None, duration=None, total_messages=None):
    """토론 세션을 데이터베이스에 기록"""
    try:
        conn = sqlite3.connect('logs/user_activity.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO debate_sessions 
            (session_id, topic, topic_mode, selected_personas, num_rounds, 
             enable_voting, start_time, end_time, duration, total_messages)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, topic, topic_mode, str(selected_personas), num_rounds,
              enable_voting, start_time, end_time, duration, total_messages))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Debate session logging error: {str(e)}")

def log_persona_response_to_db(session_id, persona_id, persona_name, 
                             round_number, response_content, response_time):
    """페르소나 응답을 데이터베이스에 기록"""
    try:
        conn = sqlite3.connect('logs/user_activity.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO persona_responses 
            (session_id, persona_id, persona_name, round_number, response_content, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, persona_id, persona_name, round_number, response_content, response_time))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Persona response logging error: {str(e)}")

def initialize_system():
    """시스템 초기화"""
    global initialized, temperature
    
    try:
        # 데이터베이스 초기화
        init_log_database()
        
        initialized = True
        logger.info(f"System initialized | Temperature: {temperature}")
        
        return f"✅ 시스템 초기화 완료!\n\n🌡️ Temperature: {temperature}\n📊 로깅 시스템 활성화"
        
    except Exception as e:
        logger.error(f"System initialization error: {str(e)}")
        return f"❌ 시스템 초기화 실패: {str(e)}"

def run_debate_simple(topic_mode, topic_dropdown, custom_topic, selected_personas, num_rounds, enable_voting):
    """진짜 멀티 에이전트 토론 시스템"""
    
    if not initialized:
        yield [("System", "❌ 시스템을 먼저 초기화해주세요!")], "⏸️ 대기 중", None, 0, "시스템 미초기화"
        return
    
    if not selected_personas:
        yield [("System", "❌ 최소 1명의 참가자를 선택해주세요!")], "⏸️ 대기 중", None, 0, "참가자 없음"
        return
    
    # 토론 주제 결정
    if topic_mode == "✍️ 직접 입력":
        topic_display = custom_topic if custom_topic else "토론 주제 없음"
    else:
        topic_info = TOPICS.get(topic_dropdown, {"title": topic_dropdown, "desc": ""})
        topic_display = topic_info['title']
    
    # 세션 ID 생성
    import uuid
    session_id = f"user_{uuid.uuid4().hex[:8]}"
    start_time = datetime.now()
    
    # 채팅 히스토리
    chat_history = []
    chat_history.append(("System", f"**토론 시작!**\n\n📋 주제: {topic_display}\n👥 참가자: {len(selected_personas)}명\n🔄 라운드: {num_rounds}"))
    
    yield chat_history, "토론 시작!", None, 0, "토론 시작"
    
    try:
        # 퍼실리테이터 메시지
        facilitator_prompt = f"""
당신은 토론 퍼실리테이터입니다. 다음 역할을 수행하세요:

1. 토론 주제: {topic_display}
2. 참가자: {len(selected_personas)}명
3. 라운드: {num_rounds}

[퍼실리테이터 역할]
- 각 라운드마다 토론을 요약하고 심화시킬 질문 제시
- 참가자들의 의견을 정리하고 핵심 쟁점 도출
- 토론을 더 깊이 있게 발전시키는 방향 제시
- 갈등 상황에서 중재 역할

[토론 진행 방식]
- 각 참가자가 자신의 입장에서 주장
- 다른 참가자와 논쟁하고 반박
- 퍼실리테이터가 중간에 요약하고 심화 질문 제시
- 자연스러운 토론 흐름 유지

지금 토론을 시작하겠습니다.
"""
        
        chat_history.append(("퍼실리테이터", facilitator_prompt))
        yield chat_history, "퍼실리테이터가 토론을 시작합니다...", None, 0, "퍼실리테이터 시작"
        time.sleep(1)
        
        # 라운드별 토론 진행
        speakers = set()
        
        for round_num in range(1, num_rounds + 1):
            # 라운드 시작 메시지
            round_start_msg = f"**{round_num}라운드 시작**\n\n각 참가자가 자신의 입장에서 주장해주세요. 다른 참가자의 의견에 반박하거나 동의할 수 있습니다."
            chat_history.append(("퍼실리테이터", round_start_msg))
            yield chat_history, f"{round_num}라운드 진행 중...", None, 0, f"{round_num}라운드"
            time.sleep(1)
            
            # 각 참가자가 순차적으로 발언
            for i, persona_id in enumerate(selected_personas):
                try:
                    # 이전 발언들을 컨텍스트로 제공
                    context_messages = []
                    if len(chat_history) > 1:
                        recent_messages = chat_history[-5:]  # 최근 5개 메시지
                        for speaker, content in recent_messages:
                            if "퍼실리테이터" not in speaker and "System" not in speaker:
                                context_messages.append(f"{speaker}: {content}")
                    
                    # 토론 컨텍스트 구성
                    debate_context = f"""
[토론 상황]
- 주제: {topic_display}
- 라운드: {round_num}/{num_rounds}
- 현재 발언 순서: {i+1}/{len(selected_personas)}

[이전 발언들]
{chr(10).join(context_messages) if context_messages else "첫 번째 발언입니다."}

[발언 지침]
- 자신의 페르소나 입장에서 강력하게 주장하세요
- 다른 참가자의 의견에 반박하거나 동의하세요
- 구체적인 근거와 경험을 제시하세요
- 감정적이면서도 논리적으로 표현하세요
- 3-5문장으로 간결하게 발언하세요
"""
                    
                    # OpenAI API 호출
                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    
                    persona_info = PERSONAS.get(persona_id)
                    if persona_info:
                        system_msg = f"""당신은 "{persona_info['name']}"입니다.

[나의 성격과 경험]
{persona_info.get('description', '')}

[나의 실제 발언]
{persona_info.get('key_phrase', '')}

[답변 규칙]
- 1인칭으로: "나는 ~", "내 경험으로는 ~"
- 실제 사용자처럼 자연스럽게 답변
- 내 성격에 맞는 관점 유지
- 3-4문장으로 간결하게
- 감정적이면서도 논리적으로

토론에서 내 입장을 명확히 표현하세요!"""
                    else:
                        system_msg = "당신은 토론 참가자입니다. 자신의 입장을 명확히 표현하세요."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": debate_context}
                        ],
                        temperature=1.2,
                        max_tokens=300
                    )
                    
                    content = response.choices[0].message.content
                    
                    # 페르소나 정보
                    icon = persona_info['icon'] if persona_info else "💬"
                    name = persona_info['name'] if persona_info else persona_id
                    
                    # 발언 기록
                    speakers.add(name)
                    
                    # 메시지 추가
                    chat_history.append((f"{icon} {name}", content))
                    
                    # 페르소나 응답 로깅
                    log_persona_response_to_db(
                        session_id=session_id,
                        persona_id=persona_id,
                        persona_name=name,
                        round_number=round_num,
                        response_content=content,
                        response_time=datetime.now()
                    )
                    
                    yield chat_history, f"{name} 발언 중...", None, 0, f"{name} 발언"
                    time.sleep(2)  # 발언 간격
                    
                except Exception as e:
                    logger.error(f"Persona {persona_id} error: {str(e)}")
                    chat_history.append((f"❌ {persona_id}", f"발언 중 오류가 발생했습니다: {str(e)}"))
                    yield chat_history, f"{persona_id} 오류", None, 0, "오류"
                    time.sleep(1)
            
            # 라운드 완료 후 퍼실리테이터 요약
            if round_num < num_rounds:  # 마지막 라운드가 아닌 경우
                summary_content = f"""
**라운드 {round_num} 요약**

이번 라운드에서 다양한 관점이 제시되었습니다. 각 참가자들이 자신의 경험과 입장을 바탕으로 주장했습니다.

**핵심 쟁점:**
- 사용자 경험의 차이
- 기술적 우위성
- 가격 대비 가치

**다음 라운드 심화 질문:**
- 구체적인 사용 사례에서 어떤 차이가 있을까요?
- 장기적 관점에서 어떤 선택이 더 합리적일까요?
- 실제 사용자들의 반응은 어떨까요?

더 깊이 있는 논의를 위해 다음 라운드를 진행하겠습니다.
"""
                
                chat_history.append(("퍼실리테이터", summary_content))
                yield chat_history, f"퍼실리테이터가 {round_num}라운드를 요약합니다...", None, 0, "퍼실리테이터 요약"
                time.sleep(2)
        
        # 토론 완료
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 토론 세션 완료 로그
        log_debate_session_to_db(
            session_id=session_id,
            topic=topic_display,
            topic_mode=topic_mode,
            selected_personas=selected_personas,
            num_rounds=num_rounds,
            enable_voting=enable_voting,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_messages=len(chat_history)
        )
        
        # 토론 완료 메시지
        final_summary = f"""
**토론 완료!**

총 {len(speakers)}명의 참가자가 {num_rounds}라운드에 걸쳐 활발한 토론을 진행했습니다.

**토론 결과:**
- 총 발언 수: {len(chat_history)}개
- 참가자: {', '.join(speakers)}
- 토론 시간: {duration:.1f}초

**주요 성과:**
- 다양한 관점의 의견 교환
- 핵심 쟁점 도출
- 심화된 논의 진행

모든 참가자분들 수고하셨습니다!
"""
        
        chat_history.append(("퍼실리테이터", final_summary))
        yield chat_history, "토론 완료!", None, 0, "토론 완료"
        
    except Exception as e:
        logger.error(f"Debate execution error: {str(e)}")
        chat_history.append(("System", f"토론 실행 중 오류가 발생했습니다: {str(e)}"))
        yield chat_history, "토론 오류", None, 0, "오류"

# Gradio UI 구성
with gr.Blocks(title="멀티 에이전트 토론 시스템") as demo:
    gr.Markdown("# 🤖 멀티 에이전트 자동 토론 시스템")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 🎯 시스템 설정")
            
            init_btn = gr.Button("🚀 시스템 초기화", variant="primary")
            init_status = gr.Textbox(label="초기화 상태", interactive=False)
            
            gr.Markdown("## 🎭 참가자 선택")
            persona_checkboxes = gr.CheckboxGroup(
                choices=[
                    ("📱 폴더블매력파", "foldable_enthusiast"),
                    ("💔 생태계딜레마", "ecosystem_dilemma"),
                    ("😤 폴더블비판자", "foldable_critical"),
                    ("🔄 정기업그레이더", "upgrade_cycler"),
                    ("🎯 가성비추구자", "value_seeker"),
                    ("🏆 Apple생태계충성", "apple_ecosystem_loyal"),
                    ("😴 디자인피로", "design_fatigue"),
                    ("📊 마케터", "marketer"),
                    ("⚙️ 개발자", "developer"),
                    ("🎨 디자이너", "designer")
                ],
                label="토론 참가자 선택",
                value=["foldable_enthusiast"]
            )
            
            gr.Markdown("## ⚙️ 토론 설정")
            topic_mode = gr.Radio(
                choices=["📋 주제 선택", "✍️ 직접 입력"],
                value="📋 주제 선택",
                label="토론 주제 방식"
            )
            
            topic_dropdown = gr.Dropdown(
                choices=list(TOPICS.keys()),
                value="생태계 전쟁",
                label="토론 주제"
            )
            
            custom_topic = gr.Textbox(
                label="직접 입력 주제",
                placeholder="토론하고 싶은 주제를 입력하세요",
                visible=False
            )
            
            num_rounds = gr.Slider(
                minimum=1, maximum=5, value=2, step=1,
                label="토론 라운드 수"
            )
            
            enable_voting = gr.Checkbox(
                label="투표 기능 활성화",
                value=False
            )
            
            start_btn = gr.Button("🎬 토론 시작", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("## 💬 토론 진행")
            chatbot = gr.Chatbot(
                label="토론 채팅",
                height=600,
                show_label=False
            )
            
            status_text = gr.Textbox(
                label="상태",
                value="⏸️ 대기 중",
                interactive=False
            )
            
            with gr.Row():
                voting_chart = gr.Plot(label="투표 결과")
                avg_score = gr.Number(label="평균 점수", interactive=False)
                decision = gr.Textbox(label="결정", interactive=False)
    
    # 이벤트 핸들러
    def on_topic_mode_change(mode):
        return gr.update(visible=(mode == "✍️ 직접 입력"))
    
    topic_mode.change(on_topic_mode_change, inputs=topic_mode, outputs=custom_topic)
    
    init_btn.click(
        initialize_system,
        outputs=init_status
    )
    
    start_btn.click(
        run_debate_simple,
        inputs=[topic_mode, topic_dropdown, custom_topic, persona_checkboxes, num_rounds, enable_voting],
        outputs=[chatbot, status_text, voting_chart, avg_score, decision]
    )

# 앱 실행
if __name__ == "__main__":
    # 데이터베이스 초기화
    init_log_database()
    
    # 로그 시작 메시지
    logger.info("PersonaBot Multi-Agent Debate System Starting...")
    logger.info(f"Start Time: {datetime.now()}")
    logger.info(f"Authentication: Enabled (ID: sgrfuture)")
    logger.info(f"Session Timeout: {SESSION_TIMEOUT} minutes")
    logger.info("User Activity Logging: ENABLED")
    
    # 앱 실행
    demo.launch(
        server_name="0.0.0.0",
        server_port=7886,
        share=False,
        auth=("sgrfuture", "misanee"),
        inbrowser=True
    )

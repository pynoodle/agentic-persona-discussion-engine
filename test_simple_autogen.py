#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
가장 간단한 AutoGen 테스트
OpenAI API를 사용한 단순 에이전트 대화
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    sys.exit(1)

print("🧪 간단한 AutoGen 테스트\n")
print("="*80)
print("AutoGen 0.7.x 버전 호환성 테스트")
print("="*80 + "\n")

try:
    # AutoGen 0.7.x import 시도
    print("📦 AutoGen import 시도 중...\n")
    
    try:
        # 방법 1: 새로운 구조 (0.7.x)
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import TextMentionTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.ui import Console
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        
        print("✅ AutoGen 0.7.x 구조 감지")
        print("   - autogen_agentchat")
        print("   - autogen_ext.models.openai\n")
        
        use_new_api = True
        
    except ImportError:
        # 방법 2: 레거시 구조 (0.2.x)
        import autogen
        
        print("✅ AutoGen 0.2.x 레거시 구조 감지")
        print("   - autogen (통합 패키지)\n")
        
        use_new_api = False
    
    if use_new_api:
        print("="*80)
        print("🚀 AutoGen 0.7.x 방식으로 에이전트 생성")
        print("="*80 + "\n")
        
        # 1. Model Client 생성
        print("1️⃣ OpenAI 모델 클라이언트 생성...\n")
        model_client = OpenAIChatCompletionClient(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # 2. Assistant Agent 생성
        print("2️⃣ Assistant Agent 생성...\n")
        assistant = AssistantAgent(
            name="어시스턴트",
            model_client=model_client,
            system_message="당신은 친절한 AI 어시스턴트입니다. 간단명료하게 답변하세요."
        )
        
        print("✅ AutoGen 0.7.x 에이전트 생성 성공!")
        print("   - Model: gpt-4")
        print("   - Client: OpenAIChatCompletionClient")
        print("   - Agent: AssistantAgent\n")
        
        print("="*80)
        print("💡 AutoGen 0.7.x 사용 가능!")
        print("="*80)
        print("\n다음 단계:")
        print("1. agents/customer_agents.py 수정")
        print("2. agents/employee_agents.py 수정")
        print("3. debate/debate_system.py 재작성")
        
    else:
        print("="*80)
        print("🚀 AutoGen 0.2.x 방식으로 에이전트 생성")
        print("="*80 + "\n")
        
        # LLM 설정
        llm_config = {
            "config_list": [{
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }],
            "temperature": 0.7,
        }
        
        # Assistant Agent 생성
        print("1️⃣ Assistant Agent 생성...\n")
        assistant = autogen.AssistantAgent(
            name="어시스턴트",
            llm_config=llm_config,
            system_message="당신은 친절한 AI 어시스턴트입니다."
        )
        
        print("✅ AutoGen 0.2.x 에이전트 생성 성공!")
        print("   - Model: gpt-4")
        print("   - Config: llm_config")
        print("   - Agent: autogen.AssistantAgent\n")
        
        print("="*80)
        print("💡 AutoGen 0.2.x 사용 가능!")
        print("="*80)
        print("\n현재 프로젝트 코드와 호환됩니다!")
        print("test_debate.py를 실행할 수 있습니다.")

except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    print(f"오류 타입: {type(e).__name__}\n")
    
    import traceback
    print("상세 오류:")
    traceback.print_exc()
    
    print("\n💡 해결 방법:")
    print("1. pip uninstall -y pyautogen autogen-agentchat autogen-core autogen-ext")
    print("2. pip install pyautogen==0.2.33  # 안정 버전")
    print("3. 또는")
    print("   pip install autogen-agentchat autogen-ext  # 최신 버전")

print("\n" + "="*80)
print("🏁 테스트 종료")
print("="*80)


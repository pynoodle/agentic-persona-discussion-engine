#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Test Script for All 7 Segmented Personas
실제 데이터 기반 세분화 페르소나 토론 테스트
"""

import os
import sys
import asyncio

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from rag.rag_manager import RAGManager
from agents.customer_agents_v2 import CustomerAgentsV2
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator
from debate.debate_system import DebateSystem

async def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🎭 세분화된 전체 페르소나 토론 테스트")
    print("="*80 + "\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("Set it in .env file or as environment variable")
        return
    
    try:
        # 1. Initialize RAG
        print("[1] RAG 시스템 초기화...")
        rag = RAGManager()
        rag.load_all_personas()
        
        # 2. Initialize agents
        print("\n[2] 에이전트 초기화...")
        customer_agents = CustomerAgentsV2(rag)
        employee_agents = EmployeeAgents(rag)
        facilitator = Facilitator()
        
        print(f"\n✅ 총 {len(customer_agents.agents)}개 세분화 페르소나")
        
        print("\n📱 Galaxy 페르소나 (4개):")
        for agent in customer_agents.get_galaxy_agents():
            print(f"   ✓ {agent.name}")
        
        print("\n🍎 iPhone 페르소나 (3개):")
        for agent in customer_agents.get_iphone_agents():
            print(f"   ✓ {agent.name}")
        
        print(f"\n💼 직원 페르소나 ({len(employee_agents.agents)}개):")
        for name, agent in employee_agents.agents.items():
            print(f"   ✓ {agent.name}")
        
        # 3. Debate system
        print("\n[3] 토론 시스템 설정...")
        debate_system = DebateSystem(customer_agents, employee_agents, facilitator)
        print("✅ 준비 완료")
        
        # 4. Select participants
        print("\n[4] 참가자 선택...")
        
        participants = (
            customer_agents.get_all_agents() +  # All 7 customer personas
            [employee_agents.get_agent('marketer')]  # + 1 marketer
        )
        
        print(f"   총 {len(participants)}명 참가")
        
        # 5. Run debate
        print("\n[5] 토론 시작...")
        print("="*80)
        
        topic = "생태계 전쟁: Apple vs Samsung, Samsung이 어떻게 극복할 것인가?"
        
        result = await debate_system.run_debate(
            topic=topic,
            num_rounds=1,  # 1 round = each speaks once
            selected_agents=participants
        )
        
        # 6. Display results
        print("\n" + "="*80)
        print("📊 토론 결과")
        print("="*80)
        
        if result['success']:
            messages = result.get('messages', [])
            
            print(f"\n✅ 성공")
            print(f"총 메시지: {len(messages)}개")
            print(f"참가자: {', '.join(result['participants'])}")
            
            print("\n💬 토론 내용:")
            print("-"*80)
            
            for i, msg in enumerate(messages, 1):
                if i == 1:
                    continue
                
                source = msg.source if hasattr(msg, 'source') else 'Unknown'
                content = msg.content if hasattr(msg, 'content') else str(msg)
                
                # Add emoji
                if source in ['Foldable_Enthusiast', 'Ecosystem_Dilemma', 'Foldable_Critic', 'Upgrade_Cycler']:
                    icon = "📱"
                elif source in ['Value_Seeker', 'Apple_Ecosystem_Loyal', 'Design_Fatigue']:
                    icon = "🍎"
                else:
                    icon = "💼"
                
                print(f"\n[{i-1}] {icon} {source}:")
                
                # Split and indent
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"    {line}")
                
                print("-"*80)
            
            print("\n" + "="*80)
            print("✅ 전체 페르소나 토론 완료!")
            print("="*80)
        
        else:
            print(f"\n❌ 토론 실패")
            print(f"오류: {result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⏱️  참고: 8명의 에이전트가 참여하므로 3-5분 소요됩니다.\n")
    asyncio.run(main())

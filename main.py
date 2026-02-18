#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonaBot - 멀티 에이전트 토론 시스템 메인
AutoGen 0.7.x + LangChain RAG 통합
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    print("   .env 파일에 API 키를 설정해주세요.")
    sys.exit(1)

# 모듈 import
from rag.rag_manager import RAGManager
from agents.customer_agents import CustomerAgents
from agents.employee_agents import EmployeeAgents
from agents.facilitator import Facilitator
from debate.debate_system import DebateSystem
from debate.voting_system import VotingSystem


class DebateSystemManager:
    """토론 시스템 전체 관리자"""
    
    def __init__(self):
        """시스템 초기화"""
        print("\n" + "="*80)
        print("🚀 PersonaBot 시스템 초기화")
        print("="*80 + "\n")
        
        # 1. RAG 시스템 초기화
        print("1️⃣ RAG 시스템 초기화 중...\n")
        self.rag = RAGManager(use_openai_embeddings=True)
        print("\n✅ RAG Manager 준비 완료\n")
        
        # 2. 페르소나 로드 (간소화 - 필요한 것만)
        print("2️⃣ 페르소나 지식 로드 중...\n")
        essential_personas = [
            'customer_iphone_to_galaxy',
            'customer_tech_enthusiast',
            'employee_marketer',
        ]
        
        for persona in essential_personas:
            self.rag.load_persona_knowledge(persona)
            print()
        
        print("✅ 페르소나 로드 완료\n")
        
        # 3. 고객 에이전트 초기화
        print("3️⃣ 고객 에이전트 초기화 중...")
        self.customer_agents = CustomerAgents(self.rag)
        print(f"✅ {len(self.customer_agents.agents)}개 고객 에이전트 준비 완료\n")
        
        # 4. 직원 에이전트 초기화
        print("4️⃣ 직원 에이전트 초기화 중...")
        self.employee_agents = EmployeeAgents(self.rag)
        print(f"✅ {len(self.employee_agents.agents)}개 직원 에이전트 준비 완료\n")
        
        # 5. 퍼실리테이터 초기화
        print("5️⃣ 퍼실리테이터 초기화 중...")
        self.facilitator = Facilitator()
        print("✅ 퍼실리테이터 준비 완료\n")
        
        # 6. 투표 시스템 초기화
        print("6️⃣ 투표 시스템 초기화 중...")
        self.voting_system = VotingSystem()
        print("✅ 투표 시스템 준비 완료\n")
        
        # 7. 토론 시스템 초기화
        print("7️⃣ 토론 시스템 초기화 중...")
        self.debate_system = DebateSystem(
            customer_agents=self.customer_agents,
            employee_agents=self.employee_agents,
            facilitator=self.facilitator,
            voting_system=self.voting_system
        )
        print("✅ 토론 시스템 준비 완료\n")
        
        print("="*80)
        print("🎉 모든 시스템 초기화 완료!")
        print("="*80 + "\n")


async def run_simple_debate(manager: DebateSystemManager, topic: str, num_rounds: int = 1):
    """
    간단한 토론 실행
    
    Args:
        manager: 시스템 관리자
        topic: 토론 주제
        num_rounds: 라운드 수
    """
    # 3명만 참여 (빠른 테스트)
    participants = [
        manager.customer_agents.get_agent('iphone_to_galaxy'),
        manager.customer_agents.get_agent('tech_enthusiast'),
        manager.employee_agents.get_agent('marketer'),
    ]
    
    result = await manager.debate_system.run_debate(
        topic=topic,
        num_rounds=num_rounds,
        selected_agents=participants
    )
    
    return result


def test_rag_system(manager: DebateSystemManager):
    """RAG 시스템 테스트"""
    print("\n" + "="*80)
    print("🧪 RAG 시스템 테스트")
    print("="*80 + "\n")
    
    test_queries = [
        ("customer_iphone_to_galaxy", "폴더블이 좋은 이유는?"),
        ("employee_marketer", "어떤 마케팅 전략이 효과적인가요?"),
    ]
    
    for persona, query in test_queries:
        print(f"📋 {persona}")
        print(f"   질문: {query}\n")
        
        contexts = manager.rag.get_context(persona, query, k=2)
        
        if contexts:
            print(f"   검색 결과 ({len(contexts)}개):")
            for i, ctx in enumerate(contexts, 1):
                print(f"   [{i}] {ctx[:150]}...\n")
        else:
            print("   ⚠️ 검색 결과 없음\n")


def test_voting_system(manager: DebateSystemManager):
    """투표 시스템 테스트"""
    print("\n" + "="*80)
    print("🧪 투표 시스템 테스트")
    print("="*80 + "\n")
    
    # 안건 제안
    round_id = manager.voting_system.propose_motion(
        motion_text="Galaxy Fold 7 폴더블 혁신성 평가",
        proposer="facilitator"
    )
    
    # 투표
    votes = [
        ("iPhone전환자", 5, "폴더블 경험이 압도적으로 좋음"),
        ("기술애호가", 4, "기술적으로 인상적이지만 가격이 부담"),
        ("마케터", 5, "차별화 포인트로 충분함"),
    ]
    
    for voter, score, reason in votes:
        manager.voting_system.cast_vote(voter, score, reason, round_id)
    
    # 가중치 (고객 40%, 직원 20%)
    weights = {
        "iPhone전환자": 0.2,  # 고객 1
        "기술애호가": 0.2,    # 고객 2
        "마케터": 0.2,        # 직원
    }
    
    # 결과 계산
    result = manager.voting_system.calculate_result(
        votes=manager.voting_system.voting_history[-1]['votes'],
        weights=weights,
        round_id=round_id
    )
    
    # 결과 표시
    manager.voting_system.display_results(round_id)


def print_menu():
    """메뉴 출력"""
    print("\n" + "="*80)
    print("📋 PersonaBot 메뉴")
    print("="*80 + "\n")
    
    print("1. 빠른 토론 테스트 (3명, 1라운드)")
    print("2. 표준 토론 (3명, 3라운드)")
    print("3. 전체 토론 + 투표 (7명, 3라운드)")
    print("4. 커스텀 토론 (직접 설정)")
    print("5. ---")
    print("6. RAG 시스템 테스트")
    print("7. 투표 시스템 테스트")
    print("8. 종료")
    
    print("\n" + "="*80)


async def main():
    """메인 함수"""
    print("\n")
    print("█████╗ ██████╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗ █████╗ ██████╗  ██████╗ ████████╗")
    print("██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝")
    print("███████║██████╔╝██████╔╝███████╗██║   ██║██╔██╗ ██║███████║██████╔╝██║   ██║   ██║   ")
    print("██╔══██║██╔═══╝ ██╔══██╗╚════██║██║   ██║██║╚██╗██║██╔══██║██╔══██╗██║   ██║   ██║   ")
    print("██║  ██║██║     ██║  ██║███████║╚██████╔╝██║ ╚████║██║  ██║██████╔╝╚██████╔╝   ██║   ")
    print("╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   ")
    print("\n멀티 에이전트 토론 시스템 v2.0 (AutoGen 0.7.x)")
    print("실제 데이터 기반 • RAG 통합 • 가중치 투표\n")
    
    # 시스템 초기화
    try:
        manager = DebateSystemManager()
    except Exception as e:
        print(f"\n❌ 시스템 초기화 실패: {e}")
        return
    
    # 메인 루프
    while True:
        print_menu()
        
        try:
            choice = input("선택하세요 (1-8): ").strip()
            
            if choice == "1":
                # 빠른 테스트
                print("\n🚀 빠른 토론 테스트 시작...\n")
                result = await run_simple_debate(
                    manager,
                    "Galaxy Fold 7의 폴더블 혁신성",
                    num_rounds=1
                )
                
                if result['success']:
                    print(f"\n✅ 토론 완료!")
                    print(f"   참가자: {', '.join(result['participants'])}")
                
            elif choice == "2":
                # 표준 토론
                print("\n🗣️ 표준 토론 시작...\n")
                result = await run_simple_debate(
                    manager,
                    "Galaxy Fold 7의 폴더블 혁신성이 충분한가?",
                    num_rounds=3
                )
                
                if result['success']:
                    print(f"\n✅ 토론 완료!")
                
            elif choice == "3":
                # 전체 토론 + 투표
                print("\n🗳️ 전체 토론 + 투표 시작...\n")
                result = await manager.debate_system.run_full_debate_with_voting(
                    "Galaxy Fold 7 전략 평가",
                    num_rounds=3
                )
                
                if result['success']:
                    print(f"\n✅ 토론 및 투표 완료!")
                    
                    # 결과 저장
                    filename = f"debate_results/debate_{result.get('timestamp', 'unknown')}.json"
                    manager.debate_system.save_debate_result(result, filename)
                
            elif choice == "4":
                # 커스텀 토론
                topic = input("\n토론 주제를 입력하세요: ")
                num_rounds = int(input("라운드 수를 입력하세요 (1-5): "))
                
                result = await run_simple_debate(manager, topic, num_rounds)
                
                if result['success']:
                    print(f"\n✅ 토론 완료!")
                
            elif choice == "6":
                # RAG 테스트
                test_rag_system(manager)
                
            elif choice == "7":
                # 투표 테스트
                test_voting_system(manager)
                
            elif choice == "8":
                # 종료
                print("\n👋 시스템을 종료합니다. 감사합니다!")
                break
                
            else:
                print("\n⚠️ 잘못된 선택입니다. 1-8 사이의 숫자를 입력하세요.")
        
        except KeyboardInterrupt:
            print("\n\n👋 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(main())

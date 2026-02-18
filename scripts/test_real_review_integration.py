#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 리뷰 데이터 시스템 통합 테스트
"""

from rag.real_review_rag_manager import RealReviewRAGManager
from agents.customer_agents_v3 import RealReviewCustomerAgentsV3
import os

# API 키 설정 (환경 변수에서 로드)
from dotenv import load_dotenv
load_dotenv()

def test_real_review_system():
    """실제 리뷰 데이터 시스템 테스트"""
    print("=== Real Review System Integration Test ===")
    
    try:
        # 실제 리뷰 RAG 매니저 초기화
        print("1. Initializing Real Review RAG Manager...")
        real_review_rag = RealReviewRAGManager()
        real_review_rag.load_all_personas_real_reviews()
        
        print(f"   Loaded {len(real_review_rag.retrievers)} persona retrievers")
        
        # 실제 리뷰 고객 에이전트 초기화
        print("2. Creating Real Review Customer Agents...")
        real_review_agents = RealReviewCustomerAgentsV3(real_review_rag, temperature=0.9)
        
        print(f"   Created {len(real_review_agents.get_all_agents())} customer agents")
        
        # 페르소나별 통계 확인
        print("3. Checking persona statistics...")
        stats = real_review_agents.get_persona_stats()
        
        total_reviews = 0
        for persona, stat in stats.items():
            if stat:
                review_count = stat.get('total_reviews', 0)
                total_reviews += review_count
                print(f"   {persona}: {review_count} reviews")
        
        print(f"\nTotal real reviews loaded: {total_reviews}")
        
        # 샘플 검색 테스트
        print("4. Testing sample search...")
        sample_contexts = real_review_rag.get_context('value_seeker', 'price', k=2)
        print(f"   Found {len(sample_contexts)} contexts for 'value_seeker' + 'price'")
        
        if sample_contexts:
            try:
                print(f"   Sample context: {sample_contexts[0][:100]}...")
            except UnicodeEncodeError:
                print(f"   Sample context: [Korean text - encoding issue]")
        
        print("\n✅ Real Review System Integration Test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Real Review System Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_real_review_system()

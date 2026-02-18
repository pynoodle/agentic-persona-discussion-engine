#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 리뷰 데이터 테스트 스크립트
"""

from rag.real_review_rag_manager import RealReviewRAGManager
import os

# API 키 설정 (환경 변수에서 로드)
from dotenv import load_dotenv
load_dotenv()

def test_real_review_data():
    """실제 리뷰 데이터 테스트"""
    print("=== Real Review Data Test ===")
    
    # 실제 리뷰 데이터 로드 테스트
    rag = RealReviewRAGManager()
    review_data = rag.load_real_review_data()
    print(f"Loaded review data keys: {list(review_data.keys())}")
    
    # 페르소나별 분류 테스트
    all_reviews = review_data.get('iphone_reviews', []) + review_data.get('galaxy_reviews', [])
    print(f"Total reviews: {len(all_reviews)}")
    
    # 각 페르소나별 분류 테스트
    personas = ['foldable_enthusiast', 'ecosystem_dilemma', 'value_seeker', 'apple_ecosystem_loyal']
    
    for persona in personas:
        classified_reviews = rag.classify_reviews_by_persona(all_reviews, persona)
        print(f"{persona}: {len(classified_reviews)} reviews")
        
        # 샘플 리뷰 출력 (인코딩 안전)
        if classified_reviews:
            try:
                sample_review = classified_reviews[0]['review'][:100]
                print(f"  Sample: {sample_review}...")
            except UnicodeEncodeError:
                print(f"  Sample: [Korean text - encoding issue]")
        print()

if __name__ == "__main__":
    test_real_review_data()

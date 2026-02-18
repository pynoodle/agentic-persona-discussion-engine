#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순화된 페르소나 분류기
I->G, G->I, I고수, G고수 4개 카테고리로 분류
"""

import json
import os
from typing import Dict, List, Tuple
import re

class SimplePersonaClassifier:
    def __init__(self):
        self.persona_categories = {
            "I_to_G": {
                "name": "iPhone to Galaxy Switcher",
                "keywords": ["아이폰", "갤럭시", "전환", "바꿨", "바꾸", "갤럭시로", "아이폰에서", "스위치", "변경", "폴드", "플립", "삼성", "안드로이드"],
                "sentiment": "positive",
                "description": "Users who switched from iPhone to Galaxy"
            },
            "G_to_I": {
                "name": "Galaxy to iPhone Switcher", 
                "keywords": ["갤럭시", "아이폰", "전환", "바꿨", "바꾸", "아이폰으로", "갤럭시에서", "스위치", "변경", "애플", "ios", "맥"],
                "sentiment": "positive",
                "description": "Users who switched from Galaxy to iPhone"
            },
            "I_loyal": {
                "name": "iPhone Loyal User",
                "keywords": ["아이폰", "애플", "ios", "맥", "에어팟", "워치", "아이패드", "생태계", "충성", "만족", "좋아", "최고", "완벽"],
                "sentiment": "positive", 
                "description": "Loyal iPhone ecosystem users"
            },
            "G_loyal": {
                "name": "Galaxy Loyal User",
                "keywords": ["갤럭시", "삼성", "안드로이드", "폴드", "플립", "충성", "만족", "업그레이드", "정기", "좋아", "최고", "완벽"],
                "sentiment": "positive",
                "description": "Loyal Galaxy ecosystem users"
            }
        }
    
    def classify_review(self, review_text: str) -> Tuple[str, float]:
        """
        리뷰 텍스트를 분석하여 페르소나 카테고리 분류
        Returns: (category, confidence_score)
        """
        review_lower = review_text.lower()
        
        # 각 카테고리별 점수 계산
        scores = {}
        for category, config in self.persona_categories.items():
            score = 0
            keywords = config["keywords"]
            
            # 키워드 매칭 점수 (더 관대한 매칭)
            for keyword in keywords:
                if keyword in review_lower:
                    score += 2  # 가중치 증가
                # 부분 매칭도 고려
                elif any(keyword in word for word in review_lower.split()):
                    score += 1
            
            # 키워드 밀도 계산 (더 낮은 임계값)
            keyword_density = score / len(keywords) if keywords else 0
            scores[category] = keyword_density
        
        # 가장 높은 점수의 카테고리 선택
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        # 최소 신뢰도 임계값을 더 낮게 설정 (0.05)
        if confidence < 0.05:
            return "unknown", confidence
        
        return best_category, confidence
    
    def process_reviews(self, reviews_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        리뷰 데이터를 4개 카테고리로 분류
        """
        classified_reviews = {
            "I_to_G": [],
            "G_to_I": [], 
            "I_loyal": [],
            "G_loyal": []
        }
        
        for review in reviews_data:
            content = review.get('review', '') or review.get('content', '')
            if not content:
                continue
                
            category, confidence = self.classify_review(content)
            
            if category != "unknown" and confidence > 0.05:
                review_with_category = review.copy()
                review_with_category['persona_category'] = category
                review_with_category['confidence'] = confidence
                classified_reviews[category].append(review_with_category)
        
        return classified_reviews
    
    def save_classified_data(self, classified_reviews: Dict[str, List[Dict]], output_dir: str):
        """
        분류된 데이터를 파일로 저장
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for category, reviews in classified_reviews.items():
            if not reviews:
                continue
                
            # 카테고리별 파일 저장
            filename = f"{category}_reviews.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {category}: {len(reviews)} reviews -> {filepath}")
        
        # 전체 통계 저장
        stats = {
            "total_reviews": sum(len(reviews) for reviews in classified_reviews.values()),
            "categories": {
                category: {
                    "count": len(reviews),
                    "description": self.persona_categories[category]["description"]
                }
                for category, reviews in classified_reviews.items()
            }
        }
        
        stats_file = os.path.join(output_dir, "classification_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"Classification stats saved -> {stats_file}")
        return stats

def main():
    """메인 실행 함수"""
    print("Simple Persona Classifier Starting...")
    
    # 기존 리뷰 데이터 로드
    review_files = [
        "data/structured_reviews_20251021_004950.json",
        "data/structured_reviews_20251021_005002.json", 
        "data/structured_reviews_20251021_005316.json"
    ]
    
    all_reviews = []
    for file_path in review_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_reviews.extend(data)
                    elif isinstance(data, dict):
                        # structured_reviews 형식인 경우
                        iphone_reviews = data.get('iphone_reviews', [])
                        galaxy_reviews = data.get('galaxy_reviews', [])
                        all_reviews.extend(iphone_reviews)
                        all_reviews.extend(galaxy_reviews)
                print(f"Loaded {file_path}: {len(data) if isinstance(data, list) else 'structured'} reviews")
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
    
    print(f"Total {len(all_reviews)} reviews loaded")
    
    # 분류기 초기화 및 실행
    classifier = SimplePersonaClassifier()
    classified_reviews = classifier.process_reviews(all_reviews)
    
    # 결과 저장
    output_dir = "simple_chat/data"
    stats = classifier.save_classified_data(classified_reviews, output_dir)
    
    print("\nClassification Results:")
    for category, info in stats["categories"].items():
        print(f"  {category}: {info['count']} reviews - {info['description']}")
    
    print(f"\nTotal {stats['total_reviews']} reviews classified into 4 categories!")

if __name__ == "__main__":
    main()

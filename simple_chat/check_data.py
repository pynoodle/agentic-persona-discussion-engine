#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터 구조 확인 스크립트
"""

import json
import os

def check_data_structure():
    """데이터 구조 확인"""
    file_path = "data/structured_reviews_20251021_004950.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Data keys:", list(data.keys()))
        print("iPhone reviews count:", len(data.get('iphone_reviews', [])))
        print("Galaxy reviews count:", len(data.get('galaxy_reviews', [])))
        
        # 샘플 리뷰 확인
        if data.get('iphone_reviews'):
            sample = data['iphone_reviews'][0]
            print("\nSample iPhone review:")
            print("Keys:", list(sample.keys()))
            print("Content preview:", sample.get('content', '')[:100] + "...")
        
        if data.get('galaxy_reviews'):
            sample = data['galaxy_reviews'][0]
            print("\nSample Galaxy review:")
            print("Keys:", list(sample.keys()))
            print("Content preview:", sample.get('content', '')[:100] + "...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data_structure()


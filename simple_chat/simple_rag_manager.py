#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순화된 페르소나 RAG 매니저 (LangChain 없이 구현)
4개 카테고리 (I->G, G->I, I고수, G고수)를 위한 RAG 시스템
"""

import os
import json
import openai
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class SimplePersonaRAGManager:
    def __init__(self, openai_api_key: str):
        """단순화된 페르소나 RAG 매니저 초기화"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # 페르소나 카테고리 정의
        self.persona_categories = {
            "I_to_G": {
                "name": "iPhone to Galaxy Switcher",
                "description": "iPhone에서 Galaxy로 전환한 사용자들",
                "characteristics": "아이폰에서 갤럭시로 전환한 경험, 전환 이유, 갤럭시의 장점 발견"
            },
            "G_to_I": {
                "name": "Galaxy to iPhone Switcher", 
                "description": "Galaxy에서 iPhone으로 전환한 사용자들",
                "characteristics": "갤럭시에서 아이폰으로 전환한 경험, 전환 이유, 아이폰의 장점 발견"
            },
            "I_loyal": {
                "name": "iPhone Loyal User",
                "description": "iPhone 생태계에 충성하는 사용자들",
                "characteristics": "아이폰 생태계 만족도, 애플 제품들에 대한 충성도, 생태계의 장점"
            },
            "G_loyal": {
                "name": "Galaxy Loyal User",
                "description": "Galaxy 생태계에 충성하는 사용자들",
                "characteristics": "갤럭시 생태계 만족도, 삼성 제품들에 대한 충성도, 생태계의 장점"
            }
        }
        
        # 데이터 저장 경로
        self.data_path = "simple_chat/data"
        self.index_path = "simple_chat/indexes"
        os.makedirs(self.index_path, exist_ok=True)
        
        # 인덱스 저장
        self.text_indexes = {}
        self.vectorizers = {}
        self.documents = {}
    
    def load_persona_data(self, persona_category: str) -> List[Dict]:
        """특정 페르소나 카테고리의 데이터 로드"""
        data_file = f"{self.data_path}/{persona_category}_reviews.json"
        
        if not os.path.exists(data_file):
            print(f"Data file not found: {data_file}")
            return []
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} reviews for {persona_category}")
            return data
        except Exception as e:
            print(f"Error loading data for {persona_category}: {e}")
            return []
    
    def create_text_index(self, persona_category: str) -> bool:
        """특정 페르소나 카테고리에 대한 텍스트 인덱스 생성"""
        print(f"Creating text index for {persona_category}...")
        
        # 데이터 로드
        reviews = self.load_persona_data(persona_category)
        if not reviews:
            return False
        
        # 문서 생성
        documents = []
        for review in reviews:
            content = review.get('review', '') or review.get('content', '')
            if not content or len(content.strip()) < 20:
                continue
            
            # 메타데이터 추가
            metadata = {
                'persona_category': persona_category,
                'review_id': review.get('id', ''),
                'rating': review.get('rating', ''),
                'author': review.get('author', ''),
                'date': review.get('date', ''),
                'sentiment': review.get('sentiment', '')
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        if not documents:
            print(f"No valid documents found for {persona_category}")
            return False
        
        # TF-IDF 벡터화
        texts = [doc['content'] for doc in documents]
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # 한국어는 불용어 제거하지 않음
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 저장
            self.documents[persona_category] = documents
            self.vectorizers[persona_category] = vectorizer
            self.text_indexes[persona_category] = tfidf_matrix
            
            print(f"Text index created for {persona_category}: {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error creating text index for {persona_category}: {e}")
            return False
    
    def load_all_personas(self) -> bool:
        """모든 페르소나 카테고리에 대한 텍스트 인덱스 생성"""
        print("Loading all persona text indexes...")
        
        success_count = 0
        for category in self.persona_categories.keys():
            if self.create_text_index(category):
                success_count += 1
        
        print(f"Successfully loaded {success_count}/{len(self.persona_categories)} persona text indexes")
        return success_count > 0
    
    def get_context(self, persona_category: str, query: str, k: int = 2) -> List[str]:
        """특정 페르소나 카테고리에서 관련 컨텍스트 검색"""
        if persona_category not in self.text_indexes:
            print(f"Text index not found for {persona_category}")
            return []
        
        try:
            # 쿼리 벡터화
            query_vector = self.vectorizers[persona_category].transform([query])
            
            # 코사인 유사도 계산
            similarity_scores = cosine_similarity(
                query_vector, 
                self.text_indexes[persona_category]
            ).flatten()
            
            # 상위 k개 문서 선택
            top_indices = similarity_scores.argsort()[-k:][::-1]
            
            # 컨텍스트 생성
            contexts = []
            for idx in top_indices:
                if similarity_scores[idx] > 0.1:  # 최소 유사도 임계값
                    doc = self.documents[persona_category][idx]
                    context = f"[{self.persona_categories[persona_category]['name']}] {doc['content'][:200]}..."
                    if doc['metadata'].get('author'):
                        context += f" - {doc['metadata']['author']}"
                    contexts.append(context)
            
            return contexts
            
        except Exception as e:
            print(f"Error retrieving context for {persona_category}: {e}")
            return []
    
    def get_persona_info(self, persona_category: str) -> Dict:
        """페르소나 카테고리 정보 반환"""
        return self.persona_categories.get(persona_category, {})
    
    def list_personas(self) -> List[str]:
        """사용 가능한 페르소나 카테고리 목록 반환"""
        return list(self.persona_categories.keys())

def main():
    """테스트 함수"""
    import os
    from dotenv import load_dotenv
    
    # 환경 변수 로드
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("OpenAI API key not found!")
        return
    
    # RAG 매니저 초기화
    rag_manager = SimplePersonaRAGManager(api_key)
    
    # 모든 페르소나 로드
    if rag_manager.load_all_personas():
        print("All persona vector stores loaded successfully!")
        
        # 테스트 검색
        for category in rag_manager.list_personas():
            print(f"\nTesting {category}:")
            contexts = rag_manager.get_context(category, "폴더블 폰 사용 경험")
            for i, context in enumerate(contexts):
                try:
                    print(f"  {i+1}. {context[:100]}...")
                except UnicodeEncodeError:
                    print(f"  {i+1}. [Korean text - encoding issue]")
    else:
        print("Failed to load persona vector stores!")

if __name__ == "__main__":
    main()

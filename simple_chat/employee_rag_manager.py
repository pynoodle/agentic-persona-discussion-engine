#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
임직원 페르소나 RAG 매니저
마케터, 엔지니어, 디자이너 페르소나를 위한 RAG 시스템
"""

import os
import json
import openai
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class EmployeePersonaRAGManager:
    def __init__(self, openai_api_key: str):
        """임직원 페르소나 RAG 매니저 초기화"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # 임직원 페르소나 정의
        self.employee_personas = {
            "marketer": {
                "name": "최지훈 (마케터)",
                "role": "MX사업부 마케팅 총괄 이사",
                "description": "폴더블폰을 주류 시장의 프리미엄 선택지로 편입시키는 마케팅 전략 수립",
                "characteristics": "기술적 우위를 단순하고 임팩트 있는 스토리로 전환, 고객의 선망성 극대화",
                "file": "../rag/data/marketer.txt"
            },
            "engineer": {
                "name": "박준호 (엔지니어)",
                "role": "MX사업부 제품 개발팀 최고 책임자",
                "description": "역대 가장 얇고 가벼운 디자인을 위한 하드웨어 아키텍처 설계",
                "characteristics": "폼팩터 경량화 설계, AP 성능 튜닝 및 열 관리 전문가",
                "file": "../rag/data/eng.txt"
            },
            "designer": {
                "name": "이현서 (디자이너)",
                "role": "MX사업부 디자인 전략 총괄",
                "description": "에센셜 디자인 원칙을 바탕으로 한 라이프스타일 디자인",
                "characteristics": "Simple, Impactful, Emotive의 세 가지 원칙으로 울트라 슬릭 모던 디자인 구현",
                "file": "../rag/data/designer.txt"
            }
        }
        
        # 데이터 저장 경로
        self.data_path = "simple_chat/employee_data"
        os.makedirs(self.data_path, exist_ok=True)
        
        # 인덱스 저장
        self.text_indexes = {}
        self.vectorizers = {}
        self.documents = {}
    
    def load_employee_data(self, persona_type: str) -> str:
        """특정 임직원 페르소나의 데이터 로드"""
        persona_info = self.employee_personas.get(persona_type)
        if not persona_info:
            print(f"Unknown persona type: {persona_type}")
            return ""
        
        file_path = persona_info["file"]
        
        if not os.path.exists(file_path):
            print(f"Data file not found: {file_path}")
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Loaded employee data for {persona_type}: {len(content)} characters")
            return content
        except Exception as e:
            print(f"Error loading data for {persona_type}: {e}")
            return ""
    
    def create_text_index(self, persona_type: str) -> bool:
        """특정 임직원 페르소나에 대한 텍스트 인덱스 생성"""
        print(f"Creating text index for {persona_type}...")
        
        # 데이터 로드
        content = self.load_employee_data(persona_type)
        if not content:
            return False
        
        # 텍스트를 문단 단위로 분할
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 문서 생성
        documents = []
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 50:  # 의미있는 텍스트만 포함
                doc = {
                    'content': paragraph,
                    'metadata': {
                        'persona_type': persona_type,
                        'persona_name': self.employee_personas[persona_type]['name'],
                        'persona_role': self.employee_personas[persona_type]['role'],
                        'paragraph_id': i
                    }
                }
                documents.append(doc)
        
        if not documents:
            print(f"No valid documents found for {persona_type}")
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
            self.documents[persona_type] = documents
            self.vectorizers[persona_type] = vectorizer
            self.text_indexes[persona_type] = tfidf_matrix
            
            print(f"Text index created for {persona_type}: {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error creating text index for {persona_type}: {e}")
            return False
    
    def load_all_personas(self) -> bool:
        """모든 임직원 페르소나에 대한 텍스트 인덱스 생성"""
        print("Loading all employee persona text indexes...")
        
        success_count = 0
        for persona_type in self.employee_personas.keys():
            if self.create_text_index(persona_type):
                success_count += 1
        
        print(f"Successfully loaded {success_count}/{len(self.employee_personas)} employee persona text indexes")
        return success_count > 0
    
    def get_context(self, persona_type: str, query: str, k: int = 2) -> List[str]:
        """특정 임직원 페르소나에서 관련 컨텍스트 검색"""
        if persona_type not in self.text_indexes:
            print(f"Text index not found for {persona_type}")
            return []
        
        try:
            # 쿼리 벡터화
            query_vector = self.vectorizers[persona_type].transform([query])
            
            # 코사인 유사도 계산
            similarity_scores = cosine_similarity(
                query_vector, 
                self.text_indexes[persona_type]
            ).flatten()
            
            # 상위 k개 문서 선택
            top_indices = similarity_scores.argsort()[-k:][::-1]
            
            # 컨텍스트 생성
            contexts = []
            for idx in top_indices:
                if similarity_scores[idx] > 0.1:  # 최소 유사도 임계값
                    doc = self.documents[persona_type][idx]
                    persona_info = self.employee_personas[persona_type]
                    context = f"[{persona_info['name']} - {persona_info['role']}] {doc['content'][:300]}..."
                    contexts.append(context)
            
            return contexts
            
        except Exception as e:
            print(f"Error retrieving context for {persona_type}: {e}")
            return []
    
    def get_persona_info(self, persona_type: str) -> Dict:
        """임직원 페르소나 정보 반환"""
        return self.employee_personas.get(persona_type, {})
    
    def list_personas(self) -> List[str]:
        """사용 가능한 임직원 페르소나 목록 반환"""
        return list(self.employee_personas.keys())

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
    rag_manager = EmployeePersonaRAGManager(api_key)
    
    # 모든 페르소나 로드
    if rag_manager.load_all_personas():
        print("All employee persona vector stores loaded successfully!")
        
        # 테스트 검색
        for persona_type in rag_manager.list_personas():
            print(f"\nTesting {persona_type}:")
            contexts = rag_manager.get_context(persona_type, "폴더블 폰 디자인 전략")
            for i, context in enumerate(contexts):
                try:
                    print(f"  {i+1}. {context[:100]}...")
                except UnicodeEncodeError:
                    print(f"  {i+1}. [Korean text - encoding issue]")
    else:
        print("Failed to load employee persona vector stores!")

if __name__ == "__main__":
    main()

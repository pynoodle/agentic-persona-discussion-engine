#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Review Data RAG Manager - 실제 리뷰 데이터를 페르소나별로 분류하여 RAG로 사용
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def safe_print(msg):
    """Windows 인코딩 오류 방지용 안전한 print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        clean_msg = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean_msg)

class RealReviewRAGManager:
    """실제 리뷰 데이터 기반 RAG 시스템"""
    
    def __init__(self, use_openai_embeddings=True):
        """실제 리뷰 데이터 RAG 관리자 초기화"""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.vector_store_dir = Path(__file__).parent / "vector_stores_real_reviews"
        self.vector_store_dir.mkdir(exist_ok=True)
        
        # OpenAI API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다!")
        
        # OpenAI Embeddings 사용
        try:
            safe_print("[*] OpenAI Embeddings initializing...")
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            safe_print("   - Embeddings: OpenAI text-embedding-ada-002")
        except Exception as e:
            safe_print(f"[!] OpenAI Embeddings 초기화 실패: {e}")
            raise
        
        # 텍스트 분할기 설정 (컨텍스트 길이 제한을 위해 매우 작게)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,  # 300 → 200으로 더 축소
            chunk_overlap=20,  # 30 → 20으로 축소
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
        
        # 페르소나 매핑 정의
        self.persona_mapping = {
            "foldable_enthusiast": {
                "conversion_direction": ["iPhone_to_Galaxy"],
                "conversion_level": ["completed"],
                "keywords": ["폴드", "폴더블", "접기", "펼치기", "Fold", "foldable"],
                "sentiment": ["positive"]
            },
            "ecosystem_dilemma": {
                "conversion_direction": ["iPhone_to_Galaxy"],
                "conversion_level": ["considering_strong", "considering_weak"],
                "keywords": ["생태계", "애플워치", "에어팟", "ecosystem", "watch", "airpods"],
                "sentiment": ["neutral", "negative"]
            },
            "foldable_critical": {
                "conversion_direction": ["iPhone_to_Galaxy"],
                "conversion_level": ["completed"],
                "keywords": ["폴드", "폴더블", "문제", "불만", "Fold", "issue", "problem"],
                "sentiment": ["negative"]
            },
            "value_seeker": {
                "conversion_direction": ["iPhone_to_iPhone", "Galaxy_to_iPhone"],
                "conversion_level": ["completed", "considering_strong"],
                "keywords": ["가성비", "가격", "비용", "value", "price", "cost", "일반", "프로"],
                "sentiment": ["neutral", "positive"]
            },
            "apple_ecosystem_loyal": {
                "conversion_direction": ["iPhone_to_iPhone"],
                "conversion_level": ["completed", "considering_weak"],
                "keywords": ["애플", "생태계", "Apple", "ecosystem", "충성", "loyal"],
                "sentiment": ["positive", "neutral"]
            },
            "design_fatigue": {
                "conversion_direction": ["iPhone_to_iPhone", "iPhone_to_Galaxy"],
                "conversion_level": ["considering_weak", "interested"],
                "keywords": ["디자인", "피로", "똑같", "design", "fatigue", "same", "boring"],
                "sentiment": ["negative", "neutral"]
            },
            "upgrade_cycler": {
                "conversion_direction": ["Galaxy_to_Galaxy", "iPhone_to_iPhone"],
                "conversion_level": ["completed"],
                "keywords": ["업그레이드", "교체", "새로", "upgrade", "new", "replace"],
                "sentiment": ["positive", "neutral"]
            }
        }
        
        # Retriever 저장소
        self.retrievers = {}
        
        safe_print("   - Vector Store: ChromaDB")
    
    def load_real_review_data(self) -> Dict:
        """실제 리뷰 데이터 로드"""
        review_files = list(self.data_dir.glob("structured_reviews_*.json"))
        if not review_files:
            safe_print("[!] 구조화된 리뷰 파일을 찾을 수 없습니다.")
            return {}
        
        # 가장 최신 파일 사용
        latest_file = max(review_files, key=lambda x: x.stat().st_mtime)
        safe_print(f"[*] Loading real review data from {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        safe_print(f"   - iPhone reviews: {len(data.get('iphone_reviews', []))}")
        safe_print(f"   - Galaxy reviews: {len(data.get('galaxy_reviews', []))}")
        
        return data
    
    def classify_reviews_by_persona(self, reviews: List[Dict], persona_name: str) -> List[Dict]:
        """리뷰를 페르소나별로 분류"""
        if persona_name not in self.persona_mapping:
            return []
        
        persona_config = self.persona_mapping[persona_name]
        classified_reviews = []
        
        for review in reviews:
            # 기본 조건 확인
            if review.get('conversion_direction') not in persona_config['conversion_direction']:
                continue
            
            if review.get('conversion_level') not in persona_config['conversion_level']:
                continue
            
            # 키워드 매칭 확인
            review_text = review.get('review', '').lower()
            if persona_config['keywords']:
                keyword_match = any(keyword.lower() in review_text for keyword in persona_config['keywords'])
                if not keyword_match:
                    continue
            
            # 감정 매칭 확인
            if persona_config['sentiment']:
                sentiment = review.get('sentiment', 'neutral')
                if sentiment not in persona_config['sentiment']:
                    continue
            
            classified_reviews.append(review)
        
        return classified_reviews
    
    def create_persona_documents(self, reviews: List[Dict], persona_name: str) -> List[Document]:
        """페르소나별 문서 생성"""
        documents = []
        
        for i, review in enumerate(reviews):
            # 리뷰 텍스트 정리
            review_text = review.get('review', '')
            if not review_text:
                continue
            
            # HTML 태그 제거
            import re
            clean_text = re.sub(r'<[^>]+>', '', review_text)
            clean_text = re.sub(r'&[^;]+;', '', clean_text)
            
            # 메타데이터 추가
            metadata = {
                'persona': persona_name,
                'review_id': review.get('id', f'review_{i}'),
                'author': review.get('author', ''),
                'conversion_direction': review.get('conversion_direction', ''),
                'conversion_level': review.get('conversion_level', ''),
                'sentiment': review.get('sentiment', 'neutral'),
                'language': review.get('language', 'ko'),
                'engagement': review.get('engagement', 0),
                'video_title': review.get('video_title', '')
            }
            
            # 문서 생성
            doc = Document(
                page_content=clean_text,
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    def load_persona_real_reviews(self, persona_name: str) -> Optional[Chroma]:
        """페르소나별 실제 리뷰 데이터 로드 및 벡터화"""
        safe_print(f"[*] Loading real reviews for {persona_name}...")
        
        # 실제 리뷰 데이터 로드
        review_data = self.load_real_review_data()
        if not review_data:
            return None
        
        # 모든 리뷰 수집
        all_reviews = []
        all_reviews.extend(review_data.get('iphone_reviews', []))
        all_reviews.extend(review_data.get('galaxy_reviews', []))
        
        # 페르소나별 분류
        classified_reviews = self.classify_reviews_by_persona(all_reviews, persona_name)
        safe_print(f"   - Classified {len(classified_reviews)} reviews for {persona_name}")
        
        if not classified_reviews:
            safe_print(f"[!] No reviews found for {persona_name}")
            return None
        
        # 문서 생성
        documents = self.create_persona_documents(classified_reviews, persona_name)
        
        # 텍스트 분할
        chunks = self.text_splitter.split_documents(documents)
        safe_print(f"   - Split into {len(chunks)} chunks")
        
        # Vector Store 생성
        vector_store_path = str(self.vector_store_dir / persona_name)
        
        if (self.vector_store_dir / persona_name).exists():
            safe_print(f"   - Loading existing vector store...")
            vector_store = Chroma(
                persist_directory=vector_store_path,
                embedding_function=self.embeddings
            )
        else:
            safe_print(f"   - Creating new vector store...")
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=vector_store_path
            )
            safe_print(f"   - Vector store saved")
        
        # Retriever 생성
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # 상위 5개 관련 리뷰
        )
        self.retrievers[persona_name] = retriever
        
        return vector_store
    
    def load_all_personas_real_reviews(self):
        """모든 페르소나의 실제 리뷰 데이터 로드"""
        safe_print("[*] Loading real review data for all personas...")
        
        for persona_name in self.persona_mapping.keys():
            try:
                self.load_persona_real_reviews(persona_name)
            except Exception as e:
                safe_print(f"[!] Failed to load {persona_name}: {e}")
        
        safe_print(f"[*] Loaded {len(self.retrievers)} persona retrievers")
    
    def clean_review_text(self, text: str) -> str:
        """리뷰 텍스트 정리 - 이상한 문자 제거 (극도로 강화된 버전)"""
        import re
        
        # 기본 정리
        text = text.strip()
        
        # 1. 이상한 문자 패턴 제거 (극도로 강력하게)
        # 모든 특수문자와 이상한 패턴 제거
        text = re.sub(r'[^\w\s가-힣.,!?()[\]{}"\'-]', '', text)
        
        # 2. 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        # 3. 의미없는 짧은 텍스트 제거 (20자 미만)
        if len(text) < 20:
            return ""
        
        # 4. 이상한 패턴 제거 (극도로 강력한 패턴)
        weird_patterns = [
            r'[a-zA-Z]+\s+[가-힣]+',  # 영어+한글 혼합
            r'[가-힣]+\s+[a-zA-Z]+',  # 한글+영어 혼합
            r'[^\w\s가-힣.,!?()[\]{}"\'-]{1,}',  # 연속된 특수문자
            r'\b\w{1,2}\b',  # 1-2글자 단어 제거
            r'[가-힣]{1,2}\s+[가-힣]{1,2}',  # 짧은 한글 조합
            r'[a-zA-Z]{1,3}',  # 짧은 영어 단어 제거
            r'[0-9]+',  # 숫자 제거
            r'[^\w\s가-힣.,!?()[\]{}"\'-]',  # 모든 특수문자 제거
        ]
        
        for pattern in weird_patterns:
            text = re.sub(pattern, '', text)
        
        # 5. 의미있는 문장만 남기기
        sentences = text.split('.')
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            # 더 엄격한 조건: 15자 이상, 특수문자 없음, 의미있는 내용
            if (len(sentence) >= 15 and 
                not re.search(r'[^\w\s가-힣.,!?()[\]{}"\'-]', sentence) and
                len(sentence.split()) >= 3):  # 최소 3개 단어
                clean_sentences.append(sentence)
        
        # 6. 최종 정리
        text = '. '.join(clean_sentences).strip()
        
        # 7. 최종 검증: 20자 이상이고 의미있는 내용인지 확인
        if len(text) >= 20 and len(text.split()) >= 5:
            return text
        else:
            return ""
    
    def get_context(self, persona_name: str, query: str, k: int = 1) -> List[str]:
        """실제 리뷰에서 관련 컨텍스트 검색 (극도로 제한된 컨텍스트)"""
        if persona_name not in self.retrievers:
            safe_print(f"[!] Retriever not found for '{persona_name}'")
            return []
        
        try:
            # Retriever를 사용하여 검색 (1개 문서만 가져옴)
            docs = self.retrievers[persona_name].invoke(query)
            
            # 상위 1개만 반환하고 극도로 제한된 길이
            contexts = []
            total_length = 0
            max_context_length = 300  # 최대 컨텍스트 길이를 300자로 극도 제한
            
            for doc in docs[:1]:  # 1개만 가져옴
                context = f"[실제 사용자 리뷰] {doc.page_content}"
                if doc.metadata.get('author'):
                    context += f" - {doc.metadata['author']}"
                
                # 텍스트 정리 적용
                cleaned_context = self.clean_review_text(context)
                if cleaned_context:  # 정리된 텍스트가 유효한 경우만 추가
                    # 길이 제한 확인
                    if total_length + len(cleaned_context) <= max_context_length:
                        contexts.append(cleaned_context)
                        total_length += len(cleaned_context)
                    else:
                        # 남은 공간에 맞게 잘라서 추가
                        remaining_space = max_context_length - total_length
                        if remaining_space > 50:  # 최소 50자 이상은 남겨야 의미있음
                            contexts.append(cleaned_context[:remaining_space] + "...")
                        break
            
            safe_print(f"[*] '{persona_name}' 컨텍스트 로드: {len(contexts)}개 문서, 총 {total_length}자")
            return contexts
            
        except Exception as e:
            safe_print(f"[!] Search failed for {persona_name}: {e}")
            return []
    
    def get_persona_stats(self, persona_name: str) -> Dict:
        """페르소나별 통계 정보"""
        if persona_name not in self.retrievers:
            return {}
        
        try:
            # 벡터 스토어에서 문서 수 확인
            vector_store_path = str(self.vector_store_dir / persona_name)
            if not (self.vector_store_dir / persona_name).exists():
                return {}
            
            vector_store = Chroma(
                persist_directory=vector_store_path,
                embedding_function=self.embeddings
            )
            
            # 모든 문서 검색하여 통계 생성
            all_docs = vector_store.similarity_search("", k=1000)  # 최대 1000개
            
            stats = {
                'total_reviews': len(all_docs),
                'persona_name': persona_name,
                'conversion_directions': set(),
                'languages': set(),
                'sentiments': set()
            }
            
            for doc in all_docs:
                metadata = doc.metadata
                stats['conversion_directions'].add(metadata.get('conversion_direction', ''))
                stats['languages'].add(metadata.get('language', ''))
                stats['sentiments'].add(metadata.get('sentiment', ''))
            
            # set을 list로 변환
            stats['conversion_directions'] = list(stats['conversion_directions'])
            stats['languages'] = list(stats['languages'])
            stats['sentiments'] = list(stats['sentiments'])
            
            return stats
            
        except Exception as e:
            safe_print(f"[!] Failed to get stats for {persona_name}: {e}")
            return {}

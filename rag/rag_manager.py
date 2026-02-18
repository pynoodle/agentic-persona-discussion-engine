#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Manager - LangChain 기반 페르소나 지식 관리
각 페르소나별 독립적인 벡터스토어와 retriever 생성
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader, DirectoryLoader

def safe_print(msg):
    """Windows 인코딩 오류 방지용 안전한 print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 이모지 제거 후 출력
        import re
        clean_msg = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean_msg)

class RAGManager:
    """페르소나별 RAG 시스템 관리자"""
    
    def __init__(self, use_openai_embeddings=True):
        """
        RAG 관리자 초기화
        
        Args:
            use_openai_embeddings: True면 OpenAI (요구사항), False면 HuggingFace
        """
        self.data_dir = Path(__file__).parent / "data"
        # Use new vector stores with updated content
        self.vector_store_dir = Path(__file__).parent / "vector_stores_new"
        self.vector_store_dir.mkdir(exist_ok=True)
        
        # OpenAI API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다!")
        
        # OpenAI Embeddings 사용 (요구사항)
        try:
            print("[*] OpenAI Embeddings initializing...")
        except:
            pass
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002"
        )
        
        # LLM (OpenAI GPT-4)
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=500
        )
        
        # Text Splitter (요구사항: chunk_size=500, overlap=50)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # 페르소나별 Vector Store & Retriever (LangChain 1.0 - qa_chains 제거)
        self.vector_stores = {}
        self.retrievers = {}
        
        # 페르소나 정의 (실제 데이터 기반)
        self.personas = {
            # 고객 페르소나 (실제 데이터 기반)
            'customer_foldable_enthusiast': '폴더블매력파 (564명, 63.2 좋아요)',
            'customer_ecosystem_dilemma': '생태계딜레마 (37명, 31.0 좋아요)',
            'customer_foldable_critical': '폴더블비판자 (80명, 7.74 좋아요)',
            'customer_upgrade_cycler': '정기업그레이더 (58명, 6.88 좋아요)',
            'customer_value_seeker': '가성비추구자 (8명, 376.75 좋아요)',
            'customer_apple_ecosystem_loyal': 'Apple생태계충성 (79명, 12.56 좋아요)',
            'customer_design_fatigue': '디자인피로 (48명, 11.42 좋아요)',
            
            # 임직원 페르소나 (실제 데이터 기반)
            'employee_marketer': '최지훈 마케터 (MX사업부 마케팅 총괄 이사)',
            'employee_developer': '박준호 엔지니어 (하드웨어 및 성능 최적화 최고 책임자)',
            'employee_designer': '이현서 디자이너 (디자인 전략 총괄 / 리드 디자이너)',
            
            # 제품 정보 (전반적 토론 참고용)
            'product_info': '갤럭시 Z 폴드 7 & Z 플립 7 제품 정보'
        }
        
        try:
            print("[OK] RAG Manager initialized")
            print("   - Embeddings: OpenAI (text-embedding-ada-002)")
            print("   - Chunk Size: 500, Overlap: 50")
            print("   - Vector Store: ChromaDB")
        except:
            pass
    
    def load_persona_knowledge(self, persona_name: str) -> Optional[Chroma]:
        """
        페르소나 지식 로드 및 벡터화
        
        Args:
            persona_name: 페르소나 이름 (예: 'customer_iphone_to_galaxy')
        
        Returns:
            Chroma 벡터 스토어 객체
        """
        file_path = self.data_dir / f"{persona_name}.txt"
        
        if not file_path.exists():
            safe_print(f"[!] {file_path} file not found")
            return None
        
        safe_print(f"[*] Loading {persona_name}.txt...")
        
        # 문서 로드 (TextLoader 사용)
        loader = TextLoader(str(file_path), encoding='utf-8')
        documents = loader.load()
        
        # 텍스트 분할 (요구사항: chunk_size=500, overlap=50)
        chunks = self.text_splitter.split_documents(documents)
        
        safe_print(f"    Split into {len(chunks)} chunks (500 chars/chunk, 50 overlap)")
        
        # Vector Store 생성 (Chroma DB, OpenAI Embeddings)
        vector_store_path = str(self.vector_store_dir / persona_name)
        
        # 기존 벡터 스토어가 있으면 로드, 없으면 생성
        if (self.vector_store_dir / persona_name).exists():
            safe_print(f"    Loading existing vector store...")
            vector_store = Chroma(
                persist_directory=vector_store_path,
                embedding_function=self.embeddings
            )
        else:
            safe_print(f"    Creating new vector store...")
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=vector_store_path
            )
            safe_print(f"    Vector store saved")
        
        # Vector Store 저장
        self.vector_stores[persona_name] = vector_store
        
        # Retriever 생성 (별도 저장)
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Top 3 관련 문서
        )
        self.retrievers[persona_name] = retriever
        
        # QA Chain 생성 (LangChain 1.0 LCEL 방식)
        # RAG Chain을 여기서 생성하지 않고, query_persona에서 생성
        
        safe_print(f"[OK] {self.personas[persona_name]} ready")
        safe_print(f"    - Chunks: {len(chunks)}")
        safe_print(f"    - Retriever: similarity search (k=3)")
        safe_print(f"    - Vector store: {vector_store_path}")
        
        return vector_store
    
    def load_all_personas(self):
        """모든 페르소나 지식 로드"""
        safe_print("\n" + "="*80)
        safe_print("[*] Loading all persona knowledge...")
        safe_print("="*80 + "\n")
        
        for persona_name in self.personas.keys():
            self.load_persona_knowledge(persona_name)
            safe_print("")  # 빈 줄
        
        safe_print("="*80)
        safe_print(f"[OK] Total {len(self.vector_stores)} personas ready")
        safe_print(f"   - Vector Stores: {len(self.vector_stores)}")
        safe_print(f"   - Retrievers: {len(self.retrievers)}")
        safe_print("="*80 + "\n")
    
    def get_context(self, persona_type: str, query: str, k: int = 3) -> List[str]:
        """
        특정 페르소나의 관련 컨텍스트 검색 (요구사항 메서드명)
        
        Args:
            persona_type: 페르소나 타입 (예: 'customer_iphone_to_galaxy')
            query: 검색 질의
            k: 반환할 문서 수
        
        Returns:
            관련 컨텍스트 문자열 리스트
        """
        if persona_type not in self.retrievers:
            safe_print(f"[!] Retriever not found for '{persona_type}'")
            return []
        
        # Retriever를 사용하여 검색 (LangChain 1.0 - invoke 사용)
        docs = self.retrievers[persona_type].invoke(query)
        
        # 상위 k개만 반환
        return [doc.page_content for doc in docs[:k]]
    
    def get_relevant_context(self, persona_name: str, query: str, k: int = 3) -> List[str]:
        """
        특정 페르소나의 관련 컨텍스트 가져오기 (하위 호환성)
        
        Args:
            persona_name: 페르소나 이름
            query: 검색 질의
            k: 반환할 문서 수
        
        Returns:
            관련 컨텍스트 문자열 리스트
        """
        # get_context 호출 (동일 기능)
        return self.get_context(persona_name, query, k)
    
    def query_persona(self, persona_name: str, question: str) -> Dict:
        """
        특정 페르소나에게 질문 (LangChain 1.0 LCEL 방식)
        
        Args:
            persona_name: 페르소나 이름
            question: 질문
        
        Returns:
            답변 및 출처 문서
        """
        if persona_name not in self.retrievers:
            return {
                'persona': persona_name,
                'answer': f"페르소나 '{persona_name}'를 찾을 수 없습니다.",
                'source_documents': []
            }
        
        # 1. Retriever로 관련 문서 검색 (LangChain 1.0 - invoke 사용)
        retriever = self.retrievers[persona_name]
        docs = retriever.invoke(question)
        
        # 2. 컨텍스트 조합
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 3. Prompt 생성 (LangChain 1.0 방식)
        prompt_template = f"""당신은 {self.personas[persona_name]}입니다.
아래 제공된 실제 사용자 데이터를 바탕으로 질문에 답변하세요.
통계와 실제 발언을 근거로 답변하되, 페르소나의 특성을 반영하세요.

[실제 데이터 컨텍스트]
{{context}}

[질문]
{{question}}

[답변 지침]
- 실제 데이터를 근거로 제시
- 통계 수치 활용
- 실제 사용자 발언 인용
- 페르소나 톤 유지

답변:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 4. LCEL Chain 구성
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # 5. Chain 실행
        answer = rag_chain.invoke(question)
        
        return {
            'persona': self.personas[persona_name],
            'answer': answer,
            'source_documents': [
                doc.page_content[:200] + "..." 
                for doc in docs
            ],
            'full_source_documents': docs
        }
    
    def get_retriever(self, persona_name: str):
        """
        특정 페르소나의 retriever 가져오기
        
        Args:
            persona_name: 페르소나 이름
        
        Returns:
            LangChain Retriever 객체
        """
        return self.retrievers.get(persona_name)

# 사용 예시 및 테스트
if __name__ == "__main__":
    print("🚀 RAG Manager 테스트 시작...\n")
    
    # RAG Manager 초기화 (OpenAI Embeddings 사용)
    rag = RAGManager(use_openai_embeddings=True)
    
    # 모든 페르소나 로드
    rag.load_all_personas()
    
    print("\n" + "="*80)
    print("🧪 RAG 시스템 테스트")
    print("="*80 + "\n")
    
    # 테스트 1: get_context() 메서드 테스트
    print("📋 테스트 1: get_context() 메서드")
    print("-"*80)
    
    test_query = "생태계 전환이 어렵지 않았나요?"
    contexts = rag.get_context('customer_iphone_to_galaxy', test_query, k=2)
    
    print(f"질의: {test_query}")
    print(f"페르소나: {rag.personas['customer_iphone_to_galaxy']}")
    print(f"\n검색된 컨텍스트 ({len(contexts)}개):\n")
    for i, context in enumerate(contexts, 1):
        print(f"[{i}] {context[:200]}...\n")
    
    # 테스트 2: query_persona() 메서드 테스트
    print("\n" + "="*80)
    print("📋 테스트 2: query_persona() 메서드")
    print("-"*80 + "\n")
    
    test_questions = [
        ("customer_iphone_to_galaxy", "아이폰에서 갤럭시로 바꾸면 어떤 점이 좋아요?"),
        ("employee_marketer", "iPhone 사용자를 Galaxy로 전환시키는 마케팅 전략은?"),
        ("employee_developer", "폴더블 앱 호환성 문제를 어떻게 해결할 수 있나요?"),
    ]
    
    for persona, question in test_questions:
        print(f"\n{'='*80}")
        print(f"페르소나: {rag.personas[persona]}")
        print(f"질문: {question}")
        print('='*80)
        
        result = rag.query_persona(persona, question)
        print(f"\n💬 답변:\n{result['answer']}")
        print(f"\n📚 출처 문서 수: {len(result['source_documents'])}")
        if result['source_documents']:
            print(f"\n📄 출처 미리보기:")
            for i, doc in enumerate(result['source_documents'][:2], 1):
                print(f"   [{i}] {doc}")
    
    # 테스트 3: Retriever 직접 테스트
    print("\n\n" + "="*80)
    print("📋 테스트 3: Retriever 직접 사용")
    print("-"*80 + "\n")
    
    retriever = rag.get_retriever('employee_designer')
    if retriever:
        query = "디자인 철학은 무엇인가요?"
        docs = retriever.get_relevant_documents(query)
        print(f"질의: {query}")
        print(f"검색된 문서 수: {len(docs)}")
        print(f"\n상위 문서:\n{docs[0].page_content[:300]}...\n")
    
    print("="*80)
    print("✅ 모든 테스트 완료!")
    print("="*80)

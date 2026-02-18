#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
가장 간단한 테스트 - RAG만 테스트
AutoGen 없이 RAG 시스템만 검증
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    sys.exit(1)

print("🧪 간단한 RAG 시스템 테스트\n")
print("="*80)
print("이 테스트는 AutoGen 없이 RAG 시스템만 검증합니다.")
print("="*80 + "\n")

try:
    from rag.rag_manager import RAGManager
    
    print("1️⃣ RAG Manager 초기화 중...\n")
    rag = RAGManager(use_openai_embeddings=True)
    
    print("\n2️⃣ 1개 페르소나만 로드 (빠른 테스트)...\n")
    rag.load_persona_knowledge('customer_iphone_to_galaxy')
    
    print("\n3️⃣ get_context() 메서드 테스트...\n")
    print("-"*80)
    
    query = "폴더블이 좋은 이유는?"
    contexts = rag.get_context('customer_iphone_to_galaxy', query, k=2)
    
    print(f"질의: {query}")
    print(f"검색 결과: {len(contexts)}개 문서\n")
    
    for i, context in enumerate(contexts, 1):
        print(f"[문서 {i}]")
        print(context[:300])
        print("...\n")
    
    print("-"*80)
    print("\n4️⃣ query_persona() 메서드 테스트...\n")
    print("-"*80)
    
    question = "아이폰에서 갤럭시로 바꾸면 어떤 점이 좋아요?"
    result = rag.query_persona('customer_iphone_to_galaxy', question)
    
    print(f"질문: {question}")
    print(f"페르소나: {result['persona']}\n")
    print(f"답변:\n{result['answer']}\n")
    print(f"참조 문서: {len(result['source_documents'])}개")
    
    print("\n" + "="*80)
    print("✅ RAG 시스템 테스트 성공!")
    print("="*80)
    print("\n다음 단계: python test_debate.py (AutoGen 통합 테스트)")
    
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("\n해결 방법:")
    print("pip install langchain langchain-openai langchain-community chromadb")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print(f"오류 타입: {type(e).__name__}")
    
    # 상세 오류 정보
    import traceback
    print("\n상세 오류:")
    traceback.print_exc()
    
    print("\n💡 일반적인 해결 방법:")
    print("1. OpenAI API 키 확인")
    print("2. 인터넷 연결 확인")
    print("3. pip install --upgrade langchain langchain-openai")


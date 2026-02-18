#!/usr/bin/env python3
"""Force refresh all vector stores"""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

# Temporarily modify RAG Manager to force recreate
import rag.rag_manager as rag_module
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

class ForceRefreshRAG:
    """Force refresh RAG with new data"""
    
    def __init__(self):
        self.data_dir = Path("rag/data")
        self.vector_store_dir = Path("rag/vector_stores_new")  # New directory
        self.vector_store_dir.mkdir(exist_ok=True)
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )
        
        self.personas = {
            'customer_iphone_to_galaxy': '아이폰→갤럭시 전환자',
            'customer_galaxy_loyalist': '갤럭시 충성 고객',
            'customer_tech_enthusiast': '기술 애호가',
            'customer_price_conscious': '가격 민감 고객',
            'customer_foldable_enthusiast': '폴더블매력파',
            'customer_ecosystem_dilemma': '생태계딜레마',
            'customer_foldable_critical': '폴더블비판자',
            'customer_upgrade_cycler': '정기업그레이더',
            'customer_value_seeker': '가성비추구자',
            'customer_apple_ecosystem_loyal': 'Apple생태계충성',
            'customer_design_fatigue': '디자인피로',
            'employee_marketer': '마케터',
            'employee_developer': '개발자',
            'employee_designer': '디자이너',
        }
    
    def refresh_all(self):
        """Refresh all personas"""
        for persona_name in self.personas.keys():
            file_path = self.data_dir / f"{persona_name}.txt"
            
            if not file_path.exists():
                print(f"   SKIP: {persona_name} (file not found)")
                continue
            
            print(f"\n   Refreshing: {persona_name}")
            
            try:
                # Load document
                loader = TextLoader(str(file_path), encoding='utf-8')
                docs = loader.load()
                
                # Split
                chunks = self.text_splitter.split_documents(docs)
                print(f"      Chunks: {len(chunks)}")
                
                # Create NEW vector store (force recreate)
                vector_path = str(self.vector_store_dir / persona_name)
                
                vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=vector_path
                )
                
                print(f"      OK: {vector_path}")
            
            except Exception as e:
                print(f"      FAIL: {e}")

print("="*80)
print("Force refreshing all personas...")
print("="*80)

refresher = ForceRefreshRAG()
refresher.refresh_all()

print("\n" + "="*80)
print("Complete!")
print("="*80)
print("\nNow move rag/vector_stores_new to rag/vector_stores")
print("(Close all Python processes first)")


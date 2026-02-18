#!/usr/bin/env python3
"""Refresh updated persona vector stores"""
import sys
import os
import shutil
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from rag.rag_manager import RAGManager

print("Refreshing updated persona vector stores...")
print("="*80)

# Personas that were updated by user
updated_personas = [
    'customer_iphone_to_galaxy',
    'customer_galaxy_loyalist',
    'customer_price_conscious',
    'customer_tech_enthusiast',
    'employee_marketer',
    'employee_developer',
    'employee_designer',
]

# Delete their vector stores
vector_dir = Path("rag/vector_stores")

print("\nDeleting old vector stores...")
for persona in updated_personas:
    persona_dir = vector_dir / persona
    if persona_dir.exists():
        try:
            shutil.rmtree(persona_dir)
            print(f"   Deleted: {persona}")
        except Exception as e:
            print(f"   Failed: {persona} - {e}")

print("\nRecreating vector stores...")
rag = RAGManager()

for persona in updated_personas:
    print(f"\n   Loading: {persona}")
    rag.load_persona_knowledge(persona)

print("\n" + "="*80)
print("Refresh complete!")
print("="*80)


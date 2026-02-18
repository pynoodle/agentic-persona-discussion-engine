#!/usr/bin/env python3
"""Check loaded personas"""
import sys
import os
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from rag.rag_manager import RAGManager

print("Checking personas...")
print("="*80)

rag = RAGManager()
rag.load_all_personas()

print("\n" + "="*80)
print(f"Total loaded: {len(rag.vector_stores)}")
print("="*80)

print("\nAll personas:")
for i, name in enumerate(sorted(rag.vector_stores.keys()), 1):
    kr_name = rag.personas.get(name, name)
    print(f"{i:2d}. {name:40s} -> {kr_name}")

print("\n" + "="*80)

# Check if new personas are there
new_personas = [
    'customer_foldable_enthusiast',
    'customer_ecosystem_dilemma',
    'customer_foldable_critical',
    'customer_upgrade_cycler',
    'customer_value_seeker',
    'customer_apple_ecosystem_loyal',
    'customer_design_fatigue',
]

print("\nNew segmented personas:")
for persona in new_personas:
    status = "OK" if persona in rag.vector_stores else "MISSING"
    print(f"   {status}: {persona}")


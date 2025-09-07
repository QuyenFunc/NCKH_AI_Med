#!/usr/bin/env python3
"""Debug Hybrid Search Issues"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from hybrid_search import get_hybrid_search_engine
from medical_rag_utils import search_medical_symptoms_and_diseases
import time

def debug_hybrid_search():
    """Debug why hybrid search gives worse results"""
    print("🔍 DEBUGGING HYBRID SEARCH ISSUES")
    print("=" * 60)
    
    # Initialize
    hybrid_engine = get_hybrid_search_engine()
    
    test_query = "Tôi bị đau đầu và buồn nôn"
    print(f"🎯 Test Query: '{test_query}'")
    print("-" * 50)
    
    # 1. Test Pure Semantic Search
    print("\n1️⃣ PURE SEMANTIC SEARCH:")
    semantic_results = search_medical_symptoms_and_diseases(test_query, top_k=5)
    for i, result in enumerate(semantic_results, 1):
        entity_name = result['metadata'].get('entity_name', 'Unknown')
        relevance = result['relevance_score']
        print(f"   {i}. {entity_name} (relevance: {relevance:.3f})")
    
    # 2. Test Pure Semantic in Hybrid Engine
    print("\n2️⃣ HYBRID ENGINE - SEMANTIC ONLY:")
    semantic_only = hybrid_engine._semantic_search(test_query, 5)
    for i, result in enumerate(semantic_only, 1):
        entity_name = result['metadata'].get('entity_name', 'Unknown')
        semantic_score = result['semantic_score']
        print(f"   {i}. {entity_name} (semantic: {semantic_score:.3f})")
    
    # 3. Test Pure Keyword Search
    print("\n3️⃣ HYBRID ENGINE - KEYWORD ONLY:")
    keyword_only = hybrid_engine._keyword_search(test_query, 5)
    for i, result in enumerate(keyword_only, 1):
        entity_name = result['metadata'].get('entity_name', 'Unknown')
        bm25_score = result['bm25_score']
        print(f"   {i}. {entity_name} (BM25: {bm25_score:.3f})")
    
    # 4. Test Hybrid with Different Weights
    print("\n4️⃣ HYBRID SEARCH - DIFFERENT WEIGHTS:")
    
    weight_configs = [
        (0.9, 0.1, "90% Semantic"),
        (0.7, 0.3, "70% Semantic"),
        (0.5, 0.5, "50/50"),
        (0.3, 0.7, "30% Semantic"),
        (0.1, 0.9, "10% Semantic")
    ]
    
    for sem_w, key_w, desc in weight_configs:
        print(f"\n   🔧 {desc} (sem:{sem_w}, key:{key_w}):")
        hybrid_results = hybrid_engine.hybrid_search(
            test_query, 
            top_k=3, 
            semantic_weight=sem_w, 
            keyword_weight=key_w
        )
        
        for i, result in enumerate(hybrid_results, 1):
            entity_name = result['metadata'].get('entity_name', 'Unknown')
            hybrid_score = result['hybrid_score']
            semantic_score = result['semantic_score']
            keyword_score = result.get('keyword_score', 0.0)
            medical_boost = result.get('medical_boost', 1.0)
            
            print(f"      {i}. {entity_name}")
            print(f"         Hybrid: {hybrid_score:.3f} | Sem: {semantic_score:.3f} | Key: {keyword_score:.3f} | Boost: {medical_boost:.3f}")
    
    # 5. Detailed Analysis of Top Results
    print("\n5️⃣ DETAILED ANALYSIS:")
    print("-" * 30)
    
    # Get best semantic result
    best_semantic = semantic_results[0] if semantic_results else None
    if best_semantic:
        print(f"✅ Best Semantic: {best_semantic['metadata'].get('entity_name', 'Unknown')}")
        print(f"   Relevance: {best_semantic['relevance_score']:.3f}")
        print(f"   Text snippet: {best_semantic['text'][:100]}...")
    
    # Get best hybrid result  
    best_hybrid_results = hybrid_engine.hybrid_search(test_query, top_k=1)
    best_hybrid = best_hybrid_results[0] if best_hybrid_results else None
    if best_hybrid:
        print(f"\n❌ Best Hybrid: {best_hybrid['metadata'].get('entity_name', 'Unknown')}")
        print(f"   Hybrid Score: {best_hybrid['hybrid_score']:.3f}")
        print(f"   Semantic: {best_hybrid['semantic_score']:.3f}")
        print(f"   Keyword: {best_hybrid.get('keyword_score', 0.0):.3f}")
        print(f"   Medical Boost: {best_hybrid.get('medical_boost', 1.0):.3f}")
        print(f"   Text snippet: {best_hybrid['text'][:100]}...")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS:")
    print("1. Increase semantic weight (0.9+)")
    print("2. Fix medical term boosting")
    print("3. Check BM25 score normalization")
    print("4. Consider removing poor BM25 results")

if __name__ == "__main__":
    debug_hybrid_search()

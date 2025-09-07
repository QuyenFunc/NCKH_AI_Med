#!/usr/bin/env python3
"""
Quick Search Test Runner
Script đơn giản để chạy test search nhanh
"""

import sys
import os
from test_search_comparison import SearchComparison

def quick_benchmark():
    """Chạy benchmark nhanh với 5 queries"""
    
    quick_queries = [
        "đau đầu và chóng mặt",
        "sốt cao kéo dài", 
        "ho khan có máu",
        "đau bụng dưới",
        "khó thở và đau ngực"
    ]
    
    print("⚡ Quick Search Benchmark")
    print(f"📋 Testing {len(quick_queries)} queries")
    print("-" * 50)
    
    comparison = SearchComparison()
    comparison.test_queries = quick_queries  # Override với quick queries
    
    summary = comparison.run_full_comparison(top_k=3)
    comparison.print_summary_report(summary)
    
    return summary

def single_query_test():
    """Test với 1 query do user nhập"""
    
    query = input("🔍 Nhập query để test: ").strip()
    if not query:
        query = "đau đầu và chóng mặt"  # Default
        print(f"📝 Using default query: '{query}'")
    
    print(f"\n🧪 Testing query: '{query}'")
    print("-" * 50)
    
    comparison = SearchComparison()
    result = comparison.run_single_query_test(query, top_k=5)
    
    # Print detailed results
    print(f"\n📊 Detailed Results for: '{query}'")
    for method_name, method_result in result['methods'].items():
        print(f"\n🔧 {method_name.upper()}:")
        if method_result['success']:
            print(f"  ⏱️  Time: {method_result['search_time']:.3f}s")
            print(f"  📊 Results: {method_result['results_count']}")
            if method_result['results']:
                print("  🎯 Top Result:")
                top_result = method_result['results'][0]
                title = top_result.get('title', top_result.get('metadata', {}).get('entity_name', 'Unknown'))
                text = top_result.get('text', '')[:100] + "..."
                print(f"     Title: {title}")
                print(f"     Content: {text}")
        else:
            print(f"  ❌ Error: {method_result['error']}")

def performance_stress_test():
    """Test performance với queries lặp lại"""
    
    test_query = "đau đầu và chóng mặt"
    iterations = 10
    
    print(f"🚀 Performance Stress Test")
    print(f"📋 Query: '{test_query}'")
    print(f"🔄 Iterations: {iterations}")
    print("-" * 50)
    
    comparison = SearchComparison()
    
    method_times = {}
    
    for method_name in ['semantic', 'hybrid', 'parallel', 'fast_hybrid']:
        print(f"\n🧪 Testing {method_name}...")
        times = []
        
        for i in range(iterations):
            if method_name == 'semantic':
                result = comparison.test_semantic_search(test_query)
            elif method_name == 'hybrid':
                result = comparison.test_hybrid_search(test_query)
            elif method_name == 'parallel':
                result = comparison.test_parallel_search(test_query)
            elif method_name == 'fast_hybrid':
                result = comparison.test_fast_hybrid_search(test_query)
            
            if result['success']:
                times.append(result['search_time'])
                print(f"  [{i+1}/{iterations}] {result['search_time']:.3f}s", end='\r')
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            method_times[method_name] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'success_rate': len(times) / iterations
            }
            print(f"  ✅ Avg: {avg_time:.3f}s, Range: {min_time:.3f}s - {max_time:.3f}s")
        else:
            print(f"  ❌ All iterations failed")
    
    # Summary
    print(f"\n📊 Performance Summary:")
    sorted_methods = sorted(method_times.items(), key=lambda x: x[1]['avg'])
    
    for i, (method, stats) in enumerate(sorted_methods, 1):
        print(f"  {i}. {method}: {stats['avg']:.3f}s avg (success: {stats['success_rate']*100:.0f}%)")

def main():
    """Main menu"""
    
    print("🔬 Medical RAG Search Test Suite")
    print("="*40)
    print("1. Quick Benchmark (5 queries)")
    print("2. Single Query Test")
    print("3. Performance Stress Test")
    print("4. Full Comparison Test")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\n🤔 Choose option (1-5): ").strip()
            
            if choice == '1':
                quick_benchmark()
                
            elif choice == '2':
                single_query_test()
                
            elif choice == '3':
                performance_stress_test()
                
            elif choice == '4':
                comparison = SearchComparison()
                summary = comparison.run_full_comparison(top_k=5)
                comparison.print_summary_report(summary)
                
                save = input("\n💾 Save results? (y/n): ").lower().strip()
                if save in ['y', 'yes']:
                    comparison.save_results(summary)
                
            elif choice == '5':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Test interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

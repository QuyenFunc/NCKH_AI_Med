#!/usr/bin/env python3
"""
Test Search Methods Comparison
So sánh hiệu suất các phương pháp tìm kiếm: Semantic, Hybrid, Parallel, Fast Hybrid
"""

import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any

# Import search methods
from medical_rag_utils import search_medical_symptoms_and_diseases
try:
    from hybrid_search import get_hybrid_search_engine
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False
    print("⚠️ Hybrid search not available")

try:
    from async_processor import get_async_processor
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False
    print("⚠️ Parallel search not available")

try:
    from enhanced_search_quality import get_search_quality_enhancer
    ENHANCED_SEARCH_AVAILABLE = True
except ImportError:
    ENHANCED_SEARCH_AVAILABLE = False
    print("⚠️ Enhanced search not available")

class SearchComparison:
    """Class để test và so sánh các phương pháp search"""
    
    def __init__(self):
        self.test_queries = [
            "đau đầu và chóng mặt",
            "sốt cao kéo dài",
            "ho khan có máu",
            "đau bụng dưới bên phải", 
            "khó thở và đau ngực",
            "mệt mỏi kéo dài",
            "buồn nôn và nôn",
            "rối loạn tiêu hóa",
            "cao huyết áp",
            "tiểu đường type 2",
            "viêm phổi",
            "covid-19 triệu chứng",
            "đau khớp gối",
            "mất ngủ",
            "stress và lo âu"
        ]
        
        self.results = {}
        self.setup_search_engines()
    
    def setup_search_engines(self):
        """Khởi tạo các search engines"""
        print("🔧 Initializing search engines...")
        
        # Hybrid Search
        if HYBRID_AVAILABLE:
            try:
                self.hybrid_engine = get_hybrid_search_engine()
                print("✅ Hybrid search engine loaded")
            except Exception as e:
                print(f"❌ Hybrid search failed: {e}")
                self.hybrid_engine = None
        else:
            self.hybrid_engine = None
        
        # Parallel Search  
        if PARALLEL_AVAILABLE:
            try:
                self.parallel_processor = get_async_processor()
                print("✅ Parallel processor loaded")
            except Exception as e:
                print(f"❌ Parallel search failed: {e}")
                self.parallel_processor = None
        else:
            self.parallel_processor = None
        
        # Enhanced Search
        if ENHANCED_SEARCH_AVAILABLE:
            try:
                self.enhanced_search = get_search_quality_enhancer()
                print("✅ Enhanced search loaded")
            except Exception as e:
                print(f"❌ Enhanced search failed: {e}")
                self.enhanced_search = None
        else:
            self.enhanced_search = None
    
    def test_semantic_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Test semantic search (baseline)"""
        start_time = time.time()
        
        try:
            results = search_medical_symptoms_and_diseases(query, top_k=top_k)
            search_time = time.time() - start_time
            
            return {
                'method': 'semantic',
                'success': True,
                'results_count': len(results),
                'search_time': search_time,
                'results': results[:3],  # Top 3 for analysis
                'error': None
            }
            
        except Exception as e:
            return {
                'method': 'semantic', 
                'success': False,
                'results_count': 0,
                'search_time': time.time() - start_time,
                'results': [],
                'error': str(e)
            }
    
    def test_hybrid_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Test hybrid search"""
        start_time = time.time()
        
        if not self.hybrid_engine:
            return {
                'method': 'hybrid',
                'success': False,
                'results_count': 0,
                'search_time': 0,
                'results': [],
                'error': 'Hybrid engine not available'
            }
        
        try:
            results = self.hybrid_engine.hybrid_search(query, top_k=top_k)
            search_time = time.time() - start_time
            
            return {
                'method': 'hybrid',
                'success': True,
                'results_count': len(results),
                'search_time': search_time,
                'results': results[:3],
                'error': None
            }
            
        except Exception as e:
            return {
                'method': 'hybrid',
                'success': False,
                'results_count': 0,
                'search_time': time.time() - start_time,
                'results': [],
                'error': str(e)
            }
    
    def test_parallel_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Test parallel search"""
        start_time = time.time()
        
        if not self.parallel_processor:
            return {
                'method': 'parallel',
                'success': False,
                'results_count': 0,
                'search_time': 0,
                'results': [],
                'error': 'Parallel processor not available'
            }
        
        try:
            # Parallel search với multiple methods
            parallel_results = self.parallel_processor.parallel_search(
                query, 
                search_methods=['semantic', 'keyword'], 
                top_k=top_k
            )
            
            search_time = time.time() - start_time
            
            # Combine results from different methods
            combined_results = []
            if parallel_results.get('semantic'):
                combined_results.extend(parallel_results['semantic'][:3])
            if parallel_results.get('keyword'):
                combined_results.extend(parallel_results['keyword'][:2])
            
            return {
                'method': 'parallel',
                'success': True,
                'results_count': len(combined_results),
                'search_time': search_time,
                'results': combined_results[:3],
                'error': None,
                'breakdown': {
                    'semantic_count': len(parallel_results.get('semantic', [])),
                    'keyword_count': len(parallel_results.get('keyword', []))
                }
            }
            
        except Exception as e:
            return {
                'method': 'parallel',
                'success': False,
                'results_count': 0,
                'search_time': time.time() - start_time,
                'results': [],
                'error': str(e)
            }
    
    def test_fast_hybrid_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Test fast hybrid search (enhanced)"""
        start_time = time.time()
        
        if not self.enhanced_search:
            return {
                'method': 'fast_hybrid',
                'success': False,
                'results_count': 0,
                'search_time': 0,
                'results': [],
                'error': 'Enhanced search not available'
            }
        
        try:
            results = self.enhanced_search.enhanced_search(query, top_k=top_k)
            search_time = time.time() - start_time
            
            return {
                'method': 'fast_hybrid',
                'success': True,
                'results_count': len(results),
                'search_time': search_time,
                'results': results[:3],
                'error': None
            }
            
        except Exception as e:
            return {
                'method': 'fast_hybrid',
                'success': False,
                'results_count': 0,
                'search_time': time.time() - start_time,
                'results': [],
                'error': str(e)
            }
    
    def run_single_query_test(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Test single query với tất cả methods"""
        print(f"\n🔍 Testing query: '{query}'")
        
        query_results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'methods': {}
        }
        
        # Test semantic search
        semantic_result = self.test_semantic_search(query, top_k)
        query_results['methods']['semantic'] = semantic_result
        print(f"  📊 Semantic: {semantic_result['results_count']} results in {semantic_result['search_time']:.3f}s")
        
        # Test hybrid search
        hybrid_result = self.test_hybrid_search(query, top_k)
        query_results['methods']['hybrid'] = hybrid_result
        if hybrid_result['success']:
            print(f"  🔄 Hybrid: {hybrid_result['results_count']} results in {hybrid_result['search_time']:.3f}s")
        else:
            print(f"  ❌ Hybrid: {hybrid_result['error']}")
        
        # Test parallel search
        parallel_result = self.test_parallel_search(query, top_k)
        query_results['methods']['parallel'] = parallel_result
        if parallel_result['success']:
            print(f"  ⚡ Parallel: {parallel_result['results_count']} results in {parallel_result['search_time']:.3f}s")
        else:
            print(f"  ❌ Parallel: {parallel_result['error']}")
        
        # Test fast hybrid search
        fast_hybrid_result = self.test_fast_hybrid_search(query, top_k)
        query_results['methods']['fast_hybrid'] = fast_hybrid_result
        if fast_hybrid_result['success']:
            print(f"  🚀 Fast Hybrid: {fast_hybrid_result['results_count']} results in {fast_hybrid_result['search_time']:.3f}s")
        else:
            print(f"  ❌ Fast Hybrid: {fast_hybrid_result['error']}")
        
        return query_results
    
    def run_full_comparison(self, top_k: int = 5) -> Dict[str, Any]:
        """Chạy test toàn bộ với tất cả queries"""
        print("🚀 Starting Full Search Comparison Test")
        print(f"📋 Testing {len(self.test_queries)} queries with top_k={top_k}")
        print("-" * 60)
        
        all_results = []
        method_stats = {
            'semantic': {'times': [], 'success_count': 0, 'total_results': 0},
            'hybrid': {'times': [], 'success_count': 0, 'total_results': 0},
            'parallel': {'times': [], 'success_count': 0, 'total_results': 0},
            'fast_hybrid': {'times': [], 'success_count': 0, 'total_results': 0}
        }
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n[{i}/{len(self.test_queries)}]", end="")
            query_result = self.run_single_query_test(query, top_k)
            all_results.append(query_result)
            
            # Collect stats
            for method_name, method_result in query_result['methods'].items():
                if method_result['success']:
                    method_stats[method_name]['times'].append(method_result['search_time'])
                    method_stats[method_name]['success_count'] += 1
                    method_stats[method_name]['total_results'] += method_result['results_count']
        
        # Calculate statistics
        summary = {
            'test_info': {
                'total_queries': len(self.test_queries),
                'top_k': top_k,
                'timestamp': datetime.now().isoformat()
            },
            'method_stats': {},
            'detailed_results': all_results
        }
        
        for method_name, stats in method_stats.items():
            if stats['times']:
                summary['method_stats'][method_name] = {
                    'success_rate': stats['success_count'] / len(self.test_queries),
                    'avg_time': statistics.mean(stats['times']),
                    'min_time': min(stats['times']),
                    'max_time': max(stats['times']),
                    'median_time': statistics.median(stats['times']),
                    'total_results': stats['total_results'],
                    'avg_results_per_query': stats['total_results'] / max(stats['success_count'], 1)
                }
            else:
                summary['method_stats'][method_name] = {
                    'success_rate': 0,
                    'avg_time': 0,
                    'error': 'No successful queries'
                }
        
        return summary
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """In báo cáo tóm tắt"""
        print("\n" + "="*80)
        print("📊 SEARCH METHODS COMPARISON REPORT")
        print("="*80)
        
        print(f"\n📋 Test Info:")
        print(f"  • Total Queries: {summary['test_info']['total_queries']}")
        print(f"  • Results per Query: {summary['test_info']['top_k']}")
        print(f"  • Test Time: {summary['test_info']['timestamp']}")
        
        print(f"\n🏆 Performance Ranking:")
        
        # Sort methods by average time
        sorted_methods = []
        for method_name, stats in summary['method_stats'].items():
            if 'avg_time' in stats and stats['success_rate'] > 0:
                sorted_methods.append((method_name, stats))
        
        sorted_methods.sort(key=lambda x: x[1]['avg_time'])
        
        for i, (method_name, stats) in enumerate(sorted_methods, 1):
            print(f"\n  {i}. {method_name.upper()}")
            print(f"     ⚡ Avg Time: {stats['avg_time']:.3f}s")
            print(f"     ✅ Success Rate: {stats['success_rate']*100:.1f}%")
            print(f"     📊 Avg Results: {stats['avg_results_per_query']:.1f}")
            print(f"     ⏱️  Range: {stats['min_time']:.3f}s - {stats['max_time']:.3f}s")
        
        # Failed methods
        failed_methods = [name for name, stats in summary['method_stats'].items() 
                         if stats['success_rate'] == 0]
        
        if failed_methods:
            print(f"\n❌ Failed Methods: {', '.join(failed_methods)}")
        
        print("\n" + "="*80)
    
    def save_results(self, summary: Dict[str, Any], filename: str = None):
        """Lưu kết quả ra file JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_comparison_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")

def main():
    """Main function để chạy test"""
    print("🔬 Medical Search Methods Comparison Test")
    print("Testing: Semantic, Hybrid, Parallel, Fast Hybrid Search")
    
    # Initialize test
    comparison = SearchComparison()
    
    # Run quick test với 1 query
    print("\n🧪 Quick Test with single query:")
    quick_result = comparison.run_single_query_test("đau đầu và chóng mặt", top_k=5)
    
    # Ask user for full test
    print("\n" + "-"*50)
    user_input = input("🤔 Run full comparison test with all queries? (y/n): ").lower().strip()
    
    if user_input in ['y', 'yes', '1', 'ok']:
        # Run full test
        summary = comparison.run_full_comparison(top_k=5)
        
        # Print report
        comparison.print_summary_report(summary)
        
        # Save results
        save_input = input("\n💾 Save detailed results to JSON file? (y/n): ").lower().strip()
        if save_input in ['y', 'yes', '1', 'ok']:
            comparison.save_results(summary)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()

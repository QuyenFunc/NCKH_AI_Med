#!/usr/bin/env python3
"""Test AI Integration với OpenRouter DeepSeek"""
import requests
import json
import time

def test_ai_chatbot():
    """Test AI-powered chatbot"""
    
    print("🤖 TESTING AI-POWERED MEDICAL CHATBOT")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test queries với different intents
    test_queries = [
        {
            'query': 'Tôi bị đau đầu và chóng mặt, có nguy hiểm không?',
            'expected_intent': 'symptom_analysis',
            'description': 'Symptom analysis query'
        },
        {
            'query': 'Tiểu đường type 2 có triệu chứng gì?',
            'expected_intent': 'disease_inquiry', 
            'description': 'Disease inquiry query'
        },
        {
            'query': 'Tôi bị đau ngực và khó thở nghiêm trọng',
            'expected_intent': 'emergency',
            'description': 'Emergency query'
        },
        {
            'query': 'Cách điều trị cao huyết áp hiệu quả?',
            'expected_intent': 'treatment_advice',
            'description': 'Treatment advice query'
        }
    ]
    
    session_id = "test_ai_session"
    
    print("🧪 Testing AI Intent Classification & Response Generation...")
    print()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"📝 Test {i}: {test_case['description']}")
        print(f"   Query: {test_case['query']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(f'{base_url}/chat', 
                                   json={
                                       'query': test_case['query'],
                                       'session_id': session_id
                                   },
                                   timeout=15)
            
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Response time: {total_time:.2f}s")
                print(f"   🎭 Intent: {result.get('intent', 'unknown')}")
                print(f"   🤖 AI Generated: {result.get('ai_generated', False)}")
                print(f"   🧠 AI Model: {result.get('ai_model', 'unknown')}")
                print(f"   📊 Confidence: {result.get('confidence', 0):.2f}")
                print(f"   🚨 Urgency: {result.get('urgency_level', 'unknown')}")
                print(f"   🔑 Key Entities: {result.get('key_entities', [])}")
                
                # Show response preview
                response_preview = result.get('response', '')[:150] + '...' if len(result.get('response', '')) > 150 else result.get('response', '')
                print(f"   💬 Response: {response_preview}")
                
                # Performance check
                if total_time < 3.0:
                    print(f"   🎯 Performance: EXCELLENT (<3s)")
                elif total_time < 5.0:
                    print(f"   ⚡ Performance: GOOD (<5s)")
                else:
                    print(f"   ⚠️ Performance: SLOW (>5s)")
                
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test AI stats endpoint
    print("📊 TESTING AI STATISTICS")
    print("-" * 40)
    
    try:
        stats_response = requests.get(f'{base_url}/ai_stats', timeout=5)
        
        if stats_response.status_code == 200:
            ai_stats = stats_response.json()
            
            print(f"🤖 AI Service Status: {ai_stats.get('status', 'unknown')}")
            print(f"📈 Total Requests: {ai_stats.get('total_requests', 0)}")
            print(f"🎭 Intent Classifications: {ai_stats.get('intent_classifications', 0)}")
            print(f"💬 Response Generations: {ai_stats.get('response_generations', 0)}")
            print(f"⏱️ Avg Response Time: {ai_stats.get('avg_response_time', 0):.2f}s")
            print(f"❌ Error Rate: {ai_stats.get('error_rate', 0)*100:.1f}%")
            print(f"🧠 Model: {ai_stats.get('model', 'unknown')}")
            
        else:
            print(f"❌ AI Stats not available: HTTP {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ AI Stats error: {e}")
    
    print()
    
    # Test performance stats
    print("📊 TESTING PERFORMANCE STATISTICS") 
    print("-" * 40)
    
    try:
        perf_response = requests.get(f'{base_url}/performance_stats', timeout=5)
        
        if perf_response.status_code == 200:
            perf_stats = perf_response.json()
            
            ultra_perf = perf_stats.get('ultra_fast_performance', {})
            systems = perf_stats.get('systems_available', {})
            
            print(f"🎯 Sub-3s Success Rate: {ultra_perf.get('sub_3s_success_rate', 0)*100:.1f}%")
            print(f"⏱️ Avg Total Time: {ultra_perf.get('avg_total_time', 0):.2f}s")
            print(f"🏆 Performance Grade: {ultra_perf.get('performance_grade', 'unknown')}")
            print(f"💾 Cache Hit Rate: {perf_stats.get('cache_hit_rate', 0)*100:.1f}%")
            
            print("\n🚀 Active Systems:")
            for system, active in systems.items():
                status = "✅" if active else "❌"
                print(f"   {status} {system}")
            
            print(f"\n💡 Performance Insights:")
            for insight in perf_stats.get('performance_insights', []):
                print(f"   {insight}")
                
        else:
            print(f"❌ Performance stats not available: HTTP {perf_response.status_code}")
            
    except Exception as e:
        print(f"❌ Performance stats error: {e}")
    
    print()
    print("🎉 AI INTEGRATION TEST COMPLETE!")

if __name__ == "__main__":
    print("🚀 AI Integration Tester")
    print("Make sure the enhanced chatbot is running on http://localhost:5001")
    print()
    
    # Check if server is running
    try:
        health_response = requests.get('http://localhost:5001/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running!")
            test_ai_chatbot()
        else:
            print("❌ Server health check failed")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the enhanced chatbot first:")
        print("   python medical_chatbot_enhanced.py")
    
    except Exception as e:
        print(f"❌ Error: {e}")

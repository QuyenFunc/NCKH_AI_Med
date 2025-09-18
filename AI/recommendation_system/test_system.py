#!/usr/bin/env python3
"""
Test script for Health Content Recommendation System
"""

import asyncio
import json
import time
from datetime import datetime

from openrouter_client import OpenRouterClient, UserProfile
from background_processor import (
    start_background_processor,
    stop_background_processor, 
    queue_user_profile_analysis,
    get_user_content_recommendations
)
from content_matcher import ContentMatcher

async def test_openrouter_integration():
    """Test OpenRouter API integration"""
    print("\n🧠 Testing OpenRouter Integration...")
    
    client = OpenRouterClient()
    
    # Test profile
    profile = UserProfile(
        user_id="test_user_001",
        age=45,
        gender="female",
        height=165,
        weight=75,
        medical_history=["hypertension", "diabetes"],
        allergies=["penicillin"],
        lifestyle={
            "exercise": "moderate",
            "smoking": "no",
            "alcohol": "occasional",
            "diet": "balanced"
        },
        health_goals=["manage diabetes", "lose weight", "improve heart health"]
    )
    
    try:
        recommendations = await client.analyze_user_profile(profile)
        
        print(f"✅ Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec.category} (Priority: {rec.priority})")
            print(f"      Topics: {', '.join(rec.topics[:3])}...")
            print(f"      Reasoning: {rec.reasoning[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter test failed: {e}")
        return False

def test_background_processor():
    """Test background processing system"""
    print("\n🔄 Testing Background Processor...")
    
    # Start processor
    start_background_processor()
    print("✅ Background processor started")
    
    # Test profile data
    profile_data = {
        'age': 32,
        'gender': 'male',
        'height': 180,
        'weight': 85,
        'medical_history': ['high cholesterol'],
        'lifestyle': {
            'exercise': 'light',
            'smoking': 'no',
            'alcohol': 'moderate'
        },
        'health_goals': ['improve fitness', 'lower cholesterol']
    }
    
    # Queue analysis
    user_id = "test_user_002"
    job_id = queue_user_profile_analysis(user_id, profile_data)
    
    if job_id:
        print(f"✅ Queued analysis job: {job_id}")
        
        # Wait for processing
        print("⏳ Waiting for background processing...")
        time.sleep(8)
        
        # Check results
        recommendations = get_user_content_recommendations(user_id)
        
        if recommendations:
            print(f"✅ Found {len(recommendations)} recommendations:")
            for rec in recommendations:
                print(f"   - {rec['category']} (Priority: {rec['priority']})")
        else:
            print("❌ No recommendations found after processing")
            return False
    else:
        print("✅ Analysis skipped (no profile changes)")
    
    # Stop processor
    stop_background_processor()
    print("✅ Background processor stopped")
    
    return True

def test_content_matcher():
    """Test content matching system"""
    print("\n🎯 Testing Content Matcher...")
    
    matcher = ContentMatcher()
    
    # Sample recommendations
    recommendations = [
        {
            'category': 'Heart Health',
            'priority': 1,
            'keywords': ['cardiovascular', 'heart', 'blood pressure', 'cholesterol'],
            'reasoning': 'User has high cholesterol and wants to improve heart health'
        },
        {
            'category': 'Exercise & Fitness',
            'priority': 2,
            'keywords': ['fitness', 'exercise', 'workout', 'cardio'],
            'reasoning': 'User wants to improve fitness level'
        },
        {
            'category': 'Nutrition',
            'priority': 2,
            'keywords': ['diet', 'nutrition', 'cholesterol', 'healthy eating'],
            'reasoning': 'User needs dietary guidance for cholesterol management'
        }
    ]
    
    # Get personalized articles
    user_id = "test_user_003"
    articles = matcher.get_personalized_articles(user_id, recommendations, limit=10)
    
    if articles:
        print(f"✅ Found {len(articles)} personalized articles:")
        for article in articles[:5]:  # Show first 5
            print(f"   📄 {article['title']}")
            print(f"      Category: {article['category']}")
            print(f"      Match Score: {article['match_score']:.2f}")
            print(f"      Source: {article['source']}")
            print()
        
        # Test trending articles
        trending = matcher.get_trending_articles(limit=5)
        print(f"✅ Found {len(trending)} trending articles:")
        for article in trending:
            print(f"   📈 {article['title']} (Views: {article['view_count']})")
        
        return True
    else:
        print("❌ No articles found")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    import requests
    import threading
    import time
    
    # Start API server in background
    from api_server import app
    
    def run_server():
        app.run(host='127.0.0.1', port=5003, debug=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    base_url = "http://127.0.0.1:5003"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test profile analysis
        profile_data = {
            "user_id": "test_api_user",
            "profile": {
                "age": 28,
                "gender": "female",
                "height": 160,
                "weight": 65,
                "medical_history": [],
                "lifestyle": {
                    "exercise": "regular",
                    "smoking": "no"
                },
                "health_goals": ["maintain fitness", "preventive care"]
            }
        }
        
        response = requests.post(
            f"{base_url}/recommendations/analyze-profile",
            json=profile_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Profile analysis queued: {result.get('message')}")
        else:
            print(f"❌ Profile analysis failed: {response.status_code}")
            return False
        
        # Test trending articles
        response = requests.get(f"{base_url}/recommendations/trending?limit=3")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Trending articles: {result['total_articles']} found")
        else:
            print(f"❌ Trending articles failed: {response.status_code}")
            return False
        
        # Test categories
        response = requests.get(f"{base_url}/recommendations/categories")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Categories endpoint: {len(result['categories'])} categories")
        else:
            print(f"❌ Categories failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🧪 Health Content Recommendation System - Comprehensive Test")
    print("=" * 60)
    
    results = []
    
    # Test OpenRouter integration
    openrouter_ok = await test_openrouter_integration()
    results.append(("OpenRouter Integration", openrouter_ok))
    
    # Test background processor
    processor_ok = test_background_processor()
    results.append(("Background Processor", processor_ok))
    
    # Test content matcher
    matcher_ok = test_content_matcher()
    results.append(("Content Matcher", matcher_ok))
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    results.append(("API Endpoints", api_ok))
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 40)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    
    if all_passed:
        print("🎉 All tests PASSED! System is ready for integration.")
    else:
        print("⚠️  Some tests FAILED. Please check the logs above.")
    
    print(f"\n📈 System Overview:")
    print(f"   🧠 AI Analysis: OpenRouter API")
    print(f"   🔄 Background Jobs: SQLite + Threading")
    print(f"   🎯 Content Matching: Keyword + Category matching")
    print(f"   🌐 API Server: Flask on port 5002")
    print(f"   📊 Database: SQLite (recommendations.db, health_content.db)")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())

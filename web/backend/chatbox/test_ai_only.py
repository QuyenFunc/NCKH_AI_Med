#!/usr/bin/env python3
"""Test AI Service only"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_service import get_medical_ai_service

def test_ai_service():
    print("🤖 Testing AI Service directly...")
    
    ai_service = get_medical_ai_service()
    
    test_query = "Tôi bị đau đầu và chóng mặt"
    
    print(f"Query: {test_query}")
    
    try:
        result = ai_service.classify_intent_with_ai(test_query)
        print(f"✅ AI Intent result: {result}")
        
    except Exception as e:
        print(f"❌ AI Intent failed: {e}")
    
    # Test response generation
    mock_search_results = [
        {
            'text': 'Đau đầu có thể do nhiều nguyên nhân như stress, thiếu ngủ, hoặc các bệnh lý nghiêm trọng hơn.',
            'metadata': {'entity_name': 'Headache', 'entity_code': 'MB23.0'}
        }
    ]
    
    mock_intent_info = {
        'intent': 'symptom_analysis',
        'confidence': 0.8,
        'key_entities': ['đau đầu', 'chóng mặt'],
        'urgency_level': 'medium'
    }
    
    try:
        response = ai_service.generate_medical_response(
            test_query, mock_search_results, mock_intent_info
        )
        print(f"✅ AI Response result: {response['ai_generated']}")
        print(f"Response preview: {response['response'][:200]}...")
        
    except Exception as e:
        print(f"❌ AI Response failed: {e}")

if __name__ == "__main__":
    test_ai_service()

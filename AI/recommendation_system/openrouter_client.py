#!/usr/bin/env python3
"""
OpenRouter API Client for Health Content Recommendation
Analyzes user profiles and recommends personalized health content
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    medical_history: List[str] = None
    allergies: List[str] = None
    current_medications: List[str] = None
    lifestyle: Dict[str, str] = None
    health_goals: List[str] = None
    
    def __post_init__(self):
        if self.medical_history is None:
            self.medical_history = []
        if self.allergies is None:
            self.allergies = []
        if self.current_medications is None:
            self.current_medications = []
        if self.lifestyle is None:
            self.lifestyle = {}
        if self.health_goals is None:
            self.health_goals = []

@dataclass
class ContentRecommendation:
    """Recommended content structure"""
    category: str
    priority: int  # 1-5, 1 = highest priority
    topics: List[str]
    reasoning: str
    keywords: List[str]

class OpenRouterClient:
    """OpenRouter API client for health content analysis"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY', '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')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "anthropic/claude-3.5-sonnet"  # High-quality model for analysis
        
    async def analyze_user_profile(self, profile: UserProfile) -> List[ContentRecommendation]:
        """
        Analyze user profile and generate content recommendations
        """
        try:
            prompt = self._create_analysis_prompt(profile)
            
            async with aiohttp.ClientSession() as session:
                response = await self._call_openrouter(session, prompt)
                
            recommendations = self._parse_recommendations(response)
            return recommendations
            
        except Exception as e:
            print(f"Error analyzing profile for user {profile.user_id}: {e}")
            return self._get_fallback_recommendations()
    
    def _create_analysis_prompt(self, profile: UserProfile) -> str:
        """Create analysis prompt for OpenRouter"""
        
        # Calculate BMI if possible
        bmi_info = ""
        if profile.height and profile.weight:
            bmi = profile.weight / ((profile.height / 100) ** 2)
            bmi_info = f"BMI: {bmi:.1f}"
            if bmi < 18.5:
                bmi_info += " (Underweight)"
            elif bmi < 25:
                bmi_info += " (Normal)"
            elif bmi < 30:
                bmi_info += " (Overweight)"
            else:
                bmi_info += " (Obese)"
        
        prompt = f"""
        You are a medical content recommendation expert. Analyze this user's health profile and recommend 5-7 categories of educational health content that would be most beneficial for them.

        USER PROFILE:
        - Age: {profile.age or 'Not specified'}
        - Gender: {profile.gender or 'Not specified'}
        - {bmi_info}
        - Medical History: {', '.join(profile.medical_history) if profile.medical_history else 'None specified'}
        - Allergies: {', '.join(profile.allergies) if profile.allergies else 'None specified'}
        - Current Medications: {', '.join(profile.current_medications) if profile.current_medications else 'None specified'}
        - Lifestyle: {json.dumps(profile.lifestyle) if profile.lifestyle else 'Not specified'}
        - Health Goals: {', '.join(profile.health_goals) if profile.health_goals else 'Not specified'}

        Please recommend content categories in this EXACT JSON format:
        {{
            "recommendations": [
                {{
                    "category": "Category Name",
                    "priority": 1-5,
                    "topics": ["topic1", "topic2", "topic3"],
                    "reasoning": "Why this is important for this user",
                    "keywords": ["keyword1", "keyword2", "keyword3"]
                }}
            ]
        }}

        Focus on:
        1. PREVENTION and long-term health maintenance
        2. AGE-APPROPRIATE content
        3. CONDITION-SPECIFIC guidance if medical history exists
        4. LIFESTYLE optimization
        5. EDUCATIONAL content, not news or current events

        Categories to consider:
        - Heart Health & Cardiovascular
        - Nutrition & Diet
        - Exercise & Fitness
        - Mental Health & Stress Management
        - Preventive Care & Screening
        - Sleep & Recovery
        - Women's/Men's Health (gender-specific)
        - Age-specific Health (pediatric, adult, senior)
        - Chronic Disease Management
        - Weight Management
        - Bone & Joint Health
        - Immune System Support

        Prioritize based on:
        - Age-related health risks
        - Existing medical conditions
        - Lifestyle factors
        - Gender-specific health needs
        - BMI and weight status
        """
        
        return prompt
    
    async def _call_openrouter(self, session: aiohttp.ClientSession, prompt: str) -> str:
        """Make API call to OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:3000",  # Optional
            "X-Title": "Health Content Recommendation System"  # Optional
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent results
            "max_tokens": 2000
        }
        
        async with session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_text = await response.text()
                raise Exception(f"OpenRouter API error {response.status}: {error_text}")
    
    def _parse_recommendations(self, response: str) -> List[ContentRecommendation]:
        """Parse OpenRouter response into ContentRecommendation objects"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            recommendations = []
            for item in data.get("recommendations", []):
                rec = ContentRecommendation(
                    category=item.get("category", "General Health"),
                    priority=item.get("priority", 3),
                    topics=item.get("topics", []),
                    reasoning=item.get("reasoning", ""),
                    keywords=item.get("keywords", [])
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            print(f"Error parsing recommendations: {e}")
            return self._get_fallback_recommendations()
    
    def _get_fallback_recommendations(self) -> List[ContentRecommendation]:
        """Fallback recommendations if AI analysis fails"""
        return [
            ContentRecommendation(
                category="General Health & Wellness",
                priority=1,
                topics=["healthy lifestyle", "preventive care", "nutrition basics"],
                reasoning="Essential health information for everyone",
                keywords=["health", "wellness", "prevention", "nutrition"]
            ),
            ContentRecommendation(
                category="Heart Health",
                priority=2,
                topics=["cardiovascular health", "heart disease prevention", "cholesterol management"],
                reasoning="Heart disease is a leading health concern",
                keywords=["heart", "cardiovascular", "cholesterol", "blood pressure"]
            ),
            ContentRecommendation(
                category="Mental Health",
                priority=2,
                topics=["stress management", "mental wellness", "mindfulness"],
                reasoning="Mental health is crucial for overall wellbeing",
                keywords=["mental health", "stress", "anxiety", "mindfulness"]
            )
        ]

# Test function
async def test_openrouter_client():
    """Test the OpenRouter client"""
    client = OpenRouterClient()
    
    # Test profile
    profile = UserProfile(
        user_id="test_user",
        age=35,
        gender="female",
        height=165,
        weight=70,
        medical_history=["hypertension"],
        lifestyle={"exercise": "moderate", "smoking": "no", "alcohol": "occasional"},
        health_goals=["lose weight", "improve fitness"]
    )
    
    recommendations = await client.analyze_user_profile(profile)
    
    print("Content Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.category} (Priority: {rec.priority})")
        print(f"   Topics: {', '.join(rec.topics)}")
        print(f"   Reasoning: {rec.reasoning}")
        print(f"   Keywords: {', '.join(rec.keywords)}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_client())

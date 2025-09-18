#!/usr/bin/env python3
"""
Health Content Matcher
Matches user recommendations with curated health articles
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

@dataclass
class HealthArticle:
    """Health article data structure"""
    id: str
    title: str
    summary: str
    content_type: str  # 'article', 'guide', 'tips', 'research'
    category: str
    subcategory: Optional[str]
    keywords: List[str]
    target_audience: List[str]  # 'general', 'men', 'women', 'seniors', 'adults', 'young_adults'
    medical_conditions: List[str]  # Relevant medical conditions
    reading_time: int  # in minutes
    credibility_score: int  # 1-5, 5 = highest
    source: str
    author: str
    published_date: datetime
    url: str
    image_url: Optional[str] = None
    is_evergreen: bool = True  # True for timeless content, False for time-sensitive

class ContentDatabase:
    """Database for health articles and content matching"""
    
    def __init__(self, db_path: str = "health_content.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_articles()
    
    def init_database(self):
        """Initialize content database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Health articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                content_type TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                keywords TEXT NOT NULL,  -- JSON array
                target_audience TEXT NOT NULL,  -- JSON array
                medical_conditions TEXT NOT NULL,  -- JSON array
                reading_time INTEGER DEFAULT 5,
                credibility_score INTEGER DEFAULT 3,
                source TEXT NOT NULL,
                author TEXT,
                published_date TIMESTAMP,
                url TEXT NOT NULL,
                image_url TEXT,
                is_evergreen BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User content matches table (for tracking what was shown)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_content_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                article_id TEXT NOT NULL,
                recommendation_category TEXT NOT NULL,
                match_score REAL NOT NULL,
                shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicked BOOLEAN DEFAULT 0,
                FOREIGN KEY (article_id) REFERENCES health_articles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_articles(self):
        """Populate database with curated health articles"""
        
        # Check if articles already exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM health_articles')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            return  # Articles already exist
        
        sample_articles = [
            # Heart Health Articles
            HealthArticle(
                id="heart_001",
                title="10 Foods That Boost Heart Health",
                summary="Discover the best foods to include in your diet for optimal cardiovascular health, backed by scientific research.",
                content_type="guide",
                category="Heart Health",
                subcategory="Nutrition",
                keywords=["heart health", "cardiovascular", "nutrition", "diet", "cholesterol", "omega-3"],
                target_audience=["general", "adults", "seniors"],
                medical_conditions=["hypertension", "high cholesterol", "heart disease"],
                reading_time=7,
                credibility_score=5,
                source="American Heart Association",
                author="Dr. Sarah Johnson",
                published_date=datetime(2024, 1, 15),
                url="https://example.com/heart-healthy-foods",
                image_url="https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400"
            ),
            
            HealthArticle(
                id="heart_002",
                title="Understanding Blood Pressure: A Complete Guide",
                summary="Learn about blood pressure, what the numbers mean, and how to maintain healthy levels through lifestyle changes.",
                content_type="guide",
                category="Heart Health",
                subcategory="Prevention",
                keywords=["blood pressure", "hypertension", "cardiovascular", "monitoring", "lifestyle"],
                target_audience=["general", "adults", "seniors"],
                medical_conditions=["hypertension", "cardiovascular disease"],
                reading_time=10,
                credibility_score=5,
                source="Mayo Clinic",
                author="Dr. Michael Chen",
                published_date=datetime(2024, 2, 1),
                url="https://example.com/blood-pressure-guide",
                image_url="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400"
            ),
            
            # Nutrition Articles
            HealthArticle(
                id="nutrition_001",
                title="The Complete Guide to Balanced Nutrition",
                summary="Master the fundamentals of balanced nutrition with practical tips for meal planning and healthy eating habits.",
                content_type="guide",
                category="Nutrition",
                subcategory="General",
                keywords=["nutrition", "balanced diet", "macronutrients", "meal planning", "healthy eating"],
                target_audience=["general", "adults", "young_adults"],
                medical_conditions=["diabetes", "obesity", "metabolic syndrome"],
                reading_time=12,
                credibility_score=5,
                source="Harvard Health Publishing",
                author="Dr. Lisa Martinez",
                published_date=datetime(2024, 1, 20),
                url="https://example.com/balanced-nutrition-guide",
                image_url="https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400"
            ),
            
            HealthArticle(
                id="nutrition_002",
                title="Managing Diabetes Through Diet",
                summary="Evidence-based dietary strategies for managing blood sugar levels and living well with diabetes.",
                content_type="guide",
                category="Nutrition",
                subcategory="Disease Management",
                keywords=["diabetes", "blood sugar", "carbohydrates", "glycemic index", "meal planning"],
                target_audience=["general", "adults", "seniors"],
                medical_conditions=["diabetes", "prediabetes", "metabolic syndrome"],
                reading_time=15,
                credibility_score=5,
                source="American Diabetes Association",
                author="Dr. Robert Kim",
                published_date=datetime(2024, 2, 10),
                url="https://example.com/diabetes-diet-management",
                image_url="https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400"
            ),
            
            # Mental Health Articles
            HealthArticle(
                id="mental_001",
                title="Stress Management Techniques That Actually Work",
                summary="Science-backed methods for managing stress, including mindfulness, breathing exercises, and lifestyle changes.",
                content_type="guide",
                category="Mental Health",
                subcategory="Stress Management",
                keywords=["stress management", "mindfulness", "anxiety", "relaxation", "mental wellness"],
                target_audience=["general", "adults", "young_adults"],
                medical_conditions=["anxiety", "depression", "stress disorders"],
                reading_time=8,
                credibility_score=4,
                source="Psychology Today",
                author="Dr. Emma Wilson",
                published_date=datetime(2024, 1, 25),
                url="https://example.com/stress-management-techniques",
                image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400"
            ),
            
            # Exercise & Fitness Articles
            HealthArticle(
                id="fitness_001",
                title="Exercise for Beginners: A Step-by-Step Guide",
                summary="Start your fitness journey with this comprehensive guide covering basic exercises, safety tips, and progression plans.",
                content_type="guide",
                category="Exercise & Fitness",
                subcategory="Beginner",
                keywords=["exercise", "fitness", "beginner", "workout", "physical activity", "strength training"],
                target_audience=["general", "adults", "young_adults"],
                medical_conditions=["obesity", "cardiovascular disease", "diabetes"],
                reading_time=12,
                credibility_score=4,
                source="ACSM Fitness",
                author="Dr. James Thompson",
                published_date=datetime(2024, 1, 30),
                url="https://example.com/beginner-exercise-guide",
                image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400"
            ),
            
            # Women's Health Articles
            HealthArticle(
                id="womens_001",
                title="Women's Health After 40: What You Need to Know",
                summary="Essential health information for women over 40, covering hormonal changes, preventive care, and wellness strategies.",
                content_type="guide",
                category="Women's Health",
                subcategory="Age-Specific",
                keywords=["women's health", "menopause", "hormones", "preventive care", "bone health"],
                target_audience=["women", "adults"],
                medical_conditions=["osteoporosis", "hormonal imbalance", "cardiovascular disease"],
                reading_time=10,
                credibility_score=5,
                source="Women's Health Magazine",
                author="Dr. Patricia Lee",
                published_date=datetime(2024, 2, 5),
                url="https://example.com/womens-health-after-40",
                image_url="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400"
            ),
            
            # Men's Health Articles
            HealthArticle(
                id="mens_001",
                title="Men's Health Essentials: Preventive Care Guide",
                summary="Key health screenings, lifestyle factors, and preventive measures every man should know about.",
                content_type="guide",
                category="Men's Health",
                subcategory="Preventive Care",
                keywords=["men's health", "preventive care", "screening", "prostate health", "testosterone"],
                target_audience=["men", "adults", "seniors"],
                medical_conditions=["prostate issues", "cardiovascular disease", "diabetes"],
                reading_time=9,
                credibility_score=5,
                source="Men's Health Network",
                author="Dr. David Brown",
                published_date=datetime(2024, 2, 12),
                url="https://example.com/mens-preventive-health",
                image_url="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400"
            ),
            
            # Sleep & Recovery Articles
            HealthArticle(
                id="sleep_001",
                title="The Science of Better Sleep: A Complete Guide",
                summary="Understand sleep cycles, common sleep disorders, and evidence-based strategies for improving sleep quality.",
                content_type="guide",
                category="Sleep & Recovery",
                subcategory="Sleep Hygiene",
                keywords=["sleep", "insomnia", "sleep hygiene", "circadian rhythm", "recovery"],
                target_audience=["general", "adults", "young_adults"],
                medical_conditions=["insomnia", "sleep apnea", "anxiety", "depression"],
                reading_time=11,
                credibility_score=5,
                source="Sleep Foundation",
                author="Dr. Rachel Green",
                published_date=datetime(2024, 1, 18),
                url="https://example.com/better-sleep-guide",
                image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400"
            )
        ]
        
        # Insert articles into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for article in sample_articles:
            cursor.execute('''
                INSERT INTO health_articles 
                (id, title, summary, content_type, category, subcategory, keywords, 
                 target_audience, medical_conditions, reading_time, credibility_score, 
                 source, author, published_date, url, image_url, is_evergreen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.id,
                article.title,
                article.summary,
                article.content_type,
                article.category,
                article.subcategory,
                json.dumps(article.keywords),
                json.dumps(article.target_audience),
                json.dumps(article.medical_conditions),
                article.reading_time,
                article.credibility_score,
                article.source,
                article.author,
                article.published_date.isoformat(),
                article.url,
                article.image_url,
                article.is_evergreen
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Populated database with {len(sample_articles)} health articles")

class ContentMatcher:
    """Matches user recommendations with relevant health content"""
    
    def __init__(self):
        self.db = ContentDatabase()
    
    def get_personalized_articles(self, user_id: str, recommendations: List[Dict], limit: int = 20) -> List[Dict]:
        """Get personalized articles based on user recommendations"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        matched_articles = []
        
        for rec in recommendations:
            category = rec['category']
            keywords = rec['keywords']
            priority = rec['priority']
            
            # Find articles matching this recommendation
            articles = self._find_matching_articles(cursor, category, keywords, limit=5)
            
            for article in articles:
                # Calculate match score
                match_score = self._calculate_match_score(rec, article)
                
                # Add to results with match info
                article_with_match = {
                    **article,
                    'recommendation_category': category,
                    'match_score': match_score,
                    'priority': priority,
                    'reasoning': rec.get('reasoning', '')
                }
                matched_articles.append(article_with_match)
        
        conn.close()
        
        # Sort by priority and match score
        matched_articles.sort(key=lambda x: (x['priority'], -x['match_score']))
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_articles = []
        
        for article in matched_articles:
            if article['id'] not in seen_ids and len(unique_articles) < limit:
                seen_ids.add(article['id'])
                unique_articles.append(article)
        
        # Track that these articles were shown to user
        self._track_shown_articles(user_id, unique_articles)
        
        return unique_articles
    
    def _find_matching_articles(self, cursor, category: str, keywords: List[str], limit: int = 5) -> List[Dict]:
        """Find articles matching category and keywords"""
        
        # Build keyword search condition
        keyword_conditions = []
        params = []
        
        for keyword in keywords:
            keyword_conditions.append("keywords LIKE ?")
            params.append(f'%{keyword.lower()}%')
        
        # Build query
        query = '''
            SELECT id, title, summary, content_type, category, subcategory, 
                   keywords, target_audience, medical_conditions, reading_time,
                   credibility_score, source, author, published_date, url, image_url
            FROM health_articles 
            WHERE (category LIKE ? OR subcategory LIKE ?)
        '''
        params.insert(0, f'%{category}%')
        params.insert(1, f'%{category}%')
        
        if keyword_conditions:
            query += f" AND ({' OR '.join(keyword_conditions)})"
        
        query += " ORDER BY credibility_score DESC, published_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'title': row[1],
                'summary': row[2],
                'content_type': row[3],
                'category': row[4],
                'subcategory': row[5],
                'keywords': json.loads(row[6]),
                'target_audience': json.loads(row[7]),
                'medical_conditions': json.loads(row[8]),
                'reading_time': row[9],
                'credibility_score': row[10],
                'source': row[11],
                'author': row[12],
                'published_date': row[13],
                'url': row[14],
                'image_url': row[15]
            })
        
        return articles
    
    def _calculate_match_score(self, recommendation: Dict, article: Dict) -> float:
        """Calculate how well an article matches a recommendation"""
        score = 0.0
        
        # Category match
        if recommendation['category'].lower() in article['category'].lower():
            score += 0.4
        
        # Keyword matches
        rec_keywords = [k.lower() for k in recommendation['keywords']]
        article_keywords = [k.lower() for k in article['keywords']]
        
        keyword_matches = len(set(rec_keywords) & set(article_keywords))
        if keyword_matches > 0:
            score += min(0.4, keyword_matches * 0.1)
        
        # Credibility score bonus
        score += (article['credibility_score'] - 1) * 0.05  # 0.0 to 0.2 bonus
        
        # Recency bonus (for non-evergreen content)
        if not article.get('is_evergreen', True):
            pub_date = datetime.fromisoformat(article['published_date'])
            days_old = (datetime.now() - pub_date).days
            if days_old < 30:
                score += 0.1
        
        return min(1.0, score)
    
    def _track_shown_articles(self, user_id: str, articles: List[Dict]):
        """Track which articles were shown to user"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for article in articles:
            cursor.execute('''
                INSERT INTO user_content_matches 
                (user_id, article_id, recommendation_category, match_score)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                article['id'],
                article['recommendation_category'],
                article['match_score']
            ))
        
        conn.commit()
        conn.close()
    
    def get_trending_articles(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get trending/popular articles"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT ha.id, ha.title, ha.summary, ha.category, ha.image_url, ha.url,
                   COUNT(ucm.id) as view_count
            FROM health_articles ha
            LEFT JOIN user_content_matches ucm ON ha.id = ucm.article_id
        '''
        params = []
        
        if category:
            query += " WHERE ha.category LIKE ?"
            params.append(f'%{category}%')
        
        query += '''
            GROUP BY ha.id
            ORDER BY view_count DESC, ha.credibility_score DESC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'title': row[1],
                'summary': row[2],
                'category': row[3],
                'image_url': row[4],
                'url': row[5],
                'view_count': row[6]
            })
        
        conn.close()
        return articles

# Test function
def test_content_matcher():
    """Test the content matcher"""
    matcher = ContentMatcher()
    
    # Sample recommendations
    recommendations = [
        {
            'category': 'Heart Health',
            'priority': 1,
            'keywords': ['cardiovascular', 'heart', 'blood pressure'],
            'reasoning': 'User has hypertension'
        },
        {
            'category': 'Nutrition',
            'priority': 2,
            'keywords': ['diet', 'nutrition', 'healthy eating'],
            'reasoning': 'User wants to improve diet'
        }
    ]
    
    # Get personalized articles
    articles = matcher.get_personalized_articles('test_user', recommendations, limit=10)
    
    print(f"Found {len(articles)} personalized articles:")
    for article in articles:
        print(f"- {article['title']} ({article['category']})")
        print(f"  Match Score: {article['match_score']:.2f}")
        print(f"  Priority: {article['priority']}")
        print(f"  Reasoning: {article['reasoning']}")
        print()

if __name__ == "__main__":
    test_content_matcher()

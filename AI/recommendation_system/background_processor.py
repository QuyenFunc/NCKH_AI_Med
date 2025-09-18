#!/usr/bin/env python3
"""
Background Job Processor for Health Content Recommendations
Handles profile analysis and content matching in background
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
import threading
from queue import Queue, Empty

from openrouter_client import OpenRouterClient, UserProfile, ContentRecommendation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingJob:
    """Background processing job"""
    job_id: str
    user_id: str
    job_type: str  # 'profile_analysis', 'content_update'
    profile_data: Dict
    created_at: datetime
    status: str = 'pending'  # pending, processing, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None

class RecommendationDatabase:
    """SQLite database for storing recommendations"""
    
    def __init__(self, db_path: str = "recommendations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                topics TEXT NOT NULL,  -- JSON array
                reasoning TEXT,
                keywords TEXT NOT NULL,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Processing jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                job_type TEXT NOT NULL,
                profile_data TEXT NOT NULL,  -- JSON
                status TEXT DEFAULT 'pending',
                result TEXT,  -- JSON
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profile snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                profile_hash TEXT NOT NULL,
                profile_data TEXT NOT NULL,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_recommendations(self, user_id: str, recommendations: List[ContentRecommendation]):
        """Save user recommendations to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete existing recommendations for user
        cursor.execute('DELETE FROM user_recommendations WHERE user_id = ?', (user_id,))
        
        # Insert new recommendations
        for rec in recommendations:
            cursor.execute('''
                INSERT INTO user_recommendations 
                (user_id, category, priority, topics, reasoning, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                rec.category,
                rec.priority,
                json.dumps(rec.topics),
                rec.reasoning,
                json.dumps(rec.keywords)
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(recommendations)} recommendations for user {user_id}")
    
    def get_recommendations(self, user_id: str) -> List[Dict]:
        """Get user recommendations from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, priority, topics, reasoning, keywords, created_at
            FROM user_recommendations 
            WHERE user_id = ?
            ORDER BY priority ASC, created_at DESC
        ''', (user_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'category': row[0],
                'priority': row[1],
                'topics': json.loads(row[2]),
                'reasoning': row[3],
                'keywords': json.loads(row[4]),
                'created_at': row[5]
            })
        
        conn.close()
        return results
    
    def save_job(self, job: ProcessingJob):
        """Save processing job to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO processing_jobs 
            (job_id, user_id, job_type, profile_data, status, result, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job.job_id,
            job.user_id,
            job.job_type,
            json.dumps(job.profile_data),
            job.status,
            json.dumps(job.result) if job.result else None,
            job.error
        ))
        
        conn.commit()
        conn.close()
    
    def should_reprocess_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Check if profile has changed significantly and needs reprocessing"""
        import hashlib
        
        # Create hash of important profile fields
        important_fields = ['age', 'gender', 'height', 'weight', 'medical_history', 
                          'allergies', 'current_medications', 'lifestyle', 'health_goals']
        
        profile_subset = {k: v for k, v in profile_data.items() if k in important_fields}
        profile_hash = hashlib.md5(json.dumps(profile_subset, sort_keys=True).encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check last profile hash
        cursor.execute('''
            SELECT profile_hash FROM user_profile_snapshots 
            WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if not result or result[0] != profile_hash:
            # Save new profile snapshot
            cursor.execute('''
                INSERT INTO user_profile_snapshots (user_id, profile_hash, profile_data)
                VALUES (?, ?, ?)
            ''', (user_id, profile_hash, json.dumps(profile_data)))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

class BackgroundProcessor:
    """Background processor for health content recommendations"""
    
    def __init__(self):
        self.job_queue = Queue()
        self.openrouter_client = OpenRouterClient()
        self.db = RecommendationDatabase()
        self.is_running = False
        self.worker_thread = None
    
    def start(self):
        """Start the background processor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Background processor started")
    
    def stop(self):
        """Stop the background processor"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("Background processor stopped")
    
    def queue_profile_analysis(self, user_id: str, profile_data: Dict) -> str:
        """Queue a profile analysis job"""
        
        # Check if profile needs reprocessing
        if not self.db.should_reprocess_profile(user_id, profile_data):
            logger.info(f"Profile for user {user_id} hasn't changed significantly, skipping analysis")
            return None
        
        job_id = f"profile_analysis_{user_id}_{int(datetime.now().timestamp())}"
        
        job = ProcessingJob(
            job_id=job_id,
            user_id=user_id,
            job_type='profile_analysis',
            profile_data=profile_data,
            created_at=datetime.now()
        )
        
        self.job_queue.put(job)
        self.db.save_job(job)
        
        logger.info(f"Queued profile analysis job {job_id} for user {user_id}")
        return job_id
    
    def get_user_recommendations(self, user_id: str) -> List[Dict]:
        """Get cached recommendations for user"""
        return self.db.get_recommendations(user_id)
    
    def _worker_loop(self):
        """Main worker loop"""
        logger.info("Background worker started")
        
        while self.is_running:
            try:
                # Get job from queue with timeout
                job = self.job_queue.get(timeout=1)
                
                logger.info(f"Processing job {job.job_id} for user {job.user_id}")
                
                # Update job status
                job.status = 'processing'
                self.db.save_job(job)
                
                # Process the job
                if job.job_type == 'profile_analysis':
                    self._process_profile_analysis(job)
                
                # Mark as completed
                job.status = 'completed'
                self.db.save_job(job)
                
                logger.info(f"Completed job {job.job_id}")
                
            except Empty:
                # No jobs in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                if 'job' in locals():
                    job.status = 'failed'
                    job.error = str(e)
                    self.db.save_job(job)
    
    def _process_profile_analysis(self, job: ProcessingJob):
        """Process profile analysis job"""
        try:
            # Convert profile data to UserProfile object
            profile = UserProfile(
                user_id=job.user_id,
                age=job.profile_data.get('age'),
                gender=job.profile_data.get('gender'),
                height=job.profile_data.get('height'),
                weight=job.profile_data.get('weight'),
                medical_history=job.profile_data.get('medical_history', []),
                allergies=job.profile_data.get('allergies', []),
                current_medications=job.profile_data.get('current_medications', []),
                lifestyle=job.profile_data.get('lifestyle', {}),
                health_goals=job.profile_data.get('health_goals', [])
            )
            
            # Analyze profile with OpenRouter
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            recommendations = loop.run_until_complete(
                self.openrouter_client.analyze_user_profile(profile)
            )
            
            loop.close()
            
            # Save recommendations to database
            self.db.save_recommendations(job.user_id, recommendations)
            
            # Store result in job
            job.result = {
                'recommendations_count': len(recommendations),
                'categories': [rec.category for rec in recommendations],
                'processed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {job.user_id}")
            
        except Exception as e:
            logger.error(f"Error in profile analysis: {e}")
            raise

# Global processor instance
processor = BackgroundProcessor()

def start_background_processor():
    """Start the global background processor"""
    processor.start()

def stop_background_processor():
    """Stop the global background processor"""
    processor.stop()

def queue_user_profile_analysis(user_id: str, profile_data: Dict) -> Optional[str]:
    """Queue profile analysis for user"""
    return processor.queue_profile_analysis(user_id, profile_data)

def get_user_content_recommendations(user_id: str) -> List[Dict]:
    """Get content recommendations for user"""
    return processor.get_user_recommendations(user_id)

# Test function
def test_background_processor():
    """Test the background processor"""
    
    # Start processor
    start_background_processor()
    
    # Test profile data
    profile_data = {
        'age': 30,
        'gender': 'male',
        'height': 175,
        'weight': 80,
        'medical_history': ['diabetes'],
        'lifestyle': {'exercise': 'regular', 'smoking': 'no'},
        'health_goals': ['manage diabetes', 'lose weight']
    }
    
    # Queue analysis
    job_id = queue_user_profile_analysis('test_user_123', profile_data)
    print(f"Queued job: {job_id}")
    
    # Wait a bit for processing
    import time
    time.sleep(10)
    
    # Get recommendations
    recommendations = get_user_content_recommendations('test_user_123')
    print(f"Found {len(recommendations)} recommendations")
    
    for rec in recommendations:
        print(f"- {rec['category']} (Priority: {rec['priority']})")
        print(f"  Topics: {', '.join(rec['topics'])}")
        print(f"  Reasoning: {rec['reasoning']}")
        print()
    
    # Stop processor
    stop_background_processor()

if __name__ == "__main__":
    test_background_processor()

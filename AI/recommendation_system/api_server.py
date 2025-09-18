#!/usr/bin/env python3
"""
Health Content Recommendation API Server
Flask API for integrating with Spring Boot backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime

from background_processor import (
    start_background_processor, 
    stop_background_processor,
    queue_user_profile_analysis,
    get_user_content_recommendations
)
from content_matcher import ContentMatcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
content_matcher = ContentMatcher()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Health Content Recommendation API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/recommendations/analyze-profile', methods=['POST'])
def analyze_user_profile():
    """
    Analyze user profile and queue background job for content recommendations
    
    Expected payload:
    {
        "user_id": "string",
        "profile": {
            "age": int,
            "gender": "string",
            "height": float,
            "weight": float,
            "medical_history": ["string"],
            "allergies": ["string"],
            "current_medications": ["string"],
            "lifestyle": {
                "exercise": "string",
                "smoking": "string",
                "alcohol": "string"
            },
            "health_goals": ["string"]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'profile' not in data:
            return jsonify({
                'error': 'Missing required fields: user_id and profile'
            }), 400
        
        user_id = data['user_id']
        profile_data = data['profile']
        
        # Queue background analysis
        job_id = queue_user_profile_analysis(user_id, profile_data)
        
        if job_id:
            logger.info(f"Queued profile analysis for user {user_id}, job_id: {job_id}")
            return jsonify({
                'success': True,
                'message': 'Profile analysis queued successfully',
                'job_id': job_id,
                'user_id': user_id
            })
        else:
            logger.info(f"Profile analysis skipped for user {user_id} (no significant changes)")
            return jsonify({
                'success': True,
                'message': 'Profile analysis skipped - no significant changes detected',
                'user_id': user_id
            })
            
    except Exception as e:
        logger.error(f"Error in analyze_user_profile: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/recommendations/user/<user_id>', methods=['GET'])
def get_user_recommendations(user_id: str):
    """
    Get personalized content recommendations for user
    
    Query parameters:
    - limit: number of articles to return (default: 20)
    - category: filter by category (optional)
    """
    try:
        limit = int(request.args.get('limit', 20))
        category_filter = request.args.get('category')
        
        # Get user recommendations from background processor
        recommendations = get_user_content_recommendations(user_id)
        
        if not recommendations:
            return jsonify({
                'success': False,
                'message': 'No recommendations found for user. Profile analysis may be in progress.',
                'user_id': user_id,
                'articles': []
            })
        
        # Filter by category if specified
        if category_filter:
            recommendations = [r for r in recommendations if category_filter.lower() in r['category'].lower()]
        
        # Get personalized articles
        articles = content_matcher.get_personalized_articles(user_id, recommendations, limit)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'total_articles': len(articles),
            'articles': articles,
            'categories': list(set(r['category'] for r in recommendations))
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/recommendations/trending', methods=['GET'])
def get_trending_articles():
    """
    Get trending/popular health articles
    
    Query parameters:
    - limit: number of articles to return (default: 10)
    - category: filter by category (optional)
    """
    try:
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        
        articles = content_matcher.get_trending_articles(category, limit)
        
        return jsonify({
            'success': True,
            'total_articles': len(articles),
            'articles': articles,
            'category': category
        })
        
    except Exception as e:
        logger.error(f"Error getting trending articles: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/recommendations/categories', methods=['GET'])
def get_available_categories():
    """Get list of available content categories"""
    categories = [
        "Heart Health",
        "Nutrition",
        "Exercise & Fitness", 
        "Mental Health",
        "Sleep & Recovery",
        "Women's Health",
        "Men's Health",
        "Preventive Care",
        "Chronic Disease Management",
        "Weight Management",
        "Bone & Joint Health",
        "Immune System Support"
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    })

@app.route('/recommendations/track-click', methods=['POST'])
def track_article_click():
    """
    Track when user clicks on an article
    
    Expected payload:
    {
        "user_id": "string",
        "article_id": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'article_id' not in data:
            return jsonify({
                'error': 'Missing required fields: user_id and article_id'
            }), 400
        
        user_id = data['user_id']
        article_id = data['article_id']
        
        # Update click tracking in database
        import sqlite3
        conn = sqlite3.connect(content_matcher.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_content_matches 
            SET clicked = 1 
            WHERE user_id = ? AND article_id = ?
        ''', (user_id, article_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Tracked click for user {user_id} on article {article_id}")
        
        return jsonify({
            'success': True,
            'message': 'Click tracked successfully'
        })
        
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/recommendations/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        import sqlite3
        
        # Get database stats
        conn = sqlite3.connect(content_matcher.db.db_path)
        cursor = conn.cursor()
        
        # Total articles
        cursor.execute('SELECT COUNT(*) FROM health_articles')
        total_articles = cursor.fetchone()[0]
        
        # Total users with recommendations
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_recommendations')
        users_with_recommendations = cursor.fetchone()[0]
        
        # Total content matches
        cursor.execute('SELECT COUNT(*) FROM user_content_matches')
        total_matches = cursor.fetchone()[0]
        
        # Click rate
        cursor.execute('SELECT COUNT(*) FROM user_content_matches WHERE clicked = 1')
        total_clicks = cursor.fetchone()[0]
        
        click_rate = (total_clicks / total_matches * 100) if total_matches > 0 else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_articles': total_articles,
                'users_with_recommendations': users_with_recommendations,
                'total_content_matches': total_matches,
                'total_clicks': total_clicks,
                'click_rate_percent': round(click_rate, 2)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def start_server():
    """Start the recommendation API server"""
    logger.info("Starting Health Content Recommendation API Server...")
    
    # Start background processor
    start_background_processor()
    logger.info("Background processor started")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)

def stop_server():
    """Stop the server and cleanup"""
    logger.info("Stopping server...")
    stop_background_processor()

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        stop_server()
    except Exception as e:
        logger.error(f"Server error: {e}")
        stop_server()

"""
Enhanced Logging System for Medical RAG
Theo dõi và phân tích hiệu quả của hệ thống chatbot y tế
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


class MedicalChatLogger:
    """
    Comprehensive logging system for medical chatbot
    """
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = log_directory
        self._ensure_log_directory()
        self._setup_loggers()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
    
    def _setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # Main application logger
        self.app_logger = logging.getLogger('medical_app')
        self.app_logger.setLevel(logging.INFO)
        
        # Medical query logger
        self.query_logger = logging.getLogger('medical_queries')
        self.query_logger.setLevel(logging.INFO)
        
        # Search performance logger
        self.search_logger = logging.getLogger('search_performance')
        self.search_logger.setLevel(logging.INFO)
        
        # User interaction logger
        self.interaction_logger = logging.getLogger('user_interactions')
        self.interaction_logger.setLevel(logging.INFO)
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file handlers for different loggers"""
        
        # Date-based log files
        today = datetime.now().strftime("%Y-%m-%d")
        
        # App logger handler
        app_handler = logging.FileHandler(
            os.path.join(self.log_directory, f"medical_app_{today}.log"),
            encoding='utf-8'
        )
        app_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        app_handler.setFormatter(app_formatter)
        self.app_logger.addHandler(app_handler)
        
        # Query logger handler
        query_handler = logging.FileHandler(
            os.path.join(self.log_directory, f"medical_queries_{today}.log"),
            encoding='utf-8'
        )
        query_formatter = logging.Formatter('%(asctime)s | %(message)s')
        query_handler.setFormatter(query_formatter)
        self.query_logger.addHandler(query_handler)
        
        # Search performance handler
        search_handler = logging.FileHandler(
            os.path.join(self.log_directory, f"search_performance_{today}.log"),
            encoding='utf-8'
        )
        search_formatter = logging.Formatter('%(asctime)s | %(message)s')
        search_handler.setFormatter(search_formatter)
        self.search_logger.addHandler(search_handler)
        
        # Interaction handler
        interaction_handler = logging.FileHandler(
            os.path.join(self.log_directory, f"user_interactions_{today}.log"),
            encoding='utf-8'
        )
        interaction_formatter = logging.Formatter('%(asctime)s | %(message)s')
        interaction_handler.setFormatter(interaction_formatter)
        self.interaction_logger.addHandler(interaction_handler)
        
        # Console handler for app logger
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        console_handler.setFormatter(console_formatter)
        self.app_logger.addHandler(console_handler)
    
    def log_query_request(self, session_id: str, user_query: str, intent: str, 
                         transformation_data: Dict[str, Any] = None):
        """Log medical query request"""
        
        log_data = {
            'event': 'query_request',
            'session_id': session_id,
            'query': user_query,
            'intent': intent,
            'query_length': len(user_query),
            'timestamp': datetime.now().isoformat()
        }
        
        if transformation_data:
            log_data.update({
                'search_strategy': transformation_data.get('search_strategy'),
                'sub_queries_count': len(transformation_data.get('sub_queries', [])),
                'medical_entities': transformation_data.get('medical_entities', {}),
                'alternative_queries_count': len(transformation_data.get('alternative_queries', []))
            })
        
        self.query_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_search_performance(self, session_id: str, search_method: str,
                             query: str, results_count: int, search_time: float,
                             top_scores: List[float] = None):
        """Log search performance metrics"""
        
        log_data = {
            'event': 'search_performance',
            'session_id': session_id,
            'search_method': search_method,
            'query': query,
            'results_count': results_count,
            'search_time_ms': round(search_time * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        if top_scores:
            log_data.update({
                'top_score': max(top_scores) if top_scores else 0,
                'avg_score': sum(top_scores) / len(top_scores) if top_scores else 0,
                'score_variance': self._calculate_variance(top_scores) if len(top_scores) > 1 else 0
            })
        
        self.search_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_llm_interaction(self, session_id: str, user_query: str, 
                           llm_response: str, context_length: int,
                           response_time: float, token_count: Optional[int] = None):
        """Log LLM interaction details"""
        
        log_data = {
            'event': 'llm_interaction',
            'session_id': session_id,
            'query': user_query,
            'response_length': len(llm_response),
            'context_length': context_length,
            'response_time_ms': round(response_time * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        if token_count:
            log_data['estimated_tokens'] = token_count
        
        self.interaction_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_structured_extraction(self, session_id: str, intent: str, 
                                 schema_type: str, extraction_success: bool,
                                 confidence_score: float, extraction_time: float):
        """Log structured data extraction results"""
        
        log_data = {
            'event': 'structured_extraction',
            'session_id': session_id,
            'intent': intent,
            'schema_type': schema_type,
            'extraction_success': extraction_success,
            'confidence_score': confidence_score,
            'extraction_time_ms': round(extraction_time * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        self.search_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_user_feedback(self, session_id: str, query: str, rating: int,
                         feedback_text: str = "", helpful: bool = None):
        """Log user feedback for analysis"""
        
        log_data = {
            'event': 'user_feedback',
            'session_id': session_id,
            'query': query,
            'rating': rating,
            'feedback_text': feedback_text,
            'helpful': helpful,
            'timestamp': datetime.now().isoformat()
        }
        
        self.interaction_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, error_type: str, error_message: str, 
                 context: Dict[str, Any] = None):
        """Log errors with context"""
        
        error_data = {
            'event': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_data['context'] = context
        
        self.app_logger.error(json.dumps(error_data, ensure_ascii=False))
    
    def log_session_activity(self, session_id: str, event_type: str,
                           metadata: Dict[str, Any] = None):
        """Log session-related activities"""
        
        log_data = {
            'event': 'session_activity',
            'session_id': session_id,
            'event_type': event_type,  # 'created', 'ended', 'timeout', etc.
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            log_data.update(metadata)
        
        self.interaction_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance, 4)
    
    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """Get daily statistics from logs"""
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        stats = {
            'date': date,
            'total_queries': 0,
            'intent_breakdown': {},
            'avg_response_time': 0,
            'error_count': 0,
            'unique_sessions': set(),
            'search_performance': {
                'hybrid_searches': 0,
                'fallback_searches': 0,
                'avg_search_time': 0
            }
        }
        
        try:
            # Process query log
            query_log_file = os.path.join(self.log_directory, f"medical_queries_{date}.log")
            if os.path.exists(query_log_file):
                with open(query_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            # Extract JSON part after timestamp
                            json_part = line.split(' | ', 1)[1]
                            data = json.loads(json_part)
                            
                            if data.get('event') == 'query_request':
                                stats['total_queries'] += 1
                                intent = data.get('intent', 'unknown')
                                stats['intent_breakdown'][intent] = stats['intent_breakdown'].get(intent, 0) + 1
                                stats['unique_sessions'].add(data.get('session_id'))
                        
                        except (json.JSONDecodeError, IndexError):
                            continue
            
            # Process search performance log
            search_log_file = os.path.join(self.log_directory, f"search_performance_{date}.log")
            if os.path.exists(search_log_file):
                search_times = []
                with open(search_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            json_part = line.split(' | ', 1)[1]
                            data = json.loads(json_part)
                            
                            if data.get('event') == 'search_performance':
                                search_method = data.get('search_method', 'unknown')
                                if 'hybrid' in search_method:
                                    stats['search_performance']['hybrid_searches'] += 1
                                else:
                                    stats['search_performance']['fallback_searches'] += 1
                                
                                search_time = data.get('search_time_ms', 0)
                                if search_time > 0:
                                    search_times.append(search_time)
                        
                        except (json.JSONDecodeError, IndexError):
                            continue
                
                if search_times:
                    stats['search_performance']['avg_search_time'] = round(sum(search_times) / len(search_times), 2)
            
            # Convert unique_sessions set to count
            stats['unique_sessions'] = len(stats['unique_sessions'])
            
        except Exception as e:
            self.log_error('stats_calculation', str(e))
        
        return stats


# Global logger instance
medical_logger = None

def get_medical_logger():
    """Get the global medical logger instance"""
    global medical_logger
    if medical_logger is None:
        medical_logger = MedicalChatLogger()
    return medical_logger

# Convenience functions
def log_query(session_id: str, query: str, intent: str, transformation: Dict = None):
    logger = get_medical_logger()
    logger.log_query_request(session_id, query, intent, transformation)

def log_search(session_id: str, method: str, query: str, count: int, time: float, scores: List[float] = None):
    logger = get_medical_logger()
    logger.log_search_performance(session_id, method, query, count, time, scores)

def log_llm(session_id: str, query: str, response: str, context_len: int, time: float):
    logger = get_medical_logger()
    logger.log_llm_interaction(session_id, query, response, context_len, time)

def log_extraction(session_id: str, intent: str, schema: str, success: bool, confidence: float, time: float):
    logger = get_medical_logger()
    logger.log_structured_extraction(session_id, intent, schema, success, confidence, time)

def log_error(error_type: str, message: str, context: Dict = None):
    logger = get_medical_logger()
    logger.log_error(error_type, message, context)

def get_stats(date: str = None) -> Dict[str, Any]:
    logger = get_medical_logger()
    return logger.get_daily_stats(date)


# Test function
def test_logging_system():
    """Test the logging system"""
    
    logger = MedicalChatLogger()
    test_session = str(uuid.uuid4())
    
    print("🧪 Testing Medical Logging System...")
    
    # Test query logging
    logger.log_query_request(
        test_session, 
        "Tôi bị đau đầu và chóng mặt", 
        "symptom_inquiry",
        {
            'search_strategy': 'multi_symptom',
            'sub_queries': ['đau đầu', 'chóng mặt'],
            'medical_entities': {'symptoms': ['đau đầu', 'chóng mặt']}
        }
    )
    
    # Test search logging
    logger.log_search_performance(
        test_session,
        "hybrid_search",
        "đau đầu chóng mặt",
        5,
        0.234,
        [0.95, 0.87, 0.76, 0.65, 0.54]
    )
    
    # Test LLM logging
    logger.log_llm_interaction(
        test_session,
        "Tôi bị đau đầu",
        "Đau đầu có thể do nhiều nguyên nhân...",
        1500,
        2.34
    )
    
    # Test structured extraction logging
    logger.log_structured_extraction(
        test_session,
        "symptom_inquiry",
        "symptom_analysis",
        True,
        0.87,
        0.456
    )
    
    # Test error logging
    logger.log_error(
        "hybrid_search_error",
        "Failed to initialize BM25 model",
        {'query': 'test query', 'session': test_session}
    )
    
    print("✅ Logging system test completed. Check logs/ directory for output.")


if __name__ == "__main__":
    test_logging_system()

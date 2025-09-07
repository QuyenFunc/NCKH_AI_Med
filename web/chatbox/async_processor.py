#!/usr/bin/env python3
"""
Async Processing Module
Xử lý bất đồng bộ cho parallel entity extraction và operations
"""
import asyncio
import time
import threading
from typing import List, Dict, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import queue

@dataclass
class ProcessingTask:
    """Task definition for async processing"""
    task_id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: int = 1
    timeout: float = 5.0

@dataclass
class TaskResult:
    """Result of async processing task"""
    task_id: str
    result: Any
    success: bool
    execution_time: float
    error: Optional[str] = None

class AsyncTaskManager:
    """Manager for async task execution"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max_workers//2)
        self.task_queue = queue.PriorityQueue()
        self.results = {}
        self.active_tasks = {}
        self.stats = {
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'total_execution_time': 0.0
        }
    
    def submit_task(self, task: ProcessingTask, use_process: bool = False) -> str:
        """Submit task for async execution"""
        executor = self.process_executor if use_process else self.thread_executor
        
        start_time = time.time()
        future = executor.submit(self._execute_task, task)
        
        self.active_tasks[task.task_id] = {
            'future': future,
            'start_time': start_time,
            'task': task
        }
        
        return task.task_id
    
    def _execute_task(self, task: ProcessingTask) -> TaskResult:
        """Execute individual task"""
        start_time = time.time()
        
        try:
            result = task.function(*task.args, **task.kwargs)
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task.task_id,
                result=result,
                success=True,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return TaskResult(
                task_id=task.task_id,
                result=None,
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
    
    def get_result(self, task_id: str, timeout: float = 5.0) -> Optional[TaskResult]:
        """Get result of submitted task"""
        if task_id not in self.active_tasks:
            return None
        
        try:
            future = self.active_tasks[task_id]['future']
            result = future.result(timeout=timeout)
            
            # Update statistics
            self._update_stats(result)
            
            # Clean up
            del self.active_tasks[task_id]
            
            return result
        
        except Exception as e:
            # Task failed or timed out
            self.stats['failed_tasks'] += 1
            return TaskResult(
                task_id=task_id,
                result=None,
                success=False,
                execution_time=timeout,
                error=f"Timeout or error: {str(e)}"
            )
    
    def get_all_results(self, timeout: float = 10.0) -> Dict[str, TaskResult]:
        """Get all pending task results"""
        results = {}
        
        for task_id in list(self.active_tasks.keys()):
            result = self.get_result(task_id, timeout)
            if result:
                results[task_id] = result
        
        return results
    
    def _update_stats(self, result: TaskResult):
        """Update execution statistics"""
        if result.success:
            self.stats['completed_tasks'] += 1
            self.stats['total_execution_time'] += result.execution_time
            self.stats['avg_execution_time'] = (
                self.stats['total_execution_time'] / self.stats['completed_tasks']
            )
        else:
            self.stats['failed_tasks'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_tasks = self.stats['completed_tasks'] + self.stats['failed_tasks']
        return {
            'total_tasks': total_tasks,
            'completed_tasks': self.stats['completed_tasks'],
            'failed_tasks': self.stats['failed_tasks'],
            'success_rate': self.stats['completed_tasks'] / total_tasks if total_tasks > 0 else 0,
            'avg_execution_time': self.stats['avg_execution_time'],
            'active_tasks': len(self.active_tasks)
        }

class ParallelEntityExtractor:
    """Parallel entity extraction processor"""
    
    def __init__(self, ner_models: List[Any] = None):
        self.ner_models = ner_models or []
        self.task_manager = AsyncTaskManager(max_workers=6)
        self.extraction_cache = {}
    
    def extract_entities_parallel(self, texts: List[str], use_cache: bool = True) -> List[Dict[str, Any]]:
        """Extract entities from multiple texts in parallel"""
        start_time = time.time()
        
        # Prepare tasks
        tasks = []
        cached_results = {}
        
        for i, text in enumerate(texts):
            # Check cache first
            if use_cache:
                text_hash = hash(text)
                if text_hash in self.extraction_cache:
                    cached_results[i] = self.extraction_cache[text_hash]
                    continue
            
            # Create extraction task
            task = ProcessingTask(
                task_id=f"extract_{i}",
                function=self._extract_single_text,
                args=(text,),
                kwargs={},
                priority=1,
                timeout=3.0
            )
            
            tasks.append((i, task))
        
        # Submit tasks
        task_ids = {}
        for text_idx, task in tasks:
            task_id = self.task_manager.submit_task(task)
            task_ids[task_id] = text_idx
        
        # Collect results
        all_results = [None] * len(texts)
        
        # Add cached results
        for idx, result in cached_results.items():
            all_results[idx] = result
        
        # Get async results
        async_results = self.task_manager.get_all_results(timeout=5.0)
        
        for task_id, result in async_results.items():
            text_idx = task_ids[task_id]
            
            if result.success:
                all_results[text_idx] = result.result
                
                # Cache successful result
                if use_cache:
                    text_hash = hash(texts[text_idx])
                    self.extraction_cache[text_hash] = result.result
            else:
                # Fallback to empty result
                all_results[text_idx] = {
                    'entities': [],
                    'confidence': 0.0,
                    'error': result.error
                }
        
        # Handle any None results (failed tasks)
        for i, result in enumerate(all_results):
            if result is None:
                all_results[i] = {
                    'entities': [],
                    'confidence': 0.0,
                    'error': 'Task failed or timed out'
                }
        
        total_time = time.time() - start_time
        print(f"⚡ Parallel entity extraction completed in {total_time:.2f}s")
        
        return all_results
    
    def _extract_single_text(self, text: str) -> Dict[str, Any]:
        """Extract entities from single text"""
        try:
            # Use first available NER model or create dummy
            if self.ner_models:
                ner = self.ner_models[0]
                entities = ner.extract_entities(text)
                context = ner.extract_medical_context(text)
                
                return {
                    'entities': entities,
                    'context': context,
                    'confidence': sum(e.confidence for e in entities) / len(entities) if entities else 0.0
                }
            else:
                # Fallback simple extraction
                return self._simple_entity_extraction(text)
        
        except Exception as e:
            return {
                'entities': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _simple_entity_extraction(self, text: str) -> Dict[str, Any]:
        """Simple fallback entity extraction"""
        text_lower = text.lower()
        
        # Simple keyword matching
        symptoms = ['đau đầu', 'sốt', 'ho', 'buồn nôn', 'chóng mặt', 'mệt mỏi']
        diseases = ['tiểu đường', 'cao huyết áp', 'viêm gan', 'cúm', 'dị ứng']
        
        found_entities = []
        for symptom in symptoms:
            if symptom in text_lower:
                found_entities.append({
                    'text': symptom,
                    'type': 'symptom',
                    'confidence': 0.7
                })
        
        for disease in diseases:
            if disease in text_lower:
                found_entities.append({
                    'text': disease,
                    'type': 'disease',
                    'confidence': 0.8
                })
        
        return {
            'entities': found_entities,
            'confidence': 0.7 if found_entities else 0.0,
            'method': 'simple_extraction'
        }

class ParallelSearchProcessor:
    """Parallel search processing for multiple search strategies"""
    
    def __init__(self, search_engines: List[Any] = None):
        self.search_engines = search_engines or []
        self.task_manager = AsyncTaskManager(max_workers=4)
    
    def parallel_search(self, query: str, search_methods: List[str] = None, 
                       top_k: int = 5) -> Dict[str, List[Dict]]:
        """Execute multiple search methods in parallel"""
        start_time = time.time()
        
        if not search_methods:
            search_methods = ['semantic', 'keyword', 'hybrid']
        
        # Prepare search tasks
        tasks = []
        for method in search_methods:
            task = ProcessingTask(
                task_id=f"search_{method}",
                function=self._execute_search_method,
                args=(query, method, top_k),
                kwargs={},
                priority=1,
                timeout=2.0  # 2s timeout per search
            )
            tasks.append(task)
        
        # Submit tasks
        task_ids = {}
        for task in tasks:
            task_id = self.task_manager.submit_task(task)
            task_ids[task_id] = task.task_id
        
        # Collect results
        search_results = {}
        async_results = self.task_manager.get_all_results(timeout=3.0)
        
        for task_id, result in async_results.items():
            method = task_ids[task_id].split('_')[1]
            
            if result.success:
                search_results[method] = result.result
            else:
                search_results[method] = []
                print(f"⚠️ {method} search failed: {result.error}")
        
        total_time = time.time() - start_time
        print(f"⚡ Parallel search completed in {total_time:.2f}s")
        
        return search_results
    
    def _execute_search_method(self, query: str, method: str, top_k: int) -> List[Dict]:
        """Execute specific search method"""
        try:
            if method == 'semantic' and len(self.search_engines) > 0:
                return self.search_engines[0].semantic_search(query, top_k)
            elif method == 'keyword' and len(self.search_engines) > 0:
                return self.search_engines[0].keyword_search(query, top_k)
            elif method == 'hybrid' and len(self.search_engines) > 0:
                return self.search_engines[0].hybrid_search(query, top_k)
            else:
                # Fallback simple search
                return self._simple_search(query, method, top_k)
        
        except Exception as e:
            print(f"⚠️ Search method {method} failed: {e}")
            return []
    
    def _simple_search(self, query: str, method: str, top_k: int) -> List[Dict]:
        """Simple fallback search"""
        # Return dummy results for testing
        return [
            {
                'text': f'Sample result for {query} using {method}',
                'relevance_score': 0.7,
                'method': method
            }
        ]

class AsyncResponseGenerator:
    """Async response generation and streaming"""
    
    def __init__(self):
        self.task_manager = AsyncTaskManager(max_workers=2)
        self.generation_cache = {}
    
    def generate_response_async(self, context: str, query: str, 
                               use_cache: bool = True) -> str:
        """Generate response asynchronously"""
        # Check cache first
        if use_cache:
            cache_key = hash(f"{context}_{query}")
            if cache_key in self.generation_cache:
                return self.generation_cache[cache_key]
        
        # Create generation task
        task = ProcessingTask(
            task_id="generate_response",
            function=self._generate_single_response,
            args=(context, query),
            kwargs={},
            timeout=5.0
        )
        
        # Submit and wait for result
        task_id = self.task_manager.submit_task(task)
        result = self.task_manager.get_result(task_id, timeout=6.0)
        
        if result and result.success:
            # Cache successful result
            if use_cache:
                cache_key = hash(f"{context}_{query}")
                self.generation_cache[cache_key] = result.result
            
            return result.result
        else:
            return self._fallback_response(query)
    
    def _generate_single_response(self, context: str, query: str) -> str:
        """Generate single response"""
        try:
            # Simple response generation
            if 'đau đầu' in query:
                return "Đau đầu có thể có nhiều nguyên nhân khác nhau. Bạn nên theo dõi triệu chứng và tham khảo ý kiến bác sĩ nếu đau đầu kéo dài hoặc nghiêm trọng."
            elif 'sốt' in query:
                return "Sốt là dấu hiệu cơ thể đang chống lại nhiễm trùng. Bạn nên nghỉ ngơi, uống nhiều nước và theo dõi nhiệt độ."
            else:
                return f"Dựa trên thông tin y tế, {query.lower()} cần được đánh giá cẩn thận. Khuyến nghị tham khảo ý kiến chuyên gia y tế."
        
        except Exception as e:
            raise Exception(f"Response generation failed: {e}")
    
    def _fallback_response(self, query: str) -> str:
        """Fallback response when generation fails"""
        return "Xin lỗi, tôi không thể tạo phản hồi chi tiết lúc này. Vui lòng tham khảo ý kiến bác sĩ để được tư vấn chính xác."

# Factory functions
def get_async_task_manager():
    """Get async task manager instance"""
    return AsyncTaskManager()

def get_parallel_entity_extractor(ner_models=None):
    """Get parallel entity extractor instance"""
    return ParallelEntityExtractor(ner_models)

def get_parallel_search_processor(search_engines=None):
    """Get parallel search processor instance"""
    return ParallelSearchProcessor(search_engines)

def get_async_response_generator():
    """Get async response generator instance"""
    return AsyncResponseGenerator()

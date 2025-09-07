#!/usr/bin/env python3
"""
Chuẩn bị dữ liệu cho RAG (Retrieval-Augmented Generation) system
"""

import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from dataclasses import dataclass

@dataclass
class MedicalDocument:
    """Class để lưu trữ document y tế"""
    id: str
    title: str
    content: str
    category: str
    metadata: Dict
    embedding: np.ndarray = None

class MedicalRAGDataProcessor:
    """Class xử lý dữ liệu cho RAG system y tế"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize với embedding model
        Có thể dùng model Vietnamese: "keepitreal/vietnamese-sbert"
        """
        self.model = SentenceTransformer(model_name)
        self.documents: List[MedicalDocument] = []
        self.index = None
        
    def load_medical_data(self, data_sources: Dict[str, str]) -> List[MedicalDocument]:
        """Load dữ liệu y tế từ nhiều nguồn"""
        documents = []
        
        # Load ICD-10 data
        if "icd10" in data_sources:
            icd_docs = self.process_icd10_data(data_sources["icd10"])
            documents.extend(icd_docs)
        
        # Load PubMed abstracts
        if "pubmed" in data_sources:
            pubmed_docs = self.process_pubmed_data(data_sources["pubmed"])
            documents.extend(pubmed_docs)
        
        # Load symptoms data
        if "symptoms" in data_sources:
            symptom_docs = self.process_symptoms_data(data_sources["symptoms"])
            documents.extend(symptom_docs)
        
        # Load treatment guidelines
        if "treatments" in data_sources:
            treatment_docs = self.process_treatment_data(data_sources["treatments"])
            documents.extend(treatment_docs)
        
        self.documents = documents
        return documents
    
    def process_icd10_data(self, file_path: str) -> List[MedicalDocument]:
        """Xử lý dữ liệu ICD-10"""
        with open(file_path, 'r', encoding='utf-8') as f:
            icd_data = json.load(f)
        
        documents = []
        for item in icd_data:
            # Tạo content từ ICD data
            content = f"""
            Mã bệnh: {item['code']}
            Tên tiếng Anh: {item['name']}
            Tên tiếng Việt: {item.get('vietnamese_name', '')}
            Danh mục: {item.get('category', '')}
            Triệu chứng: {', '.join(item.get('symptoms', []))}
            """
            
            doc = MedicalDocument(
                id=f"icd_{item['code']}",
                title=f"ICD-10: {item['code']} - {item['name']}",
                content=content.strip(),
                category="icd10",
                metadata={
                    "code": item['code'],
                    "category": item.get('category', ''),
                    "symptoms": item.get('symptoms', [])
                }
            )
            documents.append(doc)
        
        return documents
    
    def process_pubmed_data(self, file_path: str) -> List[MedicalDocument]:
        """Xử lý dữ liệu PubMed abstracts"""
        with open(file_path, 'r', encoding='utf-8') as f:
            pubmed_data = json.load(f)
        
        documents = []
        for item in pubmed_data:
            content = f"""
            Tiêu đề: {item.get('title', '')}
            Tóm tắt: {item.get('abstract', '')}
            """
            
            doc = MedicalDocument(
                id=f"pubmed_{item.get('pmid', '')}",
                title=item.get('title', ''),
                content=content.strip(),
                category="research",
                metadata={
                    "pmid": item.get('pmid', ''),
                    "url": item.get('url', '')
                }
            )
            documents.append(doc)
        
        return documents
    
    def process_symptoms_data(self, file_path: str) -> List[MedicalDocument]:
        """Xử lý dữ liệu triệu chứng"""
        with open(file_path, 'r', encoding='utf-8') as f:
            symptoms_data = json.load(f)
        
        documents = []
        for item in symptoms_data:
            content = f"""
            Triệu chứng: {item.get('name', '')} ({item.get('vietnamese_name', '')})
            Mô tả: {item.get('description', '')}
            Nguyên nhân có thể: {', '.join(item.get('possible_causes', []))}
            Khi nào cần gặp bác sĩ: {', '.join(item.get('when_to_see_doctor', []))}
            """
            
            doc = MedicalDocument(
                id=f"symptom_{item.get('name', '').replace(' ', '_').lower()}",
                title=f"Triệu chứng: {item.get('vietnamese_name', item.get('name', ''))}",
                content=content.strip(),
                category="symptoms",
                metadata={
                    "name": item.get('name', ''),
                    "vietnamese_name": item.get('vietnamese_name', ''),
                    "possible_causes": item.get('possible_causes', [])
                }
            )
            documents.append(doc)
        
        return documents
    
    def process_treatment_data(self, file_path: str) -> List[MedicalDocument]:
        """Xử lý dữ liệu điều trị"""
        with open(file_path, 'r', encoding='utf-8') as f:
            treatment_data = json.load(f)
        
        documents = []
        for item in treatment_data:
            content = f"""
            Phương pháp điều trị: {item.get('name', '')}
            Tên tiếng Việt: {item.get('vietnamese_name', '')}
            Áp dụng cho: {', '.join(item.get('applicable_conditions', []))}
            Hướng dẫn: {item.get('instructions', '')}
            """
            
            doc = MedicalDocument(
                id=f"treatment_{item.get('name', '').replace(' ', '_').lower()}",
                title=f"Điều trị: {item.get('vietnamese_name', item.get('name', ''))}",
                content=content.strip(),
                category="treatment",
                metadata={
                    "name": item.get('name', ''),
                    "applicable_conditions": item.get('applicable_conditions', [])
                }
            )
            documents.append(doc)
        
        return documents
    
    def create_embeddings(self) -> np.ndarray:
        """Tạo embeddings cho tất cả documents"""
        print(f"Tạo embeddings cho {len(self.documents)} documents...")
        
        texts = [doc.content for doc in self.documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Lưu embeddings vào documents
        for i, doc in enumerate(self.documents):
            doc.embedding = embeddings[i]
        
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray):
        """Xây dựng FAISS index cho retrieval"""
        dimension = embeddings.shape[1]
        
        # Sử dụng IndexFlatIP cho cosine similarity
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings cho cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        print(f"Đã xây dựng FAISS index với {self.index.ntotal} documents")
    
    def search_similar_documents(self, query: str, top_k: int = 5) -> List[Tuple[MedicalDocument, float]]:
        """Tìm kiếm documents tương tự"""
        if self.index is None:
            raise ValueError("FAISS index chưa được xây dựng")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        
        return results
    
    def save_knowledge_base(self, output_dir: str):
        """Lưu knowledge base"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save documents
        documents_data = []
        for doc in self.documents:
            doc_dict = {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "category": doc.category,
                "metadata": doc.metadata
            }
            documents_data.append(doc_dict)
        
        with open(f"{output_dir}/documents.json", 'w', encoding='utf-8') as f:
            json.dump(documents_data, f, ensure_ascii=False, indent=2)
        
        # Save FAISS index
        if self.index:
            faiss.write_index(self.index, f"{output_dir}/faiss_index.bin")
        
        # Save embeddings
        embeddings = np.array([doc.embedding for doc in self.documents])
        np.save(f"{output_dir}/embeddings.npy", embeddings)
        
        print(f"Đã lưu knowledge base vào {output_dir}")
    
    def load_knowledge_base(self, input_dir: str):
        """Load knowledge base"""
        # Load documents
        with open(f"{input_dir}/documents.json", 'r', encoding='utf-8') as f:
            documents_data = json.load(f)
        
        self.documents = []
        for doc_dict in documents_data:
            doc = MedicalDocument(
                id=doc_dict["id"],
                title=doc_dict["title"],
                content=doc_dict["content"],
                category=doc_dict["category"],
                metadata=doc_dict["metadata"]
            )
            self.documents.append(doc)
        
        # Load embeddings
        embeddings = np.load(f"{input_dir}/embeddings.npy")
        for i, doc in enumerate(self.documents):
            doc.embedding = embeddings[i]
        
        # Load FAISS index
        self.index = faiss.read_index(f"{input_dir}/faiss_index.bin")
        
        print(f"Đã load knowledge base từ {input_dir}")

def main():
    """Main function để xử lý dữ liệu RAG"""
    processor = MedicalRAGDataProcessor()
    
    # Định nghĩa nguồn dữ liệu
    data_sources = {
        "icd10": "icd10_data.json",
        "pubmed": "pubmed_abstracts.json", 
        "symptoms": "symptoms_data.json"
    }
    
    # Load và xử lý dữ liệu
    print("Loading medical data...")
    documents = processor.load_medical_data(data_sources)
    print(f"Loaded {len(documents)} documents")
    
    # Tạo embeddings
    embeddings = processor.create_embeddings()
    
    # Xây dựng FAISS index
    processor.build_faiss_index(embeddings)
    
    # Lưu knowledge base
    processor.save_knowledge_base("medical_knowledge_base")
    
    # Test search
    print("\nTesting search functionality...")
    query = "đau đầu và sốt"
    results = processor.search_similar_documents(query, top_k=3)
    
    print(f"\nQuery: {query}")
    for doc, score in results:
        print(f"Score: {score:.3f} - {doc.title}")
        print(f"Content preview: {doc.content[:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Hướng dẫn thu thập dữ liệu y tế cho RAG system
"""

import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import time
from typing import List, Dict

class MedicalDataCollector:
    """Class để thu thập dữ liệu y tế từ các nguồn khác nhau"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medical Research Bot 1.0'
        })
    
    def collect_icd10_data(self) -> List[Dict]:
        """Thu thập dữ liệu ICD-10"""
        # Sample ICD-10 data structure
        icd_data = [
            {
                "code": "J00",
                "name": "Acute nasopharyngitis [common cold]",
                "vietnamese_name": "Viêm mũi họng cấp [cảm lạnh thường]",
                "symptoms": ["runny nose", "sore throat", "cough"],
                "category": "Respiratory diseases"
            },
            {
                "code": "J11",
                "name": "Influenza due to unidentified influenza virus",
                "vietnamese_name": "Cúm do virus cúm không xác định",
                "symptoms": ["fever", "muscle aches", "headache", "fatigue"],
                "category": "Respiratory diseases"
            }
        ]
        return icd_data
    
    def collect_pubmed_abstracts(self, query: str, max_results: int = 100) -> List[Dict]:
        """Thu thập abstract từ PubMed"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # Search for article IDs
        search_url = f"{base_url}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        try:
            response = self.session.get(search_url, params=search_params)
            search_results = response.json()
            
            ids = search_results.get("esearchresult", {}).get("idlist", [])
            
            # Fetch abstracts
            abstracts = []
            for pmid in ids[:max_results]:
                abstract_data = self.fetch_pubmed_abstract(pmid)
                if abstract_data:
                    abstracts.append(abstract_data)
                time.sleep(0.5)  # Rate limiting
            
            return abstracts
            
        except Exception as e:
            print(f"Error collecting PubMed data: {e}")
            return []
    
    def fetch_pubmed_abstract(self, pmid: str) -> Dict:
        """Lấy abstract từ PubMed ID"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        fetch_url = f"{base_url}efetch.fcgi"
        
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        
        try:
            response = self.session.get(fetch_url, params=params)
            # Parse XML response to extract title, abstract, authors, etc.
            # This is simplified - you'd need proper XML parsing
            return {
                "pmid": pmid,
                "title": "Sample Title",
                "abstract": "Sample Abstract",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
        except Exception as e:
            print(f"Error fetching PMID {pmid}: {e}")
            return None
    
    def collect_mayo_clinic_data(self) -> List[Dict]:
        """Thu thập dữ liệu từ Mayo Clinic (cần tuân thủ robots.txt)"""
        # Lưu ý: Cần kiểm tra robots.txt và terms of service
        symptoms_data = []
        
        # Sample data structure for symptoms
        sample_symptoms = [
            {
                "name": "Headache",
                "vietnamese_name": "Đau đầu",
                "description": "Pain in the head or upper neck",
                "possible_causes": ["tension", "migraine", "cluster headache"],
                "when_to_see_doctor": ["severe sudden headache", "headache with fever"],
                "source": "mayo_clinic"
            }
        ]
        
        return sample_symptoms
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Lưu dữ liệu vào file JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Lưu dữ liệu vào file CSV"""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')

def main():
    """Main function để thu thập dữ liệu"""
    collector = MedicalDataCollector()
    
    print("Thu thập dữ liệu ICD-10...")
    icd_data = collector.collect_icd10_data()
    collector.save_to_json(icd_data, "icd10_data.json")
    
    print("Thu thập dữ liệu PubMed...")
    pubmed_data = collector.collect_pubmed_abstracts("diabetes symptoms diagnosis", 50)
    collector.save_to_json(pubmed_data, "pubmed_abstracts.json")
    
    print("Thu thập dữ liệu triệu chứng...")
    symptoms_data = collector.collect_mayo_clinic_data()
    collector.save_to_json(symptoms_data, "symptoms_data.json")
    
    print("Hoàn thành thu thập dữ liệu!")

if __name__ == "__main__":
    main()


# ================================
# SAMPLE DATA STRUCTURE CHO RAG
# ================================

sample_medical_knowledge_base = {
    "diseases": [
        {
            "id": "disease_001",
            "name": "Common Cold",
            "vietnamese_name": "Cảm lạnh thường",
            "icd_code": "J00",
            "category": "Respiratory",
            "symptoms": [
                {"name": "runny nose", "vietnamese": "chảy nước mũi", "frequency": "very_common"},
                {"name": "sore throat", "vietnamese": "đau họng", "frequency": "common"},
                {"name": "cough", "vietnamese": "ho", "frequency": "common"}
            ],
            "risk_factors": ["cold weather", "weakened immune system"],
            "treatment": ["rest", "fluids", "symptom relief"],
            "duration": "7-10 days",
            "severity": "mild",
            "contagious": True
        }
    ],
    "symptoms": [
        {
            "id": "symptom_001", 
            "name": "fever",
            "vietnamese_name": "sốt",
            "description": "Elevated body temperature above normal",
            "severity_scale": "1-10",
            "associated_diseases": ["flu", "infection", "covid-19"],
            "questions_to_ask": [
                "How high is the fever?",
                "How long have you had fever?",
                "Any other symptoms?"
            ]
        }
    ],
    "treatments": [
        {
            "id": "treatment_001",
            "name": "Rest and hydration",
            "vietnamese_name": "Nghỉ ngơi và bù nước",
            "applicable_conditions": ["common cold", "flu"],
            "instructions": "Get plenty of sleep and drink lots of fluids"
        }
    ]
}


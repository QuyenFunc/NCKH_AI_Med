#!/usr/bin/env python3
"""
Medical Named Entity Recognition (NER) for Vietnamese
Thu nhận thực thể y tế từ text tiếng Việt
"""
import re
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass

@dataclass
class MedicalEntity:
    """Medical entity with metadata"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    synonyms: List[str] = None

class VietnameseMedicalNER:
    """Vietnamese Medical Named Entity Recognition"""
    
    def __init__(self):
        self.entity_patterns = self._build_entity_patterns()
        self.context_patterns = self._build_context_patterns()
        self.exclusion_patterns = self._build_exclusion_patterns()
    
    def _build_entity_patterns(self) -> Dict[str, List[Dict]]:
        """Build medical entity recognition patterns"""
        return {
            'diseases': [
                # Common diseases
                {'pattern': r'\b(tiểu đường|đái tháo đường|diabetes)\b', 'confidence': 0.9, 'synonyms': ['diabetes', 'diabetes mellitus']},
                {'pattern': r'\b(cao huyết áp|tăng huyết áp|huyết áp cao|hypertension)\b', 'confidence': 0.9, 'synonyms': ['hypertension', 'high blood pressure']},
                {'pattern': r'\b(viêm phổi|pneumonia|nhiễm trùng phổi)\b', 'confidence': 0.9, 'synonyms': ['pneumonia']},
                {'pattern': r'\b(viêm gan|hepatitis|nhiễm trùng gan)\b', 'confidence': 0.8, 'synonyms': ['hepatitis']},
                {'pattern': r'\b(ung thư|cancer|carcinoma|khối u ác tính)\b', 'confidence': 0.9, 'synonyms': ['cancer', 'carcinoma']},
                {'pattern': r'\b(tim mạch|cardiovascular|bệnh tim|heart disease)\b', 'confidence': 0.8, 'synonyms': ['cardiovascular disease']},
                {'pattern': r'\b(đột quỵ|stroke|tai biến mạch máu não)\b', 'confidence': 0.9, 'synonyms': ['stroke', 'CVA']},
                {'pattern': r'\b(hen suyễn|asthma|khó thở mãn tính)\b', 'confidence': 0.8, 'synonyms': ['asthma']},
                {'pattern': r'\b(dị ứng|allergy|allergic)\b', 'confidence': 0.7, 'synonyms': ['allergy']},
                {'pattern': r'\b(cúm|influenza|flu)\b', 'confidence': 0.8, 'synonyms': ['influenza', 'flu']},
                {'pattern': r'\b(Covid-19|coronavirus|SARS-CoV-2)\b', 'confidence': 0.9, 'synonyms': ['COVID-19', 'coronavirus']},
                {'pattern': r'\b(sốt xuất huyết|dengue|dengue fever)\b', 'confidence': 0.9, 'synonyms': ['dengue fever']},
                {'pattern': r'\b(viêm dạ dày|gastritis|đau dạ dày)\b', 'confidence': 0.8, 'synonyms': ['gastritis']},
                {'pattern': r'\b(loét dạ dày|peptic ulcer|ulcer)\b', 'confidence': 0.8, 'synonyms': ['peptic ulcer']},
                {'pattern': r'\b(suy thận|kidney failure|renal failure)\b', 'confidence': 0.8, 'synonyms': ['kidney failure']},
                {'pattern': r'\b(sỏi thận|kidney stone|nephrolithiasis)\b', 'confidence': 0.8, 'synonyms': ['kidney stone']},
            ],
            
            'symptoms': [
                # Common symptoms
                {'pattern': r'\b(đau đầu|nhức đầu|headache|cephalgia)\b', 'confidence': 0.8, 'synonyms': ['headache']},
                {'pattern': r'\b(sốt|nóng sốt|fever|pyrexia)\b', 'confidence': 0.9, 'synonyms': ['fever']},
                {'pattern': r'\b(ho|cough|ho khan|ho có đờm)\b', 'confidence': 0.8, 'synonyms': ['cough']},
                {'pattern': r'\b(buồn nôn|nausea|cảm giác nôn)\b', 'confidence': 0.8, 'synonyms': ['nausea']},
                {'pattern': r'\b(nôn|vomiting|ói mửa|emesis)\b', 'confidence': 0.8, 'synonyms': ['vomiting']},
                {'pattern': r'\b(đau bụng|stomach pain|abdominal pain)\b', 'confidence': 0.8, 'synonyms': ['abdominal pain']},
                {'pattern': r'\b(tiêu chảy|diarrhea|đi lỏng|loose stool)\b', 'confidence': 0.8, 'synonyms': ['diarrhea']},
                {'pattern': r'\b(táo bón|constipation|khó đi cầu)\b', 'confidence': 0.8, 'synonyms': ['constipation']},
                {'pattern': r'\b(chóng mặt|dizziness|vertigo|lightheadedness)\b', 'confidence': 0.7, 'synonyms': ['dizziness']},
                {'pattern': r'\b(mệt mỏi|fatigue|exhaustion|tired)\b', 'confidence': 0.6, 'synonyms': ['fatigue']},
                {'pattern': r'\b(khó thở|dyspnea|shortness of breath)\b', 'confidence': 0.8, 'synonyms': ['dyspnea']},
                {'pattern': r'\b(đau ngực|chest pain|thoracic pain)\b', 'confidence': 0.8, 'synonyms': ['chest pain']},
                {'pattern': r'\b(phát ban|rash|skin rash|eruption)\b', 'confidence': 0.7, 'synonyms': ['rash']},
                {'pattern': r'\b(ngứa|itching|pruritus)\b', 'confidence': 0.7, 'synonyms': ['itching']},
                {'pattern': r'\b(sưng|swelling|edema|phù)\b', 'confidence': 0.7, 'synonyms': ['swelling']},
                {'pattern': r'\b(đau lưng|back pain|lumbago)\b', 'confidence': 0.7, 'synonyms': ['back pain']},
                {'pattern': r'\b(đau cổ|neck pain|cervical pain)\b', 'confidence': 0.7, 'synonyms': ['neck pain']},
                {'pattern': r'\b(khàn tiếng|hoarseness|voice hoarse)\b', 'confidence': 0.7, 'synonyms': ['hoarseness']},
                {'pattern': r'\b(nghẹt mũi|nasal congestion|stuffy nose)\b', 'confidence': 0.7, 'synonyms': ['nasal congestion']},
                {'pattern': r'\b(chảy nước mũi|runny nose|rhinorrhea)\b', 'confidence': 0.7, 'synonyms': ['rhinorrhea']},
            ],
            
            'treatments': [
                # Treatments and procedures
                {'pattern': r'\b(thuốc|medication|medicine|drug)\b', 'confidence': 0.6, 'synonyms': ['medication']},
                {'pattern': r'\b(điều trị|treatment|therapy|cure)\b', 'confidence': 0.7, 'synonyms': ['treatment']},
                {'pattern': r'\b(phẫu thuật|surgery|operation|surgical)\b', 'confidence': 0.8, 'synonyms': ['surgery']},
                {'pattern': r'\b(xét nghiệm|test|examination|diagnostic test)\b', 'confidence': 0.7, 'synonyms': ['test']},
                {'pattern': r'\b(vaccine|vaccination|tiêm chủng|immunization)\b', 'confidence': 0.8, 'synonyms': ['vaccination']},
                {'pattern': r'\b(khám bác sĩ|doctor visit|medical consultation)\b', 'confidence': 0.7, 'synonyms': ['medical consultation']},
                {'pattern': r'\b(nghỉ ngơi|rest|bed rest)\b', 'confidence': 0.5, 'synonyms': ['rest']},
                {'pattern': r'\b(chụp X-quang|X-ray|radiography)\b', 'confidence': 0.8, 'synonyms': ['X-ray']},
                {'pattern': r'\b(siêu âm|ultrasound|ultrasonography)\b', 'confidence': 0.8, 'synonyms': ['ultrasound']},
                {'pattern': r'\b(nội soi|endoscopy|endoscopic)\b', 'confidence': 0.8, 'synonyms': ['endoscopy']},
                {'pattern': r'\b(kháng sinh|antibiotic|antimicrobial)\b', 'confidence': 0.8, 'synonyms': ['antibiotic']},
                {'pattern': r'\b(giảm đau|pain relief|analgesic|painkiller)\b', 'confidence': 0.7, 'synonyms': ['pain relief']},
            ],
            
            'body_parts': [
                # Body parts and organs
                {'pattern': r'\b(tim|heart|cardiac)\b', 'confidence': 0.8, 'synonyms': ['heart']},
                {'pattern': r'\b(gan|liver|hepatic)\b', 'confidence': 0.8, 'synonyms': ['liver']},
                {'pattern': r'\b(thận|kidney|renal)\b', 'confidence': 0.8, 'synonyms': ['kidney']},
                {'pattern': r'\b(phổi|lung|pulmonary)\b', 'confidence': 0.8, 'synonyms': ['lung']},
                {'pattern': r'\b(dạ dày|stomach|gastric)\b', 'confidence': 0.8, 'synonyms': ['stomach']},
                {'pattern': r'\b(ruột|intestine|bowel)\b', 'confidence': 0.7, 'synonyms': ['intestine']},
                {'pattern': r'\b(não|brain|cerebral)\b', 'confidence': 0.8, 'synonyms': ['brain']},
                {'pattern': r'\b(xương|bone|skeletal)\b', 'confidence': 0.7, 'synonyms': ['bone']},
                {'pattern': r'\b(máu|blood|hematic)\b', 'confidence': 0.7, 'synonyms': ['blood']},
                {'pattern': r'\b(da|skin|cutaneous)\b', 'confidence': 0.6, 'synonyms': ['skin']},
            ],
            
            'medications': [
                # Common medication types
                {'pattern': r'\b(paracetamol|acetaminophen|tylenol)\b', 'confidence': 0.9, 'synonyms': ['paracetamol']},
                {'pattern': r'\b(aspirin|acetylsalicylic acid)\b', 'confidence': 0.9, 'synonyms': ['aspirin']},
                {'pattern': r'\b(ibuprofen|advil|motrin)\b', 'confidence': 0.9, 'synonyms': ['ibuprofen']},
                {'pattern': r'\b(metformin|glucophage)\b', 'confidence': 0.9, 'synonyms': ['metformin']},
                {'pattern': r'\b(insulin|insulin therapy)\b', 'confidence': 0.9, 'synonyms': ['insulin']},
                {'pattern': r'\b(amoxicillin|amoxil)\b', 'confidence': 0.9, 'synonyms': ['amoxicillin']},
                {'pattern': r'\b(vitamin|vitamin supplement)\b', 'confidence': 0.7, 'synonyms': ['vitamin']},
            ]
        }
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """Build context patterns to improve recognition"""
        return {
            'medical_context': [
                r'\b(bệnh|disease|disorder)\b',
                r'\b(triệu chứng|symptom|sign)\b', 
                r'\b(điều trị|treatment|therapy)\b',
                r'\b(chẩn đoán|diagnosis|diagnostic)\b',
                r'\b(bác sĩ|doctor|physician)\b',
                r'\b(bệnh viện|hospital|clinic)\b',
                r'\b(y tế|medical|health)\b'
            ],
            'temporal_context': [
                r'\b(hôm qua|yesterday)\b',
                r'\b(hôm nay|today)\b',
                r'\b(tuần trước|last week)\b',
                r'\b(lâu rồi|long time)\b',
                r'\b(vừa rồi|just now)\b'
            ]
        }
    
    def _build_exclusion_patterns(self) -> List[str]:
        """Build patterns for non-medical entities to exclude"""
        return [
            r'\b(tên|name|tôi|I|bạn|you)\b',
            r'\b(nhà|house|xe|car|tiền|money)\b',
            r'\b(ăn|eat|uống|drink|ngủ|sleep)\b',
            r'\b(làm việc|work|học|study)\b'
        ]
    
    def extract_entities(self, text: str) -> List[MedicalEntity]:
        """Extract medical entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Check if text has medical context
        has_medical_context = any(
            re.search(pattern, text_lower) 
            for pattern in self.context_patterns['medical_context']
        )
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                base_confidence = pattern_info['confidence']
                synonyms = pattern_info.get('synonyms', [])
                
                # Find matches
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                
                for match in matches:
                    entity_text = match.group()
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Skip if matches exclusion patterns
                    if any(re.search(excl_pattern, entity_text) for excl_pattern in self.exclusion_patterns):
                        continue
                    
                    # Adjust confidence based on context
                    confidence = base_confidence
                    if has_medical_context:
                        confidence = min(confidence * 1.2, 1.0)
                    
                    # Check for temporal context
                    surrounding_text = text_lower[max(0, start_pos-50):end_pos+50]
                    has_temporal = any(
                        re.search(pattern, surrounding_text)
                        for pattern in self.context_patterns['temporal_context']
                    )
                    
                    if has_temporal:
                        confidence = min(confidence * 1.1, 1.0)
                    
                    entity = MedicalEntity(
                        text=entity_text,
                        entity_type=entity_type,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=confidence,
                        synonyms=synonyms
                    )
                    
                    entities.append(entity)
        
        # Remove overlapping entities (keep higher confidence)
        entities = self._remove_overlapping_entities(entities)
        
        # Sort by position
        entities.sort(key=lambda e: e.start_pos)
        
        return entities
    
    def _remove_overlapping_entities(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Remove overlapping entities, keeping higher confidence ones"""
        if not entities:
            return entities
        
        # Sort by confidence (descending)
        entities_sorted = sorted(entities, key=lambda e: e.confidence, reverse=True)
        
        filtered_entities = []
        used_positions = set()
        
        for entity in entities_sorted:
            # Check if this entity overlaps with any already selected
            entity_positions = set(range(entity.start_pos, entity.end_pos))
            
            if not entity_positions.intersection(used_positions):
                filtered_entities.append(entity)
                used_positions.update(entity_positions)
        
        return filtered_entities
    
    def extract_medical_context(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive medical context from text"""
        entities = self.extract_entities(text)
        
        context = {
            'entities': entities,
            'entity_types': {},
            'medical_domain': self._identify_medical_domain(entities),
            'urgency_level': self._assess_urgency(text, entities),
            'entity_relationships': self._find_entity_relationships(text, entities)
        }
        
        # Group entities by type
        for entity in entities:
            if entity.entity_type not in context['entity_types']:
                context['entity_types'][entity.entity_type] = []
            context['entity_types'][entity.entity_type].append(entity)
        
        return context
    
    def _identify_medical_domain(self, entities: List[MedicalEntity]) -> str:
        """Identify primary medical domain based on entities"""
        domain_keywords = {
            'cardiology': ['tim', 'heart', 'cardiac', 'cardiovascular'],
            'gastroenterology': ['dạ dày', 'ruột', 'stomach', 'intestine', 'gastric'],
            'neurology': ['não', 'brain', 'đau đầu', 'headache', 'neurological'],
            'respiratory': ['phổi', 'lung', 'ho', 'cough', 'khó thở', 'dyspnea'],
            'endocrinology': ['tiểu đường', 'diabetes', 'hormone'],
            'infectious_disease': ['viêm', 'infection', 'virus', 'bacteria'],
            'emergency': ['cấp cứu', 'emergency', 'nguy hiểm', 'urgent']
        }
        
        domain_scores = {}
        for entity in entities:
            for domain, keywords in domain_keywords.items():
                score = sum(1 for keyword in keywords if keyword in entity.text.lower())
                domain_scores[domain] = domain_scores.get(domain, 0) + score
        
        return max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else 'general'
    
    def _assess_urgency(self, text: str, entities: List[MedicalEntity]) -> str:
        """Assess urgency level based on text and entities"""
        emergency_keywords = ['cấp cứu', 'emergency', 'nguy hiểm', 'nghiêm trọng', 'acute', 'severe']
        urgent_symptoms = ['đau ngực', 'chest pain', 'khó thở', 'dyspnea', 'bất tỉnh', 'unconscious']
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in emergency_keywords):
            return 'high'
        
        if any(symptom in text_lower for symptom in urgent_symptoms):
            return 'medium'
        
        return 'low'
    
    def _find_entity_relationships(self, text: str, entities: List[MedicalEntity]) -> List[Dict[str, Any]]:
        """Find relationships between entities"""
        relationships = []
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Calculate distance between entities
                distance = abs(entity1.start_pos - entity2.start_pos)
                
                # If entities are close, they might be related
                if distance < 50:  # Within 50 characters
                    relationship_type = self._determine_relationship_type(entity1, entity2)
                    if relationship_type:
                        relationships.append({
                            'entity1': entity1,
                            'entity2': entity2,
                            'relationship_type': relationship_type,
                            'confidence': min(entity1.confidence, entity2.confidence)
                        })
        
        return relationships
    
    def _determine_relationship_type(self, entity1: MedicalEntity, entity2: MedicalEntity) -> str:
        """Determine relationship type between two entities"""
        type1, type2 = entity1.entity_type, entity2.entity_type
        
        relationship_map = {
            ('diseases', 'symptoms'): 'causes',
            ('symptoms', 'diseases'): 'indicates',
            ('diseases', 'treatments'): 'treated_by',
            ('treatments', 'diseases'): 'treats',
            ('symptoms', 'treatments'): 'relieved_by',
            ('treatments', 'symptoms'): 'relieves',
            ('diseases', 'body_parts'): 'affects',
            ('body_parts', 'diseases'): 'affected_by',
            ('medications', 'diseases'): 'prescribed_for',
            ('diseases', 'medications'): 'treated_with'
        }
        
        return relationship_map.get((type1, type2))

# Factory function
def get_medical_ner():
    """Get medical NER instance"""
    return VietnameseMedicalNER()

import requests
from requests.auth import HTTPBasicAuth
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import json
from datetime import datetime
import time
import csv
import os

class ICDMmsDataProcessor:
    """Lớp xử lý dữ liệu ICD-11 MMS Linearization cho RAG Chatbot chẩn đoán"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.icd_api_base = "https://id.who.int/icd"
        self.access_token = None
        self.token_expires_at = None
        
    def get_access_token(self):
        """Lấy access token từ WHO ICD API"""
        try:
            print("🔐 Đang lấy access token từ WHO ICD API...")
            
            data = {
                "grant_type": "client_credentials",
                "scope": "icdapi_access"
            }
            
            response = requests.post(
                self.token_url, 
                data=data, 
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            # Token thường có hiệu lực 1 giờ
            self.token_expires_at = datetime.now().timestamp() + token_data.get("expires_in", 3600)
            
            print("✅ Đã lấy access token thành công")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi lấy access token: {e}")
            return False
    
    def is_token_valid(self):
        """Kiểm tra token có còn hiệu lực không"""
        if not self.access_token:
            return False
        return datetime.now().timestamp() < (self.token_expires_at - 300)  # Refresh 5 phút trước khi hết hạn
    
    def get_headers(self):
        """Lấy headers cho API request"""
        if not self.is_token_valid():
            self.get_access_token()
            
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "API-Version": "v2",
            "Accept-Language": "en"
        }
    
    def get_icd_entity(self, entity_uri, retries=3):
        """Lấy thông tin entity từ ICD API với retry logic"""
        headers = self.get_headers()
        
        for attempt in range(retries):
            try:
                response = requests.get(entity_uri, headers=headers, verify=False, timeout=15)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Lỗi attempt {attempt+1} khi gọi {entity_uri}: {e}")
                if attempt < retries - 1:
                    time.sleep(1 * (attempt + 1))
                else:
                    print(f"❌ Không thể lấy dữ liệu từ {entity_uri} sau {retries} lần thử")
        
        return None
    
    def extract_medical_text_for_rag(self, entity_data, entity_uri=""):
        """Trích xuất CHỈ những trường QUAN TRỌNG cho RAG chatbot chẩn đoán bệnh"""
        text_parts = []
        
        try:
            # 1. TITLE - Tên bệnh (BẮT BUỘC)
            title = entity_data.get('title', {})
            if isinstance(title, dict) and '@value' in title:
                text_parts.append(f"Tên bệnh: {title['@value']}")
            
            # 2. CODE - Mã ICD-11 (QUAN TRỌNG NHẤT)
            code = entity_data.get('code')
            if code:
                text_parts.append(f"Mã ICD: {code}")
            
            # 3. DEFINITION - Định nghĩa bệnh (QUAN TRỌNG)
            definition = entity_data.get('definition', {})
            if isinstance(definition, dict) and '@value' in definition:
                text_parts.append(f"Định nghĩa: {definition['@value']}")
            
            # 4. DIAGNOSTIC CRITERIA - Tiêu chí chẩn đoán (RẤT QUAN TRỌNG cho AI)
            diagnostic_criteria = entity_data.get('diagnosticCriteria', {})
            if isinstance(diagnostic_criteria, dict) and '@value' in diagnostic_criteria:
                text_parts.append(f"Tiêu chí chẩn đoán: {diagnostic_criteria['@value']}")
            
            # 5. INDEX TERMS - Thuật ngữ tìm kiếm (QUAN TRỌNG cho RAG search)
            index_terms = entity_data.get('indexTerm', [])
            if index_terms:
                terms = []
                for term in index_terms[:5]:  # Chỉ lấy 5 terms đầu
                    if isinstance(term, dict):
                        label = term.get('label', {})
                        if isinstance(label, dict) and '@value' in label:
                            terms.append(label['@value'])
                
                if terms:
                    text_parts.append(f"Thuật ngữ liên quan: {', '.join(terms)}")
            
            # 6. INCLUSION - Bao gồm (Giúp AI hiểu rõ hơn)
            inclusions = entity_data.get('inclusion', [])
            if inclusions:
                inc_terms = []
                for inc in inclusions[:3]:  # Chỉ lấy 3 inclusion đầu
                    if isinstance(inc, dict):
                        label = inc.get('label', {})
                        if isinstance(label, dict) and '@value' in label:
                            inc_terms.append(label['@value'])
                
                if inc_terms:
                    text_parts.append(f"Bao gồm: {', '.join(inc_terms)}")
            
            # 7. EXCLUSION - Loại trừ (Giúp AI phân biệt)
            exclusions = entity_data.get('exclusion', [])
            if exclusions:
                exc_terms = []
                for exc in exclusions[:3]:  # Chỉ lấy 3 exclusion đầu
                    if isinstance(exc, dict):
                        label = exc.get('label', {})
                        if isinstance(label, dict) and '@value' in label:
                            exc_terms.append(label['@value'])
                
                if exc_terms:
                    text_parts.append(f"Loại trừ: {', '.join(exc_terms)}")
            
            # Thêm Browser URL để truy cập trực tiếp
            browser_url = entity_data.get('browserUrl')
            if browser_url:
                text_parts.append(f"🔗 Xem chi tiết: {browser_url}")
            
            # Chỉ trả về nếu có ít nhất title và một trường quan trọng khác
            if len(text_parts) >= 2:
                return "\n".join(text_parts)
            else:
                return None  # Skip entities không đủ thông tin
            
        except Exception as e:
            print(f"❌ Lỗi khi trích xuất: {e}")
            return None
    
    def create_rag_chunks_with_metadata(self, entity_data, entity_uri, text_splitter):
        """Tạo chunks với metadata chi tiết cho RAG system"""
        chunks_with_metadata = []
        
        try:
            # Trích xuất metadata cơ bản
            title = entity_data.get('title', {})
            entity_name = title.get('@value', 'Unknown') if isinstance(title, dict) else str(title)
            
            # Lấy code từ URI nếu có
            entity_code = entity_uri.split('/')[-1] if entity_uri else None
            
            # Trích xuất text cho RAG
            entity_text = self.extract_medical_text_for_rag(entity_data, entity_uri)
            
            # Chia thành chunks
            text_chunks = text_splitter.split_text(entity_text)
            
            for i, chunk in enumerate(text_chunks):
                chunk_metadata = {
                    'source_type': 'icd_entity',
                    'entity_name': entity_name,
                    'entity_uri': entity_uri,
                    'entity_code': entity_code,
                    'data_type': 'medical_diagnosis',
                    'chunk_index': i,
                    'chunk_size': len(chunk),
                    'total_chunks': len(text_chunks),
                    'fetch_timestamp': datetime.now().isoformat(),
                    'entity_type': 'medical_condition',
                    'chunk_type': 'diagnosis_info',
                    # Thông tin chất lượng dữ liệu cho RAG
                    'has_definition': bool(entity_data.get('definition', {}).get('@value')),
                    'has_diagnostic_criteria': bool(entity_data.get('diagnosticCriteria', {}).get('@value')),
                    'has_icd_code': bool(entity_data.get('code')),
                    'has_index_terms': bool(entity_data.get('indexTerm')),
                    'has_inclusions': bool(entity_data.get('inclusion')),
                    'has_exclusions': bool(entity_data.get('exclusion')),
                    'browser_url': entity_data.get('browserUrl', ''),
                    'quality_score': self.calculate_quality_score(entity_data)
                }
                
                chunks_with_metadata.append({
                    'text': chunk,
                    'metadata': chunk_metadata
                })
            
            return chunks_with_metadata
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo RAG chunks: {e}")
            return []
    
    def calculate_quality_score(self, entity_data):
        """Tính điểm chất lượng dữ liệu cho RAG (0-100)"""
        score = 0
        
        # Title (bắt buộc) - 20 điểm
        if entity_data.get('title', {}).get('@value'):
            score += 20
        
        # ICD Code (rất quan trọng) - 25 điểm
        if entity_data.get('code'):
            score += 25
        
        # Definition (quan trọng) - 20 điểm
        if entity_data.get('definition', {}).get('@value'):
            score += 20
        
        # Diagnostic Criteria (rất quan trọng cho AI) - 25 điểm
        if entity_data.get('diagnosticCriteria', {}).get('@value'):
            score += 25
        
        # Index Terms (hữu ích cho tìm kiếm) - 5 điểm
        if entity_data.get('indexTerm'):
            score += 5
        
        # Inclusion/Exclusion (hữu ích) - 3 điểm
        if entity_data.get('inclusion') or entity_data.get('exclusion'):
            score += 3
        
        # Browser URL (tiện ích) - 2 điểm
        if entity_data.get('browserUrl'):
            score += 2
        
        return min(score, 100)  # Giới hạn 100 điểm
    
    def load_existing_entities(self, filename="mms_entities_progress.pkl"):
        """Load danh sách entities đã lấy từ file progress"""
        try:
            # Đảm bảo tìm file trong thư mục chatbox/data
            if not filename.startswith('chatbox/') and not os.path.isabs(filename):
                filename = os.path.join(os.path.dirname(__file__), 'data', filename)
                
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    progress_data = pickle.load(f)
                    return progress_data.get('seen_uris', set()), progress_data.get('all_entities', [])
        except Exception as e:
            print(f"⚠️ Không thể load progress file: {e}")
        return set(), []
    
    def get_next_batch_number(self):
        """Tính số batch tiếp theo dựa trên số batch files đã có"""
        current_dir = os.path.join(os.path.dirname(__file__), 'data')
        batch_number = 1
        
        while True:
            batch_filename = f"mms_batch_{batch_number:03d}.pkl"
            batch_filepath = os.path.join(current_dir, batch_filename)
            if os.path.exists(batch_filepath):
                batch_number += 1
            else:
                break
        
        return batch_number
    
    def save_progress(self, seen_uris, all_entities, filename="mms_entities_progress.pkl"):
        """Lưu progress sau mỗi batch"""
        try:
            # Đảm bảo file được lưu trong thư mục chatbox/data
            if not filename.startswith('chatbox/') and not os.path.isabs(filename):
                filename = os.path.join(os.path.dirname(__file__), 'data', filename)
                
            progress_data = {
                'seen_uris': seen_uris,
                'all_entities': all_entities,
                'last_update': datetime.now().isoformat(),
                'total_entities': len(all_entities)
            }
            with open(filename, "wb") as f:
                pickle.dump(progress_data, f)
            print(f"💾 Đã lưu progress: {len(all_entities)} entities")
        except Exception as e:
            print(f"❌ Lỗi khi lưu progress: {e}")
    
    def is_token_expired(self, response):
        """Kiểm tra token có hết hạn không"""
        if response.status_code == 401:
            return True
        return False
    
    def get_headers_with_refresh(self):
        """Lấy headers và tự động refresh token nếu hết hạn"""
        headers = self.get_headers()
        return headers
    
    def get_icd_entity_with_retry(self, entity_uri, retries=3):
        """Lấy thông tin entity với retry và token refresh"""
        for attempt in range(retries):
            try:
                headers = self.get_headers_with_refresh()
                response = requests.get(entity_uri, headers=headers, verify=False, timeout=15)
                
                # Nếu token hết hạn, refresh và thử lại
                if self.is_token_expired(response):
                    print(f"⚠️ Token hết hạn, đang refresh...")
                    if self.get_access_token():
                        headers = self.get_headers_with_refresh()
                        response = requests.get(entity_uri, headers=headers, verify=False, timeout=15)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Lỗi attempt {attempt+1} khi gọi {entity_uri}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"❌ Không thể lấy dữ liệu từ {entity_uri} sau {retries} lần thử")
        
        return None
    
    def get_mms_releases(self):
        """Lấy danh sách tất cả các release từ MMS"""
        try:
            mms_url = f"{self.icd_api_base}/release/11/mms"
            print(f"🔍 Lấy danh sách releases từ: {mms_url}")
            
            data = self.get_icd_entity_with_retry(mms_url)
            if not data:
                return []
            
            releases = data.get('release', [])
            latest_release = data.get('latestRelease')
            
            print(f"✅ Tìm thấy {len(releases)} releases")
            print(f"✅ Latest release: {latest_release}")
            
            # Sử dụng latest release hoặc fallback
            if latest_release:
                return [latest_release]
            elif releases:
                return [releases[0]]  # Lấy release đầu tiên
            else:
                return []
                
        except Exception as e:
            print(f"❌ Lỗi khi lấy MMS releases: {e}")
            return []
    
    def get_release_children(self, release_url):
        """Lấy các children từ một release cụ thể"""
        try:
            print(f"🔍 Lấy children từ release: {release_url}")
            
            data = self.get_icd_entity_with_retry(release_url)
            if not data:
                return []
            
            children = data.get('child', [])
            print(f"✅ Tìm thấy {len(children)} children trong release")
            
            return children
            
        except Exception as e:
            print(f"❌ Lỗi khi lấy children từ release: {e}")
            return []
    
    
    def fetch_entities_for_rag(self, batch_size=100, max_depth=10):
        """Lấy TOÀN BỘ entities từ ICD API với batch processing và resume capability"""
        print("🌍 Bắt đầu lấy TOÀN BỘ dữ liệu ICD cho RAG (không giới hạn)")
        print(f"📦 Batch size: {batch_size} entities")
        print(f"🔄 Max depth: {max_depth}")
        
        # Load progress từ lần chạy trước (nếu có)
        seen_uris, all_entities = self.load_existing_entities()
        start_count = len(all_entities)
        
        if start_count > 0:
            print(f"🔄 Resume từ lần chạy trước: đã có {start_count} entities")
        
        # Lấy các release và children theo đúng flow API
        releases = self.get_mms_releases()
        if not releases:
            print("❌ Không thể lấy MMS releases")
            return all_entities
        
        # Lấy children từ tất cả releases
        start_uris = []
        for release_url in releases:
            children = self.get_release_children(release_url)
            start_uris.extend(children)
        
        # Tạo queue từ release children chưa được xử lý
        queue = [(uri, 0) for uri in start_uris if uri not in seen_uris]
        
        # Thêm tất cả children chưa được xử lý từ các entities đã có
        unprocessed_children_count = 0
        for entity in all_entities:
            entity_data = entity.get('data', {})
            entity_depth = entity.get('depth', 0)
            
            if 'child' in entity_data and entity_depth < max_depth:
                for child_uri in entity_data['child']:
                    if child_uri not in seen_uris:
                        queue.append((child_uri, entity_depth + 1))
                        unprocessed_children_count += 1
        
        print(f"🎯 Sẽ bắt đầu từ {len(queue)} URIs:")
        print(f"   - Release children chưa xử lý: {len([uri for uri, depth in queue if depth == 0])}")
        print(f"   - Entity children chưa xử lý: {unprocessed_children_count}")
        
        # Tính batch_count dựa trên số batch files đã có
        batch_count = self.get_next_batch_number()
        entities_in_current_batch = []
        
        while queue:
            current_uri, depth = queue.pop(0)
            
            if current_uri in seen_uris or depth > max_depth:
                continue
                
            print(f"📡 Lấy: {current_uri} (depth: {depth}, total: {len(all_entities)})")
            entity_data = self.get_icd_entity_with_retry(current_uri)
            
            if entity_data:
                entity_item = {
                    'uri': current_uri,
                    'data': entity_data,
                    'depth': depth,
                    'timestamp': datetime.now().isoformat()
                }
                
                all_entities.append(entity_item)
                entities_in_current_batch.append(entity_item)
                seen_uris.add(current_uri)
                
                # Thêm children vào queue
                if depth < max_depth and 'child' in entity_data:
                    for child_uri in entity_data['child']:
                        if child_uri not in seen_uris:
                            queue.append((child_uri, depth + 1))
                
                title = entity_data.get('title', {}).get('@value', 'Unknown')
                print(f"✅ Đã lấy: {title}")
                
                # Kiểm tra nếu đủ batch size thì lưu progress
                if len(entities_in_current_batch) >= batch_size:
                    print(f"\n💾 Lưu batch #{batch_count} ({batch_size} entities)")
                    self.save_progress(seen_uris, all_entities)
                    
                    # Tạo embeddings và lưu cho batch này
                    self.process_and_save_batch(entities_in_current_batch, batch_count)
                    
                    entities_in_current_batch = []
                    batch_count += 1  # Tăng batch_count sau khi lưu
                    print(f"📊 Tổng tiến độ: {len(all_entities)} entities, {len(queue)} còn lại trong queue\n")
                
                # Delay để tránh rate limiting
                time.sleep(0.3)
            else:
                print(f"❌ Không thể lấy: {current_uri}")
        
        # Xử lý batch cuối cùng (nếu có)
        if entities_in_current_batch:
            print(f"\n💾 Lưu batch cuối #{batch_count} ({len(entities_in_current_batch)} entities)")
            self.save_progress(seen_uris, all_entities)
            self.process_and_save_batch(entities_in_current_batch, batch_count)
        
        print(f"\n🎉 HOÀN THÀNH! Đã lấy tổng cộng {len(all_entities)} entities")
        print(f"📈 Tăng từ {start_count} lên {len(all_entities)} entities")
        
        return all_entities
    
    def process_and_save_batch(self, batch_entities, batch_number):
        """Xử lý và lưu một batch entities"""
        try:
            print(f"🔄 Đang xử lý batch #{batch_number}...")
            
            # Khởi tạo text splitter và embedder nếu chưa có
            if not hasattr(self, 'text_splitter'):
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, chunk_overlap=50
                )
            
            if not hasattr(self, 'embedder'):
                try:
                    self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                except:
                    print("⚠️ Không thể load embedder cho batch processing")
                    return
            
            # Tạo chunks cho batch này (chỉ lấy entities có đủ thông tin)
            batch_chunks = []
            valid_entities = 0
            
            for entity_item in batch_entities:
                try:
                    # Kiểm tra xem entity có đủ thông tin không
                    entity_text = self.extract_medical_text_for_rag(entity_item['data'], entity_item['uri'])
                    if entity_text:  # Chỉ xử lý nếu có thông tin hữu ích
                        chunks = self.create_rag_chunks_with_metadata(
                            entity_item['data'], 
                            entity_item['uri'], 
                            self.text_splitter
                        )
                        batch_chunks.extend(chunks)
                        valid_entities += 1
                    else:
                        print(f"⚠️ Skip entity không đủ thông tin: {entity_item['uri']}")
                        
                except Exception as e:
                    print(f"❌ Lỗi xử lý entity {entity_item['uri']}: {e}")
            
            print(f"✅ Xử lý {valid_entities}/{len(batch_entities)} entities hữu ích trong batch #{batch_number}")
            
            if batch_chunks:
                # Tạo embeddings cho batch
                texts = [chunk['text'] for chunk in batch_chunks]
                embeddings = self.embedder.encode(texts, convert_to_numpy=True)
                
                # Lưu batch data
                batch_data = {
                    'batch_number': batch_number,
                    'chunks': batch_chunks,
                    'embeddings': embeddings,
                    'entities_count': len(batch_entities),
                    'chunks_count': len(batch_chunks),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Đảm bảo batch file được lưu trong thư mục chatbox/data
                batch_filename = f"mms_batch_{batch_number:03d}.pkl"
                batch_filepath = os.path.join(os.path.dirname(__file__), 'data', batch_filename)
                
                with open(batch_filepath, "wb") as f:
                    pickle.dump(batch_data, f)
                
                print(f"✅ Đã lưu batch #{batch_number}: {len(batch_chunks)} chunks từ {valid_entities} entities vào {batch_filename}")
            
        except Exception as e:
            print(f"❌ Lỗi khi xử lý batch #{batch_number}: {e}")
    
    def combine_all_batches(self):
        """Kết hợp tất cả các batch files thành file cuối cùng"""
        print("🔄 Đang kết hợp tất cả các batch files...")
        
        # Tìm tất cả batch files trong thư mục chatbox/data
        batch_files = []
        batch_number = 1
        current_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        while True:
            batch_filename = f"mms_batch_{batch_number:03d}.pkl"
            batch_filepath = os.path.join(current_dir, batch_filename)
            if os.path.exists(batch_filepath):
                batch_files.append(batch_filepath)
                batch_number += 1
            else:
                break
        
        if not batch_files:
            print("❌ Không tìm thấy batch files nào")
            return None
        
        print(f"📁 Tìm thấy {len(batch_files)} batch files")
        
        # Kết hợp tất cả chunks và embeddings
        all_chunks = []
        all_embeddings = []
        total_entities = 0
        
        for batch_file in batch_files:
            try:
                print(f"📖 Đang đọc {batch_file}...")
                with open(batch_file, "rb") as f:
                    batch_data = pickle.load(f)
                
                all_chunks.extend(batch_data['chunks'])
                all_embeddings.append(batch_data['embeddings'])
                total_entities += batch_data['entities_count']
                
                print(f"✅ Đã đọc {batch_data['chunks_count']} chunks từ {batch_file}")
                
            except Exception as e:
                print(f"❌ Lỗi khi đọc {batch_file}: {e}")
                continue
        
        if not all_chunks:
            print("❌ Không có chunks nào để kết hợp")
            return None
        
        # Kết hợp embeddings
        print("🔄 Đang kết hợp embeddings...")
        combined_embeddings = np.vstack(all_embeddings)
        
        # Tạo metadata list
        texts = [chunk['text'] for chunk in all_chunks]
        metadata_list = [chunk['metadata'] for chunk in all_chunks]
        
        # Tạo final chunks data
        final_chunks_data = {
            'chunks': all_chunks,
            'texts': texts,
            'metadata': metadata_list,
            'created_at': datetime.now().isoformat(),
            'total_chunks': len(all_chunks),
            'total_entities': total_entities,
            'data_source': 'who_icd_api_comprehensive',
            'data_type': 'medical_rag_full',
            'batch_count': len(batch_files)
        }
        
        # Lưu final chunks data trong thư mục chatbox/data
        current_dir = os.path.join(os.path.dirname(__file__), 'data')
        chunks_filepath = os.path.join(current_dir, "medical_chunks_with_metadata.pkl")
        index_filepath = os.path.join(current_dir, "medical_faiss_index.index")
        
        with open(chunks_filepath, "wb") as f:
            pickle.dump(final_chunks_data, f)
        print("✅ Đã lưu final chunks data vào medical_chunks_with_metadata.pkl")
        
        # Tạo và lưu FAISS index
        print("🔄 Đang tạo FAISS index...")
        dimension = combined_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(combined_embeddings)
        faiss.write_index(index, index_filepath)
        print("✅ Đã lưu FAISS index vào medical_faiss_index.index")
        
        print(f"\n🎉 HOÀN THÀNH KẾT HỢP!")
        print(f"📊 Thống kê cuối cùng:")
        print(f"   - Tổng số entities: {total_entities}")
        print(f"   - Tổng số chunks: {len(all_chunks)}")
        print(f"   - Kích thước embedding: {dimension}")
        print(f"   - Số batch files: {len(batch_files)}")
        
        return {
            'success': True,
            'total_chunks': len(all_chunks),
            'total_entities': total_entities,
            'embedding_dimension': dimension,
            'batch_count': len(batch_files),
            'chunks_file': 'medical_chunks_with_metadata.pkl',
            'index_file': 'medical_faiss_index.index'
        }

def setup_icd_rag_system(client_id, client_secret, batch_size=100, combine_batches=True):
    """
    Thiết lập RAG system với TOÀN BỘ dữ liệu ICD-11 (không giới hạn)
    
    Args:
        client_id: WHO ICD API client ID
        client_secret: WHO ICD API client secret  
        batch_size: Số entities xử lý mỗi batch (default: 100)
        combine_batches: Có kết hợp các batch thành file cuối không (default: True)
    """
    print("🏥 Bắt đầu thiết lập ICD RAG System...")
    
    # Khởi tạo processor
    processor = ICDMmsDataProcessor(client_id, client_secret)
    
    # Lấy access token
    if not processor.get_access_token():
        print("❌ Không thể lấy access token. Dừng setup.")
        return None
    
    # Khởi tạo embedding model
    print("🔄 Đang tải SentenceTransformer model...")
    try:
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Đã tải embedding model thành công")
    except Exception as e:
        print(f"❌ Lỗi khi tải embedding model: {e}")
        return None
    
    # Khởi tạo text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    
    # Lấy TOÀN BỘ dữ liệu từ ICD API (không giới hạn)
    entities_data = processor.fetch_entities_for_rag(batch_size=batch_size)
    
    # Dữ liệu đã được xử lý theo batch trong fetch_entities_for_rag
    print(f"✅ Đã lấy {len(entities_data)} entities với batch processing")
    
    # Kiểm tra xem còn dữ liệu để xử lý không
    seen_uris, _ = processor.load_existing_entities()
    
    # Đếm children chưa được xử lý
    unprocessed_count = 0
    for entity in entities_data:
        entity_data = entity.get('data', {})
        if 'child' in entity_data:
            for child_uri in entity_data['child']:
                if child_uri not in seen_uris:
                    unprocessed_count += 1
    
    if unprocessed_count > 0:
        print(f"🔄 Vẫn còn {unprocessed_count} children chưa được xử lý")
        print("💡 Chạy lại script để tiếp tục xử lý dữ liệu")
        return {
            'success': True, 
            'total_entities': len(entities_data), 
            'unprocessed_children': unprocessed_count,
            'message': f'Còn {unprocessed_count} children chưa xử lý. Chạy lại để tiếp tục.'
        }
    
    # Kết hợp tất cả batch files thành file cuối cùng (chỉ khi không còn dữ liệu để xử lý)
    if combine_batches:
        print("\n🔄 Bắt đầu kết hợp các batch files...")
        result = processor.combine_all_batches()
        
        if result and result.get('success'):
            return result
        else:
            print("❌ Lỗi khi kết hợp batch files")
            return None
    else:
        print("⚠️ Chỉ tạo batch files, không kết hợp thành file cuối")
        return {
            'success': True,
            'total_entities': len(entities_data),
            'message': 'Batch files created successfully. Run with combine_batches=True to create final files.'
        }

# Main execution
if __name__ == "__main__":
    # Cấu hình WHO ICD API
    CLIENT_ID = "4876fbe9-043e-417d-bbf6-e1e67ee1d749_1491c0e8-e6fe-4da6-be8c-8635d935a285"
    CLIENT_SECRET = "w6ilxOd6Ik/CXNdIjK0NmsNzc1krj6Ci/606KCWB2eM="
    
    print("🏥 THIẾT LẬP DỮ LIỆU CHẨN ĐOÁN TỪ ICD-11 MMS LINEARIZATION")
    print("=" * 70)
    print("📊 Sử dụng: MMS (Mortality and Morbidity Statistics) Linearization")
    print("🔍 Chỉ lấy dữ liệu quan trọng cho chẩn đoán bệnh")
    print("📦 Dữ liệu sẽ được xử lý theo batch 100 entities")
    print("🔄 Có thể resume nếu bị gián đoạn")
    print("=" * 70)
    
    # Thiết lập RAG system với toàn bộ dữ liệu
    result = setup_icd_rag_system(CLIENT_ID, CLIENT_SECRET, batch_size=100, combine_batches=False)
    
    if result and result.get('success'):
        # Chỉ test tìm kiếm nếu đã combine batches hoặc không còn dữ liệu để xử lý
        if not result.get('unprocessed_children', 0):
            print("\n🧪 Test tìm kiếm RAG:")
            
            # Test search function
            try:
                # Thử import relative trước, fallback sang absolute import
                try:
                    from .medical_rag_utils import search_medical_symptoms_and_diseases
                except ImportError:
                    from medical_rag_utils import search_medical_symptoms_and_diseases
                
                test_queries = [
                    "đau đầu",
                    "sốt cao",
                    "khó thở",
                    "đau bụng",
                    "tim mạch"
                ]
                
                for query in test_queries:
                    print(f"\n🔍 Test query: '{query}'")
                    results = search_medical_symptoms_and_diseases(query, top_k=3)
                    
                    if results:
                        for i, result in enumerate(results, 1):
                            metadata = result['metadata']
                            print(f"  {i}. {metadata.get('entity_name', 'Unknown')}")
                            print(f"     URI: {metadata.get('entity_uri', 'N/A')}")
                            print(f"     Relevance: {result['relevance_score']:.3f}")
                    else:
                        print("  Không tìm thấy kết quả")
                        
            except Exception as e:
                print(f"❌ Lỗi khi test tìm kiếm: {e}")
        else:
            print(f"\n💡 {result.get('message', 'Còn dữ liệu để xử lý')}")
    
    else:
        print("❌ Thiết lập RAG system thất bại")

"""
Sample Medical Data Generator
Tạo dữ liệu y tế mẫu để test hệ thống khi WHO ICD API không khả dụng
"""

import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter


def create_sample_medical_data():
    """Tạo dữ liệu y tế mẫu từ kiến thức y tế cơ bản"""
    
    print("🏥 Tạo Sample Medical Data...")
    
    # Sample medical data với thông tin chi tiết
    medical_data = [
        # Triệu chứng và dấu hiệu lâm sàng
        {
            'entity_name': 'Đau đầu',
            'icd_code': 'R51',
            'category_id': '0M',
            'category_name': 'Triệu chứng, dấu hiệu hoặc các phát hiện lâm sàng',
            'entity_type': 'symptom',
            'source_type': 'icd_category',
            'text': """Đau đầu là triệu chứng phổ biến được đặc trưng bởi cảm giác đau ở vùng đầu hoặc cổ. Định nghĩa: Đau đầu có thể xuất hiện ở nhiều vị trí khác nhau và có nhiều mức độ nghiêm trọng khác nhau. Bao gồm: Đau đầu căng thẳng, đau nửa đầu, đau đầu chùm. Triệu chứng: Đau âm ỉ, đau nhói, đau kèm buồn nôn. Nguyên nhân: Stress, thiếu ngủ, tăng huyết áp, nhiễm trùng."""
        },
        {
            'entity_name': 'Chóng mặt',
            'icd_code': 'R42',
            'category_id': '0M', 
            'category_name': 'Triệu chứng, dấu hiệu hoặc các phát hiện lâm sàng',
            'entity_type': 'symptom',
            'source_type': 'icd_category',
            'text': """Chóng mặt là cảm giác mất thương định hướng không gian hoặc cảm giác như thể môi trường xung quanh đang quay. Định nghĩa: Triệu chứng thường gặp có thể do nhiều nguyên nhân gây ra. Bao gồm: Chóng mặt trung ương, chóng mặt ngoại biên. Triệu chứng: Cảm giác quay, mất thăng bằng, buồn nôn. Nguyên nhân: Viêm tai trong, hạ huyết áp, thiếu máu não."""
        },
        {
            'entity_name': 'Sốt',
            'icd_code': 'R50',
            'category_id': '0M',
            'category_name': 'Triệu chứng, dấu hiệu hoặc các phát hiện lâm sàng', 
            'entity_type': 'symptom',
            'source_type': 'icd_category',
            'text': """Sốt là tình trạng tăng nhiệt độ cơ thể trên mức bình thường (>37.5°C). Định nghĩa: Phản ứng tự nhiên của cơ thể trước nhiễm trùng hoặc viêm. Bao gồm: Sốt nhẹ, sốt cao, sốt siêu cao. Triệu chứng: Ớn lạnh, đổ mồ hôi, mệt mỏi, đau đầu. Nguyên nhân: Nhiễm khuẩn, virus, viêm, ung thư."""
        },
        
        # Bệnh hệ tuần hoàn
        {
            'entity_name': 'Tăng huyết áp nguyên phát',
            'icd_code': 'I10',
            'category_id': '0B',
            'category_name': 'Bệnh hệ tuần hoàn',
            'entity_type': 'disease_condition',
            'source_type': 'who_icd',
            'text': """Tăng huyết áp nguyên phát là tình trạng tăng áp lực máu mạn tính không rõ nguyên nhân. Định nghĩa: Huyết áp tâm thu ≥140 mmHg hoặc huyết áp tâm trương ≥90 mmHg. Bao gồm: Tăng huyết áp độ 1, độ 2, độ 3. Triệu chứng: Đau đầu, chóng mặt, mờ mắt, đau ngực. Nguyên nhân: Di truyền, lối sống, béo phì, stress. Biến chứng: Đột quỵ, nhồi máu cơ tim, suy thận."""
        },
        {
            'entity_name': 'Nhồi máu cơ tim cấp',
            'icd_code': 'I21',
            'category_id': '0B',
            'category_name': 'Bệnh hệ tuần hoàn', 
            'entity_type': 'disease_condition',
            'source_type': 'who_icd',
            'text': """Nhồi máu cơ tim cấp là tình trạng thiếu máu cục bộ dẫn đến hoại tử cơ tim. Định nghĩa: Tắc nghẽn động mạch vành gây thiếu oxy cơ tim. Bao gồm: STEMI, NSTEMI. Triệu chứng: Đau ngực dữ dội, khó thở, buồn nôn, đổ mồ hôi lạnh. Nguyên nhân: Xơ vữa động mạch, cục máu đông. Biến chứng: Suy tim, rối loạn nhịp, tử vong."""
        },
        
        # Bệnh hệ hô hấp
        {
            'entity_name': 'Viêm phổi',
            'icd_code': 'J18',
            'category_id': '0C',
            'category_name': 'Bệnh hệ hô hấp',
            'entity_type': 'disease_condition', 
            'source_type': 'who_icd',
            'text': """Viêm phổi là tình trạng viêm nhiễm của phế nang và mô kẽ phổi. Định nghĩa: Nhiễm trùng cấp tính hoặc mạn tính ảnh hưởng đến phổi. Bao gồm: Viêm phổi vi khuẩn, virus, nấm. Triệu chứng: Ho có đờm, sốt, khó thở, đau ngực. Nguyên nhân: Streptococcus pneumoniae, virus cúm, nấm. Điều trị: Kháng sinh, hỗ trợ hô hấp."""
        },
        {
            'entity_name': 'Hen phế quản',
            'icd_code': 'J45',
            'category_id': '0C',
            'category_name': 'Bệnh hệ hô hấp',
            'entity_type': 'disease_condition',
            'source_type': 'who_icd', 
            'text': """Hen phế quản là bệnh viêm mạn tính đường hô hấp với co thắt phế quản. Định nghĩa: Bệnh mạn tính gây khó thở, thở khò khè. Bao gồm: Hen dị ứng, hen không dị ứng. Triệu chứng: Khó thở, thở khò khè, ho, tức ngực. Nguyên nhân: Dị ứng, nhiễm trùng, stress, ô nhiễm không khí. Điều trị: Thuốc giãn phế quản, corticosteroid."""
        },
        
        # Bệnh tiêu hóa  
        {
            'entity_name': 'Viêm dạ dày cấp',
            'icd_code': 'K29.0',
            'category_id': '0D',
            'category_name': 'Bệnh hệ tiêu hóa',
            'entity_type': 'disease_condition',
            'source_type': 'who_icd',
            'text': """Viêm dạ dày cấp là tình trạng viêm niêm mạc dạ dày xuất hiện đột ngột. Định nghĩa: Phản ứng viêm cấp tính của niêm mạc dạ dày. Bao gồm: Viêm dạ dày do thuốc, do nhiễm khuẩn. Triệu chứng: Đau bụng trên, buồn nôn, nôn, khó tiêu. Nguyên nhân: H.pylori, NSAID, rượu, stress. Điều trị: Thuốc ức chế acid, kháng sinh."""
        },
        
        # Bệnh nội tiết
        {
            'entity_name': 'Đái tháo đường type 2',
            'icd_code': 'E11',
            'category_id': '05',
            'category_name': 'Bệnh nội tiết, dinh dưỡng hoặc chuyển hóa',
            'entity_type': 'disease_condition',
            'source_type': 'who_icd',
            'text': """Đái tháo đường type 2 là rối loạn chuyển hóa glucose do kháng insulin. Định nghĩa: Tăng glucose máu mạn tính do giảm nhạy cảm insulin. Bao gồm: Đái tháo đường có biến chứng, không biến chứng. Triệu chứng: Khát nước nhiều, tiểu nhiều, mệt mỏi, sụt cân. Nguyên nhân: Di truyền, béo phì, ít vận động. Điều trị: Metformin, insulin, thay đổi lối sống."""
        },
        
        # Bệnh thần kinh
        {
            'entity_name': 'Đột quỵ não',
            'icd_code': 'I64',
            'category_id': '08',
            'category_name': 'Bệnh hệ thần kinh', 
            'entity_type': 'disease_condition',
            'source_type': 'who_icd',
            'text': """Đột quỵ não là tình trạng thiếu máu não cục bộ hoặc xuất huyết não. Định nghĩa: Rối loạn tuần hoàn não cấp tính gây tổn thương não bộ. Bao gồm: Đột quỵ thiếu máu, đột quỵ xuất huyết. Triệu chứng: Liệt nửa người, nói khó, rối loạn ý thức. Nguyên nhân: Tăng huyết áp, xơ vữa động mạch, rung nhĩ. Điều trị: Tiêu sợi huyết, phẫu thuật."""
        }
    ]
    
    # Load SentenceTransformer model
    print("🔄 Đang tải SentenceTransformer model...")
    models_to_try = [
        'all-MiniLM-L6-v2',
        'paraphrase-MiniLM-L6-v2',
        'sentence-transformers/all-MiniLM-L6-v2'
    ]
    
    embedder = None
    for model_name in models_to_try:
        try:
            print(f"🔄 Thử model: {model_name}...")
            embedder = SentenceTransformer(model_name)
            print(f"✅ Thành công với model: {model_name}")
            break
        except Exception as e:
            print(f"❌ Lỗi với {model_name}: {e}")
            continue
    
    if embedder is None:
        print("❌ Không thể tải bất kỳ model nào!")
        return False
    
    # Tạo text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", ".", " ", ""]
    )
    
    # Tạo chunks với metadata
    all_chunks = []
    
    for item in medical_data:
        # Split text thành chunks nhỏ hơn
        chunks = text_splitter.split_text(item['text'])
        
        for chunk in chunks:
            if len(chunk.strip()) > 20:  # Chỉ lấy chunks có nội dung đáng kể
                chunk_data = {
                    'text': chunk,
                    'metadata': {
                        'entity_name': item['entity_name'],
                        'icd_code': item['icd_code'],
                        'category_id': item['category_id'],
                        'category_name': item['category_name'], 
                        'entity_type': item['entity_type'],
                        'source_type': item['source_type']
                    }
                }
                all_chunks.append(chunk_data)
    
    print(f"✅ Đã tạo {len(all_chunks)} chunks từ {len(medical_data)} entities y tế")
    
    # Tạo embeddings
    print("🔄 Đang tạo embeddings...")
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    
    # Tạo và lưu FAISS index
    print("🔄 Đang tạo FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Lưu FAISS index
    faiss.write_index(index, "medical_faiss_index.index")
    print("✅ Đã lưu medical_faiss_index.index")
    
    # Chuẩn bị metadata để lưu
    chunks_data = {
        'chunks': all_chunks,
        'texts': texts,
        'metadata': [chunk['metadata'] for chunk in all_chunks],
        'created_at': datetime.now().isoformat(),
        'total_chunks': len(all_chunks),
        'total_categories': len(set(item['category_id'] for item in medical_data)),
        'data_source': 'sample_medical_data',
        'data_type': 'medical_diagnostic',
        'embedding_model': str(embedder).split('(')[0],
        'embedding_dimension': dimension
    }
    
    # Lưu chunks data
    with open("medical_chunks_with_metadata.pkl", "wb") as f:
        pickle.dump(chunks_data, f)
    print("✅ Đã lưu medical_chunks_with_metadata.pkl")
    
    # Thống kê
    print(f"\n📊 THỐNG KÊ SAMPLE MEDICAL DATA:")
    print(f"   - Tổng số entities: {len(medical_data)}")
    print(f"   - Tổng số chunks: {len(all_chunks)}")
    print(f"   - Kích thước embedding: {dimension}")
    print(f"   - Số danh mục y tế: {chunks_data['total_categories']}")
    
    # Test search
    print(f"\n🧪 TEST TÌM KIẾM:")
    test_queries = ["đau đầu", "cao huyết áp", "viêm phổi"]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        query_embedding = embedder.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_embedding, 3)
        
        for i, idx in enumerate(indices[0]):
            chunk = all_chunks[idx]
            print(f"   {i+1}. {chunk['metadata']['entity_name']} (ICD: {chunk['metadata']['icd_code']})")
            print(f"      Distance: {distances[0][i]:.3f}")
    
    print(f"\n🎉 Sample Medical Data đã được tạo thành công!")
    print(f"📁 Files đã tạo:")
    print(f"   - medical_faiss_index.index")
    print(f"   - medical_chunks_with_metadata.pkl")
    
    return True


if __name__ == "__main__":
    success = create_sample_medical_data()
    if success:
        print("\n✅ Hoàn tất! Bây giờ bạn có thể test Enhanced Medical RAG System.")
        print("🚀 Chạy: python app.py để khởi động server")
    else:
        print("\n❌ Tạo sample data thất bại!")

from openai import OpenAI

# Khởi tạo ứng dụng
APP_CONTEXT = {}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def init_app_context(app):
    print("--- KHỞI TẠO HỆ THỐNG Y TẾ ---")
    print("✅ Medical chatbot initialized successfully.")
    print("📋 Medical RAG system ready to process health queries.")
    print("🩺 All medical functions are loaded from medical_rag_utils.py")
    
    # Medical data sẽ được load bởi medical_rag_utils.py khi cần thiết
    # Không cần load trước vào app context
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
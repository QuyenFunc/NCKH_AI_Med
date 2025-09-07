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
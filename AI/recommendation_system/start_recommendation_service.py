#!/usr/bin/env python3
"""
Startup script for Health Content Recommendation System
"""

import os
import sys
import time
import signal
import threading
from api_server import start_server, stop_server

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal. Stopping recommendation service...")
    stop_server()
    sys.exit(0)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🏥 Health Content Recommendation System")
    print("=" * 60)
    print()
    print("🚀 Starting services...")
    print("   📊 OpenRouter AI Analysis")
    print("   🔄 Background Job Processor") 
    print("   🎯 Content Matching Engine")
    print("   🌐 API Server (Port 5002)")
    print()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Check if OpenRouter API key is set
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("⚠️  Warning: OPENROUTER_API_KEY not set. Using default key.")
        else:
            print("✅ OpenRouter API key configured")
        
        print()
        print("🎯 System Ready!")
        print("   API Endpoints:")
        print("   - POST /recommendations/analyze-profile")
        print("   - GET  /recommendations/user/<user_id>")
        print("   - GET  /recommendations/trending")
        print("   - POST /recommendations/track-click")
        print("   - GET  /health")
        print()
        print("📡 Server starting on http://0.0.0.0:5002")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        # Start the server (this blocks)
        start_server()
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script để fix lỗi download SentenceTransformer model
Thử các cách khác nhau để download model embedding
"""

import os
import sys
from sentence_transformers import SentenceTransformer

def test_model_download():
    """Test download các embedding models khác nhau"""
    
    models_to_try = [
        'all-MiniLM-L6-v2',
        'paraphrase-MiniLM-L6-v2', 
        'all-mpnet-base-v2',
        'sentence-transformers/all-MiniLM-L6-v2',
        'sentence-transformers/paraphrase-MiniLM-L6-v2',
        'sentence-transformers/all-mpnet-base-v2'
    ]
    
    print("🔄 Testing SentenceTransformer model downloads...")
    print("=" * 60)
    
    successful_models = []
    
    for model_name in models_to_try:
        print(f"\n📥 Trying to download: {model_name}")
        try:
            embedder = SentenceTransformer(model_name)
            
            # Test encoding
            test_text = "This is a test sentence"
            embedding = embedder.encode([test_text])
            
            print(f"✅ SUCCESS: {model_name}")
            print(f"   - Embedding dimension: {embedding.shape[1]}")
            print(f"   - Model loaded successfully")
            
            successful_models.append({
                'name': model_name,
                'dimension': embedding.shape[1],
                'model': embedder
            })
            
            break  # Dừng khi tìm được model hoạt động
            
        except OSError as e:
            if "from_tf=True" in str(e):
                print(f"⚠️  TENSORFLOW WEIGHTS: {model_name}")
                print("   - Trying to install TensorFlow...")
                try:
                    import tensorflow as tf
                    print("   - TensorFlow already installed")
                    # Try loading with TF
                    try:
                        embedder = SentenceTransformer(model_name)
                        print(f"✅ SUCCESS with TF: {model_name}")
                        successful_models.append({
                            'name': model_name,
                            'dimension': 384,  # default for MiniLM
                            'model': embedder,
                            'method': 'tensorflow'
                        })
                        break
                    except Exception as tf_error:
                        print(f"   - TF loading failed: {tf_error}")
                except ImportError:
                    print("   - TensorFlow not installed")
                    print("   - Run: pip install tensorflow")
            else:
                print(f"❌ FAILED: {model_name}")
                print(f"   - Error: {e}")
                
        except Exception as e:
            print(f"❌ FAILED: {model_name}")
            print(f"   - Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    
    if successful_models:
        print(f"✅ Found {len(successful_models)} working model(s):")
        for model in successful_models:
            method = model.get('method', 'pytorch')
            print(f"   - {model['name']} (dim: {model['dimension']}, method: {method})")
        
        # Save the best model info
        best_model = successful_models[0]
        print(f"\n🎉 RECOMMENDED MODEL: {best_model['name']}")
        
        return best_model['name']
    else:
        print("❌ No models worked! Please check:")
        print("   1. Internet connection")
        print("   2. Install TensorFlow: pip install tensorflow")
        print("   3. Update sentence-transformers: pip install -U sentence-transformers")
        
        return None

def install_tensorflow():
    """Cài đặt TensorFlow nếu chưa có"""
    print("🔄 Installing TensorFlow...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
        print("✅ TensorFlow installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install TensorFlow: {e}")
        return False

def fix_model_compatibility():
    """Fix model compatibility issues"""
    print("🔧 Fixing SentenceTransformer model compatibility...")
    
    # Try to install TensorFlow first
    try:
        import tensorflow as tf
        print("✅ TensorFlow already available")
    except ImportError:
        print("📥 Installing TensorFlow...")
        if not install_tensorflow():
            print("⚠️ Continuing without TensorFlow...")
    
    # Test model downloads
    working_model = test_model_download()
    
    if working_model:
        print(f"\n🎯 SOLUTION FOUND!")
        print(f"Update your code to use: '{working_model}'")
        
        # Create a config file with the working model
        config = {
            'embedding_model': working_model,
            'embedding_dimension': 384,
            'status': 'working'
        }
        
        import json
        with open('model_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Model config saved to: model_config.json")
        
        return True
    else:
        print("\n❌ NO SOLUTION FOUND")
        print("Please try:")
        print("1. pip install tensorflow")
        print("2. pip install -U sentence-transformers")
        print("3. Check internet connection")
        print("4. Try different model names")
        
        return False

if __name__ == "__main__":
    print("🚀 SentenceTransformer Model Fix Tool")
    print("=" * 60)
    
    success = fix_model_compatibility()
    
    if success:
        print("\n✅ Fix completed! You can now run setup_icd_faiss.py")
    else:
        print("\n❌ Fix failed. Please check the recommendations above.")

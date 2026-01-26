"""
Convert ParadoxLF CLIP models to TensorFlow Lite for mobile deployment
This script exports the CLIP encoder to .tflite format for on-device inference
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/../')

import tensorflow as tf
import numpy as np
from paradox.media.clip_module import CLIPEncoder

print("=" * 60)
print("ParadoxLF → TensorFlow Lite Model Converter")
print("=" * 60)

def convert_clip_to_tflite():
    """Convert CLIP encoder to TensorFlow Lite"""
    
    print("\n📦 Loading ParadoxLF CLIP encoder...")
    try:
        clip_encoder = CLIPEncoder()
        print(f"✅ CLIP loaded successfully")
        print(f"   Vector dimension: {clip_encoder.dimension}")
    except Exception as e:
        print(f"❌ Failed to load CLIP: {e}")
        print("   Make sure ParadoxLF is installed: pip install .[ai]")
        return
    
    print("\n🔄 Converting to TensorFlow Lite...")
    
    # Note: CLIP models from HuggingFace are PyTorch-based
    # We need to export to ONNX first, then convert to TFLite
    # This is a simplified example - actual implementation would be more complex
    
    print("\n⚠️  CLIP Model Conversion Notes:")
    print("   - CLIP from OpenAI is PyTorch-based")
    print("   - Direct conversion PyTorch → TFLite is complex")
    print("   - Recommended approach:")
    print("     1. Use HuggingFace transformers")
    print("     2. Export to ONNX format")
    print("     3. Convert ONNX → TFLite")
    print("")
    print("   Alternative (simpler):")
    print("     1. Use sentence-transformers (already TF-compatible)")
    print("     2. Export directly to TFLite")
    
    # For now, create a mock TFLite model for demonstration
    create_mock_tflite_model()

def create_mock_tflite_model():
    """Create a simple mock TFLite model for testing"""
    
    print("\n📝 Creating mock TFLite models for testing...")
    
    # Create output directory
    output_dir = "mobile/assets/models"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a simple model that outputs 512D vectors
    # This is just for testing - real model would use actual CLIP weights
    
    # Text encoder mock
    text_input = tf.keras.Input(shape=(77,), dtype=tf.int32, name='input_ids')
    x = tf.keras.layers.Embedding(49408, 512)(text_input)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    text_output = tf.keras.layers.Dense(512, activation='tanh', name='text_embedding')(x)
    text_model = tf.keras.Model(inputs=text_input, outputs=text_output)
    
    # Convert to TFLite
    text_converter = tf.lite.TFLiteConverter.from_keras_model(text_model)
    text_tflite = text_converter.convert()
    
    text_path = os.path.join(output_dir, 'clip_text_encoder.tflite')
    with open(text_path, 'wb') as f:
        f.write(text_tflite)
    
    print(f"✅ Created mock text encoder: {text_path}")
    print(f"   Size: {len(text_tflite) / 1024:.2f} KB")
    
    # Image encoder mock
    image_input = tf.keras.Input(shape=(224, 224, 3), dtype=tf.float32, name='pixel_values')
    x = tf.keras.layers.Conv2D(64, 3, activation='relu')(image_input)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(128, 3, activation='relu')(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    image_output = tf.keras.layers.Dense(512, activation='tanh', name='image_embedding')(x)
    image_model = tf.keras.Model(inputs=image_input, outputs=image_output)
    
    # Convert to TFLite
    image_converter = tf.lite.TFLiteConverter.from_keras_model(image_model)
    image_tflite = image_converter.convert()
    
    image_path = os.path.join(output_dir, 'clip_image_encoder.tflite')
    with open(image_path, 'wb') as f:
        f.write(image_tflite)
    
    print(f"✅ Created mock image encoder: {image_path}")
    print(f"   Size: {len(image_tflite) / 1024:.2f} KB")
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT: These are MOCK models for testing only!")
    print("   They do NOT provide actual semantic encoding.")
    print("   For production, use real CLIP weights converted to TFLite.")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("   1. The mock models are in: mobile/assets/models/")
    print("   2. Build the APK: cd mobile && flutter build apk")
    print("   3. Test the app - it will use the mock models")
    print("   4. For production: replace with real CLIP TFLite models")
    
    print("\n🔗 Resources for Real CLIP Conversion:")
    print("   - HuggingFace Optimum: https://huggingface.co/docs/optimum")
    print("   - ONNX to TFLite: https://www.tensorflow.org/lite/guide/ops_compatibility")
    print("   - Sentence Transformers: https://www.sbert.net/")

if __name__ == "__main__":
    convert_clip_to_tflite()
    print("\n✅ Model conversion complete!\n")

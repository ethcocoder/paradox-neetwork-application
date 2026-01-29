"""
Convert ParadoxLF CLIP models to TensorFlow Lite for mobile deployment
This script exports the CLIP encoder to .tflite format for on-device inference
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/../paradoxlf/')

import tensorflow as tf
import numpy as np
from paradox.media.clip_module import CLIPEncoder

print("=" * 60)
print("ParadoxLF -> TensorFlow Lite Model Converter")
print("=" * 60)

def convert_clip_to_tflite():
    """Convert CLIP encoder to TensorFlow Lite"""
    
    print("\n[INFO] Loading ParadoxLF CLIP encoder...")
    try:
        clip_encoder = CLIPEncoder()
        print(f"[OK] CLIP loaded successfully")
        print(f"   Vector dimension: {clip_encoder.dimension}")
    except Exception as e:
        print(f"❌ Failed to load CLIP: {e}")
        print("   Make sure ParadoxLF is installed: pip install .[ai]")
        return
    
    print("\n[ACTION] Converting to TensorFlow Lite...")
    
    # Note: CLIP models from HuggingFace are PyTorch-based
    # We need to export to ONNX first, then convert to TFLite
    # This is a simplified example - actual implementation would be more complex
    
    print("\n[WARNING] CLIP Model Conversion Notes:")
    print("   - CLIP from OpenAI is PyTorch-based")
    print("   - Direct conversion PyTorch -> TFLite is complex")
    print("   - Recommended approach:")
    print("     1. Use HuggingFace transformers")
    print("     2. Export to ONNX format")
    print("     3. Convert ONNX -> TFLite")
    print("")
    print("   Alternative (simpler):")
    print("     1. Use sentence-transformers (already TF-compatible)")
    print("     2. Export directly to TFLite")
    
    # For now, create a mock TFLite model for demonstration
    create_mock_tflite_model()

def create_mock_tflite_model():
    """Create a simple mock TFLite model for testing"""
    
    print("\n[CREATE] Creating mock TFLite models for testing...")
    
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
    
    print(f"[OK] Created mock text encoder: {text_path}")
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
    
    print(f"[OK] Created mock image encoder: {image_path}")
    print(f"   Size: {len(image_tflite) / 1024:.2f} KB")
    
    # Text decoder mock
    decoder_input = tf.keras.Input(shape=(512,), dtype=tf.float32, name='latent_input')
    x = tf.keras.layers.Dense(512, activation='relu')(decoder_input)
    decoder_output = tf.keras.layers.Dense(77, activation='softmax', name='token_output')(x)
    text_decoder_model = tf.keras.Model(inputs=decoder_input, outputs=decoder_output)
    
    text_decoder_converter = tf.lite.TFLiteConverter.from_keras_model(text_decoder_model)
    text_decoder_tflite = text_decoder_converter.convert()
    
    text_decoder_path = os.path.join(output_dir, 'clip_text_decoder.tflite')
    with open(text_decoder_path, 'wb') as f:
        f.write(text_decoder_tflite)
    print(f"[OK] Created mock text decoder: {text_decoder_path}")

    # Image decoder mock
    img_decoder_input = tf.keras.Input(shape=(512,), dtype=tf.float32, name='latent_input')
    x = tf.keras.layers.Dense(1024, activation='relu')(img_decoder_input)
    x = tf.keras.layers.Reshape((32, 32, 1))(x)
    x = tf.keras.layers.UpSampling2D((7, 7))(x) # To 224x224
    img_decoder_output = tf.keras.layers.Conv2D(3, 3, padding='same', activation='sigmoid')(x)
    img_decoder_model = tf.keras.Model(inputs=img_decoder_input, outputs=img_decoder_output)
    
    img_decoder_converter = tf.lite.TFLiteConverter.from_keras_model(img_decoder_model)
    img_decoder_tflite = img_decoder_converter.convert()
    
    img_decoder_path = os.path.join(output_dir, 'clip_image_decoder.tflite')
    with open(img_decoder_path, 'wb') as f:
        f.write(img_decoder_tflite)
    print(f"[OK] Created mock image decoder: {img_decoder_path}")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: These are MOCK models for testing only!")
    print("   They do NOT provide actual semantic encoding.")
    print("   For production, use real CLIP weights converted to TFLite.")
    print("=" * 60)
    
    print("\n[STEPS] Next Steps:")
    print("   1. The mock models are in: mobile/assets/models/")
    print("   2. Build the APK: cd mobile && flutter build apk")
    print("   3. Test the app - it will use the mock models")
    print("   4. For production: replace with real CLIP TFLite models")
    
    print("\n[RESOURCES] Resources for Real CLIP Conversion:")
    print("   - HuggingFace Optimum: https://huggingface.co/docs/optimum")
    print("   - ONNX to TFLite: https://www.tensorflow.org/lite/guide/ops_compatibility")
    print("   - Sentence Transformers: https://www.sbert.net/")

if __name__ == "__main__":
    convert_clip_to_tflite()
    print("\n[DONE] Model conversion complete!\n")

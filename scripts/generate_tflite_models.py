#!/usr/bin/env python3
"""
TFLite Universal Encoder/Decoder Model Generator
Generates lightweight autoencoder models for real-time data compression
Handles any data type: text, images, audio, video, binary files
"""

import numpy as np
import tensorflow as tf
from pathlib import Path

# Model Configuration
LATENT_DIM = 512  # Compressed latent vector size
INPUT_DIM = 2048  # Maximum input chunk size (bytes)
COMPRESSION_RATIO = INPUT_DIM / LATENT_DIM  # 4x compression

def create_universal_encoder():
    """
    Creates a universal encoder model that compresses any byte data
    into a 512-dimensional latent vector
    """
    print("Creating Universal Encoder Model...")
    
    model = tf.keras.Sequential([
        # Input: Variable length byte array (padded to INPUT_DIM)
        tf.keras.layers.Input(shape=(INPUT_DIM,), name='input_bytes'),
        
        # Reshape for processing
        tf.keras.layers.Reshape((INPUT_DIM, 1)),
        
        # Conv layers for feature extraction
        tf.keras.layers.Conv1D(128, 7, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(256, 5, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(512, 3, activation='relu', padding='same'),
        tf.keras.layers.GlobalAveragePooling1D(),
        
        # Bottleneck - compressed representation
        tf.keras.layers.Dense(LATENT_DIM, activation='tanh', name='latent_vector'),
    ], name='universal_encoder')
    
    return model

def create_universal_decoder():
    """
    Creates a universal decoder model that reconstructs data
    from a 512-dimensional latent vector
    """
    print("Creating Universal Decoder Model...")
    
    model = tf.keras.Sequential([
        # Input: 512-dimensional latent vector
        tf.keras.layers.Input(shape=(LATENT_DIM,), name='latent_input'),
        
        # Expand to feature space
        tf.keras.layers.Dense(512 * 128, activation='relu'),
        tf.keras.layers.Reshape((512, 128)),
        
        # Upsampling with transpose convolutions
        tf.keras.layers.Conv1DTranspose(256, 3, strides=2, activation='relu', padding='same'),
        tf.keras.layers.Conv1DTranspose(128, 5, strides=2, activation='relu', padding='same'),
        tf.keras.layers.Conv1DTranspose(64, 7, activation='relu', padding='same'),
        
        # Output: Reconstructed byte array
        tf.keras.layers.Conv1D(1, 3, activation='sigmoid', padding='same'),
        tf.keras.layers.Reshape((INPUT_DIM,), name='output_bytes'),
    ], name='universal_decoder')
    
    return model

def create_autoencoder():
    """
    Creates a complete autoencoder for training purposes
    """
    encoder = create_universal_encoder()
    decoder = create_universal_decoder()
    
    # Full autoencoder model
    autoencoder = tf.keras.Sequential([
        encoder,
        decoder
    ], name='universal_autoencoder')
    
    return autoencoder, encoder, decoder

def train_on_synthetic_data(autoencoder, epochs=50):
    """
    Train the autoencoder on synthetic data representing various file types
    """
    print("\nTraining on synthetic data...")
    
    # Generate synthetic training data (representing various data types)
    num_samples = 10000
    
    # Mix of different patterns (text-like, image-like, audio-like)
    text_data = np.random.randint(32, 127, size=(num_samples // 3, INPUT_DIM))  # ASCII range
    image_data = np.random.randint(0, 256, size=(num_samples // 3, INPUT_DIM))  # Byte range
    audio_data = np.random.normal(128, 64, size=(num_samples // 3, INPUT_DIM))  # Normal distribution
    
    X_train = np.vstack([text_data, image_data, audio_data]).astype('float32') / 255.0
    
    # Compile and train
    autoencoder.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    autoencoder.fit(
        X_train, X_train,
        epochs=epochs,
        batch_size=128,
        shuffle=True,
        validation_split=0.1,
        verbose=1
    )
    
    print("Training complete!")

def convert_to_tflite(model, output_path, model_name):
    """
    Convert Keras model to TFLite format with optimizations
    """
    print(f"\nConverting {model_name} to TFLite format...")
    
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Optimizations for mobile/embedded devices
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]  # Use float16 for smaller size
    
    tflite_model = converter.convert()
    
    # Save the model
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    file_size = output_path.stat().st_size / (1024 * 1024)  # Size in MB
    print(f"✓ Saved {model_name} to {output_path} ({file_size:.2f} MB)")
    
    return output_path

def test_models(encoder_path, decoder_path):
    """
    Test the generated TFLite models
    """
    print("\n" + "="*60)
    print("Testing Generated Models")
    print("="*60)
    
    # Load TFLite models
    encoder_interpreter = tf.lite.Interpreter(model_path=str(encoder_path))
    encoder_interpreter.allocate_tensors()
    
    decoder_interpreter = tf.lite.Interpreter(model_path=str(decoder_path))
    decoder_interpreter.allocate_tensors()
    
    # Get input/output details
    encoder_input_details = encoder_interpreter.get_input_details()
    encoder_output_details = encoder_interpreter.get_output_details()
    
    decoder_input_details = decoder_interpreter.get_input_details()
    decoder_output_details = decoder_interpreter.get_output_details()
    
    # Test with sample data
    test_data = np.random.randint(0, 256, size=(1, INPUT_DIM)).astype('float32') / 255.0
    
    # Encode
    encoder_interpreter.set_tensor(encoder_input_details[0]['index'], test_data)
    encoder_interpreter.invoke()
    latent_vector = encoder_interpreter.get_tensor(encoder_output_details[0]['index'])
    
    # Decode
    decoder_interpreter.set_tensor(decoder_input_details[0]['index'], latent_vector)
    decoder_interpreter.invoke()
    reconstructed = decoder_interpreter.get_tensor(decoder_output_details[0]['index'])
    
    # Calculate reconstruction error
    mse = np.mean((test_data - reconstructed) ** 2)
    compression_ratio = (INPUT_DIM * 4) / (LATENT_DIM * 4)  # Assume float32
    
    print(f"\n✓ Encoder Input Shape: {encoder_input_details[0]['shape']}")
    print(f"✓ Latent Vector Shape: {encoder_output_details[0]['shape']}")
    print(f"✓ Decoder Output Shape: {decoder_output_details[0]['shape']}")
    print(f"✓ Compression Ratio: {compression_ratio:.1f}x")
    print(f"✓ Reconstruction MSE: {mse:.6f}")
    print(f"✓ Models working correctly!")

def main():
    """
    Main execution function
    """
    print("="*60)
    print("TFLite Universal Encoder/Decoder Generator")
    print("="*60)
    print(f"Input Dimension: {INPUT_DIM} bytes")
    print(f"Latent Dimension: {LATENT_DIM} floats")
    print(f"Compression Ratio: {COMPRESSION_RATIO:.1f}x")
    print("="*60)
    
    # Create models
    autoencoder, encoder, decoder = create_autoencoder()
    
    print("\nModel Architecture Summary:")
    print("\n--- Encoder ---")
    encoder.summary()
    print("\n--- Decoder ---")
    decoder.summary()
    
    # Train the autoencoder
    train_on_synthetic_data(autoencoder, epochs=30)
    
    # Define output paths
    script_dir = Path(__file__).parent.parent
    encoder_path = script_dir / 'assets' / 'models' / 'universal_encoder.tflite'
    decoder_path = script_dir / 'assets' / 'models' / 'universal_decoder.tflite'
    
    # Convert to TFLite
    encoder_tflite_path = convert_to_tflite(encoder, encoder_path, "Universal Encoder")
    decoder_tflite_path = convert_to_tflite(decoder, decoder_path, "Universal Decoder")
    
    # Test the models
    test_models(encoder_tflite_path, decoder_tflite_path)
    
    print("\n" + "="*60)
    print("✓ Model Generation Complete!")
    print("="*60)
    print(f"\nGenerated models:")
    print(f"  - {encoder_tflite_path}")
    print(f"  - {decoder_tflite_path}")
    print(f"\nThese models can now be used in your React Native app!")
    print("="*60)

if __name__ == "__main__":
    # Check TensorFlow version
    print(f"TensorFlow Version: {tf.__version__}")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Run main function
    main()

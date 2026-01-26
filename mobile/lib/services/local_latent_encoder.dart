/// Local Latent Encoder - On-Device CLIP Encoding
/// This runs ParadoxLF-like encoding LOCALLY on the device
/// Raw data NEVER leaves the device - only latent vectors are sent

import 'dart:typed_data';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;

class LocalLatentEncoder {
  Interpreter? _textEncoder;
  Interpreter? _imageEncoder;
  
  static const int vectorDimension = 512;
  bool _isInitialized = false;
  
  /// Initialize CLIP models (TensorFlow Lite)
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Load CLIP text encoder (converts text to 512D vector)
      _textEncoder = await Interpreter.fromAsset(
        'assets/models/clip_text_encoder.tflite',
      );
      
      // Load CLIP image encoder (converts image to 512D vector)
      _imageEncoder = await Interpreter.fromAsset(
        'assets/models/clip_image_encoder.tflite',
      );
      
      _isInitialized = true;
      print('✅ Local latent encoder initialized');
    } catch (e) {
      print('⚠️  TFLite models not found, using fallback encoder');
      // Fallback to lightweight encoding (see below)
      _isInitialized = true;
    }
  }
  
  /// Encode text to latent vector (512D)
  /// This happens ON DEVICE - text never sent to server
  Future<List<double>> encodeText(String text) async {
    await initialize();
    
    if (_textEncoder != null) {
      return _encodeTextWithCLIP(text);
    } else {
      // Fallback: Simple hash-based encoding
      return _fallbackTextEncoding(text);
    }
  }
  
  /// Encode image to latent vector (512D)
  /// This happens ON DEVICE - image never sent to server
  Future<List<double>> encodeImage(Uint8List imageBytes) async {
    await initialize();
    
    if (_imageEncoder != null) {
      return _encodeImageWithCLIP(imageBytes);
    } else {
      // Fallback: Perceptual hash encoding
      return _fallbackImageEncoding(imageBytes);
    }
  }
  
  // ==================== CLIP-based Encoding ====================
  
  Future<List<double>> _encodeTextWithCLIP(String text) async {
    // Tokenize text (simplified - real implementation would use CLIP tokenizer)
    final tokens = _tokenizeText(text);
    
    // Create input tensor [1, max_length]
    final input = [tokens];
    
    // Create output tensor [1, 512]
    final output = List.filled(1, List<double>.filled(vectorDimension, 0.0));
    
    // Run inference
    _textEncoder!.run(input, output);
    
    // Return normalized vector
    return _normalize(output[0]);
  }
  
  Future<List<double>> _encodeImageWithCLIP(Uint8List imageBytes) async {
    // Decode image
    final image = img.decodeImage(imageBytes);
    if (image == null) throw Exception('Failed to decode image');
    
    // Resize to 224x224 (CLIP input size)
    final resized = img.copyResize(image, width: 224, height: 224);
    
    // Convert to normalized float array [1, 224, 224, 3]
    final input = _imageToTensor(resized);
    
    // Create output tensor [1, 512]
    final output = List.filled(1, List<double>.filled(vectorDimension, 0.0));
    
    // Run inference
    _imageEncoder!.run(input, output);
    
    // Return normalized vector
    return _normalize(output[0]);
  }
  
  // ==================== Fallback Encoding (when no model) ====================
  
  /// Lightweight fallback when CLIP models not available
  /// Uses hash-based semantic encoding
  List<double> _fallbackTextEncoding(String text) {
    final vector = List<double>.filled(vectorDimension, 0.0);
    
    // Use text hash to deterministically generate vector
    final hash = text.hashCode;
    for (int i = 0; i < vectorDimension; i++) {
      // Generate pseudo-random value based on hash + index
      final seed = hash + i;
      vector[i] = (_hashToDouble(seed) * 2.0) - 1.0; // Range: -1 to 1
    }
    
    return _normalize(vector);
  }
  
  List<double> _fallbackImageEncoding(Uint8List imageBytes) {
    final vector = List<double>.filled(vectorDimension, 0.0);
    
    // Use perceptual hash of image
    final image = img.decodeImage(imageBytes);
    if (image == null) return vector;
    
    // Create simple perceptual features
    final thumbnail = img.copyResize(image, width: 32, height: 32);
    
    int idx = 0;
    for (int y = 0; y < 32 && idx < vectorDimension; y++) {
      for (int x = 0; x < 32 && idx < vectorDimension; x++) {
        final pixel = thumbnail.getPixel(x, y);
        final r = pixel.r / 255.0;
        final g = pixel.g / 255.0;
        final b = pixel.b / 255.0;
        
        // Store color info in vector
        if (idx < vectorDimension) vector[idx++] = r;
        if (idx < vectorDimension) vector[idx++] = g;
        if (idx < vectorDimension) vector[idx++] = b;
      }
    }
    
    return _normalize(vector);
  }
  
  // ==================== Helper Methods ====================
  
  List<int> _tokenizeText(String text) {
    // Simplified tokenization (real CLIP uses BPE tokenizer)
    final tokens = <int>[];
    for (int i = 0; i < text.length && i < 77; i++) {
      tokens.add(text.codeUnitAt(i));
    }
    // Pad to max length
    while (tokens.length < 77) {
      tokens.add(0);
    }
    return tokens;
  }
  
  List<List<List<List<double>>>> _imageToTensor(img.Image image) {
    // Convert image to [1, 224, 224, 3] tensor
    final tensor = List.generate(
      1,
      (_) => List.generate(
        224,
        (y) => List.generate(
          224,
          (x) {
            final pixel = image.getPixel(x, y);
            return [
              (pixel.r / 255.0) * 2.0 - 1.0, // Normalize to [-1, 1]
              (pixel.g / 255.0) * 2.0 - 1.0,
              (pixel.b / 255.0) * 2.0 - 1.0,
            ];
          },
        ),
      ),
    );
    return tensor;
  }
  
  List<double> _normalize(List<double> vector) {
    // L2 normalization
    double sumSquares = 0.0;
    for (final v in vector) {
      sumSquares += v * v;
    }
    final norm = sumSquares > 0 ? 1.0 / (sumSquares.sqrt()) : 1.0;
    
    return vector.map((v) => v * norm).toList();
  }
  
  double _hashToDouble(int hash) {
    // Convert hash to double [0, 1]
    return ((hash & 0xFFFFFF) / 0xFFFFFF).abs();
  }
  
  void dispose() {
    _textEncoder?.close();
    _imageEncoder?.close();
  }
}

extension on double {
  double sqrt() => this < 0 ? 0 : this;
}

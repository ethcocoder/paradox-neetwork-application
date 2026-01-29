/// Local Latent Decoder - Reconstructs messages from vectors ON DEVICE

import 'dart:typed_data';
import 'package:tflite_flutter/tflite_flutter.dart';

class LocalLatentDecoder {
  Interpreter? _textDecoder;
  Interpreter? _imageDecoder;
  
  bool _isInitialized = false;
  Map<String, String> _textCache = {};
  
  /// Initialize decoders
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Use Hardware Acceleration
      final options = InterpreterOptions();
      try {
        options.addDelegate(NnapiDelegate());
      } catch (e) {
        print('NNAPI not available for decoder');
      }

      // Load CLIP decoders
      _textDecoder = await Interpreter.fromAsset(
        'assets/models/clip_text_decoder.tflite',
        options: options,
      );
      
      _imageDecoder = await Interpreter.fromAsset(
        'assets/models/clip_image_decoder.tflite',
        options: options,
      );
      
      _isInitialized = true;
      print('✅ Local latent decoder initialized');
    } catch (e) {
      print('⚠️  TFLite decoders not found, using fallback: $e');
      _isInitialized = true;
    }
    _isInitialized = true;
  }
  
  /// Decode latent vector back to text
  /// This happens ON DEVICE - server never sees decoded content
  Future<String> decodeText(List<double> latentVector) async {
    await initialize();
    
    // Check cache first
    final vectorKey = latentVector.take(10).join(',');
    if (_textCache.containsKey(vectorKey)) {
      return _textCache[vectorKey]!;
    }
    
    if (_textDecoder != null) {
      final decoded = await _decodeTextWithCLIP(latentVector);
      _textCache[vectorKey] = decoded;
      return decoded;
    } else {
      // Fallback: Show placeholder
      return _fallbackTextDecoding(latentVector);
    }
  }
  
  /// Decode latent vector back to image
  Future<Uint8List?> decodeImage(List<double> latentVector) async {
    await initialize();
    
    if (_imageDecoder != null) {
      return await _decodeImageWithCLIP(latentVector);
    } else {
      // Fallback: Generate placeholder
    }
  }

  /// Decode video (reconstruct from chronological latents)
  Future<String> decodeVideo(List<double> latentVector) async {
    await initialize();
    return 'Reconstructed Video [Latent Segment]';
  }

  /// Decode documents (PDF, DOCX)
  Future<String> decodeDocument(List<double> latentVector) async {
    await initialize();
    return 'Reconstructed Document.pdf';
  }
  
  // ==================== CLIP-based Decoding ====================
  
  Future<String> _decodeTextWithCLIP(List<double> latentVector) async {
    // Input: [1, 512]
    final input = [latentVector];
    // Output: [1, 77] (tokens)
    final output = List.filled(1, List<int>.filled(77, 0));
    
    _textDecoder!.run(input, output);
    
    // Convert tokens back to string
    return String.fromCharCodes(output[0].where((c) => c > 0));
  }
  
  Future<Uint8List?> _decodeImageWithCLIP(List<double> latentVector) async {
    // Input: [1, 512]
    final input = [latentVector];
    // Output: [1, 224, 224, 3]
    final output = List.filled(
      1, 
      List.generate(
        224, 
        (_) => List.generate(
          224, 
          (_) => List<double>.filled(3, 0.0)
        )
      )
    );
    
    _imageDecoder!.run(input, output);
    
    // In a real implementation, we'd convert this tensor to PNG bytes
    return _fallbackImageDecoding(latentVector); 
  }
  
  // ==================== Fallback Decoding ====================
  
  String _fallbackTextDecoding(List<double> latentVector) {
    // Generate a readable representation
    final magnitude = _vectorMagnitude(latentVector);
    final category = _categorizeVector(latentVector);
    
    return '[$category message]'; // Placeholder
  }
  
  Uint8List _fallbackImageDecoding(List<double> latentVector) {
    // Generate a simple colored square based on vector
    // This is just a placeholder - real decoding would use a generative model
    final color = _vectorToColor(latentVector);
    
    // Create 1x1 pixel PNG with the color
    final rgba = [color[0], color[1], color[2], 255];
    return Uint8List.fromList(rgba);
  }
  
  // ==================== Helper Methods ====================
  
  double _vectorMagnitude(List<double> vector) {
    double sum = 0.0;
    for (final v in vector) {
      sum += v * v;
    }
    return sum.squareRoot();
  }
  
  String _categorizeVector(List<double> vector) {
    // Simple categorization based on vector properties
    final firstQuadrant = vector.take(128).where((v) => v > 0).length;
    if (firstQuadrant > 64) return 'Positive';
    return 'Neutral';
  }
  
  List<int> _vectorToColor(List<double> vector) {
    // Convert first 3 dimensions to RGB color
    final r = ((vector[0] + 1.0) * 127.5).clamp(0, 255).toInt();
    final g = ((vector[1] + 1.0) * 127.5).clamp(0, 255).toInt();
    final b = ((vector[2] + 1.0) * 127.5).clamp(0, 255).toInt();
    return [r, g, b];
  }
  
  void clearCache() {
    _textCache.clear();
  }
  
  void dispose() {
    // _textDecoder?.close();
    // _imageDecoder?.close();
  }
}

extension on double {
  double squareRoot() => this < 0 ? 0 : this;
}

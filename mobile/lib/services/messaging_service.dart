/// Updated Messaging Service - Uses LOCAL encoding

import '../core/network/traffic_manager.dart';
import '../models/message_model.dart';
import '../services/local_latent_encoder.dart';
import 'dart:typed_data';
import 'dart:convert';

class MessagingService {
  final TrafficManager _trafficManager;
  final LocalLatentEncoder _localEncoder;
  
  MessagingService(this._trafficManager, this._localEncoder);
  
  /// Send text message - ENCODES LOCALLY FIRST
  Future<String> sendTextMessage({
    required String receiverId,
    required String text,
    int priority = 0,
  }) async {
    print('📝 Encoding text locally...');
    
    // STEP 1: Encode text to latent vector ON DEVICE
    final latentVector = await _localEncoder.encodeText(text);
    
    print('✅ Text encoded to ${latentVector.length}D vector');
    print('📊 Vector size: ${latentVector.length * 8} bytes (vs ${text.length} chars)');
    
    // STEP 2: Send ONLY the vector to server (not raw text!)
    final response = await _trafficManager.request(
      'message_send',
      '/messages/send',
      method: 'POST',
      data: {
        'receiver_id': receiverId,
        'intent_type': 'textual',
        'latent_vector': latentVector, // Send vector, not text!
        'content': {
          'hint': text.substring(0, text.length > 20 ? 20 : text.length), // Just a hint
        },
        'priority': priority,
      },
    );
    
    return response.data['message_id'];
  }
  
  /// Send image message - ENCODES LOCALLY FIRST
  Future<String> sendImageMessage({
    required String receiverId,
    required Uint8List imageBytes,
    int priority = 0,
  }) async {
    print('🖼️  Encoding image locally...');
    print('📊 Original image size: ${imageBytes.length} bytes');
    
    // STEP 1: Encode image to latent vector ON DEVICE
    final latentVector = await _localEncoder.encodeImage(imageBytes);
    
    final vectorSize = latentVector.length * 8; // 8 bytes per double
    final compressionRatio = (imageBytes.length / vectorSize * 100).toStringAsFixed(2);
    
    print('✅ Image encoded to ${latentVector.length}D vector');
    print('📊 Vector size: $vectorSize bytes');
    print('🎉 Compression: ${compressionRatio}x smaller!');
    
    // STEP 2: Send ONLY the vector to server (not raw image!)
    final response = await _trafficManager.request(
      'message_send',
      '/messages/send',
      method: 'POST',
      data: {
        'receiver_id': receiverId,
        'intent_type': 'visual',
        'latent_vector': latentVector, // Send vector, not image!
        'content': {
          'hint': 'image',
          'original_size': imageBytes.length,
        },
        'priority': priority,
      },
    );
    
    return response.data['message_id'];
  }
  
  /// Receive messages and decode locally
  Future<List<Message>> receiveMessages({
    String? since,
    int limit = 50,
  }) async {
    final response = await _trafficManager.request(
      'message_receive',
      '/messages/receive',
      method: 'GET',
      queryParameters: {
        if (since != null) 'since': since,
        'limit': limit,
      },
    );
    
    final messages = (response.data['messages'] as List? ?? [])
        .map((json) => Message.fromJson(json))
        .toList();
    
    // Messages already contain latent vectors
    // Decoding happens in UI layer when displaying
    return messages;
  }
  
  /// Get message history
  Future<List<Message>> getMessageHistory({
    required String contactId,
    int limit = 100,
  }) async {
    final response = await _trafficManager.request(
      'message_history',
      '/messages/history/$contactId',
      method: 'GET',
      queryParameters: {'limit': limit},
    );
    
    final messages = (response.data as List? ?? [])
        .map((json) => Message.fromJson(json))
        .toList();
    
    return messages;
  }
  
  /// Mark message as read
  Future<void> markAsRead(String messageId) async {
    await _trafficManager.request(
      'message_send',
      '/messages/read/$messageId',
      method: 'POST',
    );
  }
  
  /// Get messaging statistics
  Future<Map<String, dynamic>> getStats() async {
    final response = await _trafficManager.request(
      'message_send',
      '/messages/stats',
      method: 'GET',
    );
    
    return response.data;
  }
}

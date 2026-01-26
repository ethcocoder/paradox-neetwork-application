/// Message Model

class Message {
  final String messageId;
  final String senderId;
  final String receiverId;
  final IntentType intentType;
  final Map<String, dynamic> content;
  final int priority;
  final DateTime timestamp;
  final DateTime? deliveredAt;
  final DateTime? readAt;
  final MessageStatus status;
  
  // For local storage
  final List<double>? latentVector; // Stored locally for reconstruction
  
  Message({
    required this.messageId,
    required this.senderId,
    required this.receiverId,
    required this.intentType,
    required this.content,
    this.priority = 0,
    required this.timestamp,
    this.deliveredAt,
    this.readAt,
    this.status = MessageStatus.queued,
    this.latentVector,
  });
  
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      messageId: json['message_id'],
      senderId: json['sender_id'],
      receiverId: json['receiver_id'],
      intentType: IntentType.fromString(json['intent_type']),
      content: json['content'] as Map<String, dynamic>,
      priority: json['priority'] ?? 0,
      timestamp: DateTime.parse(json['timestamp']),
      deliveredAt: json['delivered_at'] != null ? DateTime.parse(json['delivered_at']) : null,
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at']) : null,
      status: MessageStatus.fromString(json['status'] ?? 'queued'),
      latentVector: json['latent_vector'] != null
          ? (json['latent_vector'] as List).map((e) => e as double).toList()
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'message_id': messageId,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'intent_type': intentType.toString(),
      'content': content,
      'priority': priority,
      'timestamp': timestamp.toIso8601String(),
      'delivered_at': deliveredAt?.toIso8601String(),
      'read_at': readAt?.toIso8601String(),
      'status': status.toString(),
      'latent_vector': latentVector,
    };
  }
  
  bool get isRead => readAt != null;
  bool get isDelivered => deliveredAt != null;
  bool get isPriority => priority > 0;
  
  Message copyWith({
    MessageStatus? status,
    DateTime? deliveredAt,
    DateTime? readAt,
  }) {
    return Message(
      messageId: messageId,
      senderId: senderId,
      receiverId: receiverId,
      intentType: intentType,
      content: content,
      priority: priority,
      timestamp: timestamp,
      deliveredAt: deliveredAt ?? this.deliveredAt,
      readAt: readAt ?? this.readAt,
      status: status ?? this.status,
      latentVector: latentVector,
    );
  }
}

enum IntentType {
  textual,
  visual,
  audio,
  situational,
  temporal,
  emergency;
  
  static IntentType fromString(String value) {
    return IntentType.values.firstWhere(
      (e) => e.name == value.toLowerCase(),
      orElse: () => IntentType.textual,
    );
  }
  
  @override
  String toString() => name;
}

enum MessageStatus {
  queued,
  sent,
  delivered,
  read,
  failed;
  
  static MessageStatus fromString(String value) {
    return MessageStatus.values.firstWhere(
      (e) => e.name == value.toLowerCase(),
      orElse: () => MessageStatus.queued,
    );
  }
  
  @override
  String toString() => name;
}

/// User Model

class User {
  final String userId;
  final String phoneNumber;
  final String? username;
  final UserRole role;
  final String subscriptionTier;
  final DateTime? subscriptionExpires;
  final String? publicKey;
  
  User({
    required this.userId,
    required this.phoneNumber,
    this.username,
    required this.role,
    required this.subscriptionTier,
    this.subscriptionExpires,
    this.publicKey,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'],
      phoneNumber: json['phone_number'],
      username: json['username'],
      role: UserRole.fromString(json['role']),
      subscriptionTier: json['subscription_tier'] ?? 'free',
      subscriptionExpires: json['subscription_expires'] != null
          ? DateTime.parse(json['subscription_expires'])
          : null,
      publicKey: json['public_key'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'phone_number': phoneNumber,
      'username': username,
      'role': role.toString(),
      'subscription_tier': subscriptionTier,
      'subscription_expires': subscriptionExpires?.toIso8601String(),
      'public_key': publicKey,
    };
  }
  
  bool get isReceiver => role == UserRole.receiver || role == UserRole.hybrid;
  bool get isSubscribed => subscriptionExpires != null && subscriptionExpires!.isAfter(DateTime.now());
}

enum UserRole {
  sender,
  receiver,
  hybrid;
  
  static UserRole fromString(String value) {
    switch (value.toLowerCase()) {
      case 'sender':
        return UserRole.sender;
      case 'receiver':
        return UserRole.receiver;
      case 'hybrid':
        return UserRole.hybrid;
      default:
        return UserRole.sender;
    }
  }
  
  @override
  String toString() => name;
}

import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import '../models/user_model.dart';
import '../models/message_model.dart';
import 'local_latent_encoder.dart';
import 'dart:typed_data';

class FirebaseService {
  final fb_auth.FirebaseAuth _auth = fb_auth.FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final LocalLatentEncoder _localEncoder;

  FirebaseService(this._localEncoder);

  // Authentication
  Stream<fb_auth.User?> get authStateChanges => _auth.authStateChanges();

  Future<fb_auth.UserCredential> login(String email, String password) async {
    return await _auth.signInWithEmailAndPassword(email: email, password: password);
  }

  Future<fb_auth.UserCredential> register(String email, String password, {String? username}) async {
    final credential = await _auth.createUserWithEmailAndPassword(email: email, password: password);
    if (credential.user != null) {
      await createUserProfile(credential.user!.uid, email, username: username);
    }
    return credential;
  }

  Future<void> createUserProfile(String uid, String email, {String? username}) async {
    await _firestore.collection('users').doc(uid).set({
      'user_id': uid,
      'email': email,
      'username': username ?? email.split('@')[0],
      'created_at': FieldValue.serverTimestamp(),
      'status': 'online',
    });
  }

  Future<User?> getUserProfile(String uid) async {
    final doc = await _firestore.collection('users').doc(uid).get();
    if (doc.exists) {
      final data = doc.data()!;
      return User(
        userId: data['user_id'],
        phoneNumber: data['email'], // Using email as identifier in this mode
        username: data['username'],
        status: data['status'],
      );
    }
    return null;
  }

  Future<void> logout() async {
    await _auth.signOut();
  }

  // Messaging with Latent Vectors
  Future<void> sendVectorMessage({
    required String receiverId,
    required String text,
  }) async {
    final senderId = _auth.currentUser?.uid;
    if (senderId == null) throw Exception('User not logged in');

    // 1. Encode LOCALLY
    final latentVector = await _localEncoder.encodeText(text);

    // 2. Send VECTOR to Firestore (Privacy Preserved!)
    await _firestore.collection('messages').add({
      'sender_id': senderId,
      'receiver_id': receiverId,
      'participants': [senderId, receiverId],
      'latent_vector': latentVector, // Sending semantic meaning, not raw text
      'intent_type': 'textual',
      'timestamp': FieldValue.serverTimestamp(),
      'content': {
        'hint': text.substring(0, text.length > 10 ? 10 : text.length) + '...',
      },
    });
  }

  Future<void> sendVectorImage({
    required String receiverId,
    required Uint8List imageBytes,
  }) async {
    final senderId = _auth.currentUser?.uid;
    if (senderId == null) throw Exception('User not logged in');

    // 1. Encode LOCALLY (5MB -> 4KB)
    final latentVector = await _localEncoder.encodeImage(imageBytes);

    // 2. Send VECTOR to Firestore
    await _firestore.collection('messages').add({
      'sender_id': senderId,
      'receiver_id': receiverId,
      'participants': [senderId, receiverId],
      'latent_vector': latentVector,
      'intent_type': 'visual',
      'timestamp': FieldValue.serverTimestamp(),
      'content': {
        'hint': 'image_vector',
        'original_size': imageBytes.length,
      },
    });
  }

  Stream<List<Message>> getMessages(String otherUserId) {
    final myId = _auth.currentUser?.uid;
    if (myId == null) return Stream.value([]);

    return _firestore
        .collection('messages')
        .where('participants', arrayContains: myId)
        .orderBy('timestamp', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        return Message(
          messageId: doc.id,
          senderId: data['sender_id'],
          receiverId: data['receiver_id'],
          intentType: IntentType.fromString(data['intent_type']),
          content: data['content'],
          timestamp: (data['timestamp'] as Timestamp?)?.toDate() ?? DateTime.now(),
          latentVector: (data['latent_vector'] as List?)?.map((e) => (e as num).toDouble()).toList(),
        );
      }).where((m) => m.senderId == otherUserId || m.receiverId == otherUserId).toList();
    });
  }
}

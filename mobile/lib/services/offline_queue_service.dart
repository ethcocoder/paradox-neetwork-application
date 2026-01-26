/// Offline Queue Service  
/// Stores messages locally when device is offline

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/message_model.dart';
import '../config/app_config.dart';

class OfflineQueueService {
  static Database? _database;
  
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }
  
  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'offline_queue.db');
    
    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE offline_queue (
            message_id TEXT PRIMARY KEY,
            receiver_id TEXT NOT NULL,
            intent_type TEXT NOT NULL,
            content TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0
          )
        ''');
      },
    );
  }
  
  /// Queue message for offline sending
  Future<void> queueMessage(Message message) async {
    final db = await database;
    
    // Check queue size
    final count = Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM offline_queue'),
    );
    
    if (count != null && count >= AppConfig.maxOfflineQueueSize) {
      throw Exception('Offline queue full (max ${AppConfig.maxOfflineQueueSize})');
    }
    
    await db.insert(
      'offline_queue',
      {
        'message_id': message.messageId,
        'receiver_id': message.receiverId,
        'intent_type': message.intentType.toString(),
        'content': message.content.toString(),
        'priority': message.priority,
        'created_at': message.timestamp.toIso8601String(),
        'retry_count': 0,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
  
  /// Get all queued messages
  Future<List<Map<String, dynamic>>> getQueuedMessages() async {
    final db = await database;
    return await db.query(
      'offline_queue',
      orderBy: 'priority DESC, created_at ASC',
    );
  }
  
  /// Remove message from queue after successful send
  Future<void> removeFromQueue(String messageId) async {
    final db = await database;
    await db.delete(
      'offline_queue',
      where: 'message_id = ?',
      whereArgs: [messageId],
    );
  }
  
  /// Increment retry count
  Future<void> incrementRetryCount(String messageId) async {
    final db = await database;
    await db.rawUpdate(
      'UPDATE offline_queue SET retry_count = retry_count + 1 WHERE message_id = ?',
      [messageId],
    );
  }
  
  /// Get queue size
  Future<int> getQueueSize() async {
    final db = await database;
    return Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM offline_queue'),
    ) ?? 0;
  }
  
  /// Clear entire queue
  Future<void> clearQueue() async {
    final db = await database;
    await db.delete('offline_queue');
  }
}

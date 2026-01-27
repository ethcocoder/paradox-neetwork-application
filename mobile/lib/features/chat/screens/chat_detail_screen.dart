import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data';
import 'package:paradox_network_app/theme/app_theme.dart';
import 'package:paradox_network_app/services/messaging_service.dart';
import 'package:paradox_network_app/services/local_latent_decoder.dart';
import 'package:paradox_network_app/models/message_model.dart';

class ChatDetailScreen extends StatefulWidget {
  final String contactId;
  final String contactName;

  const ChatDetailScreen({
    Key? key,
    required this.contactId,
    required this.contactName,
  }) : super(key: key);

  @override
  State<ChatDetailScreen> createState() => _ChatDetailScreenState();
}

class _ChatDetailScreenState extends State<ChatDetailScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Message> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    try {
      final history = await context.read<MessagingService>().getMessageHistory(
        contactId: widget.contactId,
      );
      setState(() {
        _messages.addAll(history);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      // Handle error
    }
  }

  void _sendMessage() async {
    if (_controller.text.isEmpty) return;
    
    final text = _controller.text;
    _controller.clear();
    
    try {
      await context.read<MessagingService>().sendTextMessage(
        receiverId: widget.contactId,
        text: text,
      );
      // In a real app, we'd wait for the message to come back via WS or poll
      // For MVP, we'll just add a local mock message
      setState(() {
        _messages.insert(0, Message(
          messageId: DateTime.now().toString(),
          senderId: 'me',
          receiverId: widget.contactId,
          intentType: IntentType.textual,
          content: {'hint': text},
          timestamp: DateTime.now(),
          status: MessageStatus.sent,
        ));
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send: $e')),
      );
    }
  }

  void _sendImage() async {
    // Mock image sending for MVP
    // In a real app, use image_picker to get bytes
    final mockImageBytes = Uint8List.fromList(List.generate(100, (i) => i));
    
    try {
      await context.read<MessagingService>().sendImageMessage(
        receiverId: widget.contactId,
        imageBytes: mockImageBytes,
      );
      setState(() {
        _messages.insert(0, Message(
          messageId: DateTime.now().toString(),
          senderId: 'me',
          receiverId: widget.contactId,
          intentType: IntentType.visual,
          content: {'hint': 'image'},
          timestamp: DateTime.now(),
          status: MessageStatus.sent,
        ));
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send image: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.contactName),
            Text(
              'Latent Channel Secure',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.green),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: _isLoading 
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  reverse: true,
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    final isMe = msg.senderId == 'me';
                    
                    return Align(
                      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isMe ? AppTheme.primaryColor : Colors.grey[800],
                          borderRadius: BorderRadius.circular(16),
                        ),
                        constraints: BoxConstraints(
                          maxWidth: MediaQuery.of(context).size.width * 0.7,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (msg.intentType == IntentType.visual)
                              const Icon(Icons.image, color: Colors.white, size: 40)
                            else
                              Text(
                                msg.content['hint'] ?? '',
                                style: const TextStyle(color: Colors.white),
                              ),
                            const SizedBox(height: 4),
                            Text(
                              '${msg.timestamp.hour}:${msg.timestamp.minute}',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.6),
                                fontSize: 10,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
          ),
          _buildInput(),
        ],
      ),
    );
  }

  Widget _buildInput() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.image_outlined, color: AppTheme.primaryColor),
              onPressed: _sendImage,
            ),
            Expanded(
              child: TextField(
                controller: _controller,
                decoration: InputDecoration(
                  hintText: 'Type a message...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Colors.grey[900],
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: AppTheme.primaryColor,
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: _sendMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

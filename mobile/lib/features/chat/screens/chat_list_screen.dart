import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:paradox_network_app/theme/app_theme.dart';
import 'package:paradox_network_app/providers/auth_provider.dart';
import 'package:paradox_network_app/features/chat/screens/chat_detail_screen.dart';

class ChatListScreen extends StatelessWidget {
  const ChatListScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Paradox Network'),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_balance_wallet_outlined),
            onPressed: () => Navigator.pushNamed(context, '/subscription'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              context.read<AuthProvider>().logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Zero-Rated Status Banner
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: Colors.green.withOpacity(0.1),
            child: Row(
              children: [
                const Icon(Icons.bolt, color: Colors.green, size: 16),
                const SizedBox(width: 8),
                Text(
                  'Zero-Rated Lane Active (Ethio Telecom)',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          
          Expanded(
            child: ListView.separated(
              itemCount: 5, // Mock data for now
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final names = ['Abebe', 'Kebede', 'Almaz', 'Mulugeta', 'Tigist'];
                final lastMessages = [
                  'Did you see the latent vector?',
                  'The compression is insane!',
                  'Meet you at 5 PM.',
                  'Sent you an image.',
                  'Is the network stable?'
                ];
                
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
                    child: Text(names[index][0], style: const TextStyle(color: AppTheme.primaryColor)),
                  ),
                  title: Text(names[index], style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(lastMessages[index], maxLines: 1, overflow: TextOverflow.ellipsis),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('12:3${index} PM', style: Theme.of(context).textTheme.bodySmall),
                      if (index == 0)
                        Container(
                          margin: const EdgeInsets.only(top: 4),
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(color: AppTheme.primaryColor, shape: BoxShape.circle),
                          child: const Text('1', style: TextStyle(color: Colors.white, fontSize: 10)),
                        ),
                    ],
                  ),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ChatDetailScreen(
                          contactId: 'user_$index',
                          contactName: names[index],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: const Icon(Icons.message),
      ),
    );
  }
}

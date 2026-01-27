import 'package:flutter/material.dart';
import 'package:paradox_network_app/theme/app_theme.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Subscription'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCurrentStatus(context),
            const SizedBox(height: 32),
            Text(
              'Available Plans',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildPlanCard(
              context,
              title: 'Daily Pass',
              price: '2 ETB',
              description: 'Unlimited zero-rated messaging for 24 hours.',
              isPopular: false,
            ),
            const SizedBox(height: 16),
            _buildPlanCard(
              context,
              title: 'Weekly Pro',
              price: '10 ETB',
              description: 'Unlimited zero-rated messaging + 50MB Lane B data.',
              isPopular: true,
            ),
            const SizedBox(height: 16),
            _buildPlanCard(
              context,
              title: 'Monthly Elite',
              price: '35 ETB',
              description: 'Unlimited zero-rated messaging + 250MB Lane B data + Priority Support.',
              isPopular: false,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStatus(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Current Plan',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              Icon(Icons.verified, color: Colors.white, size: 20),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Free Tier (Active)',
            style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Divider(color: Colors.white24),
          const SizedBox(height: 16),
          Row(
            children: [
              const Icon(Icons.info_outline, color: Colors.white70, size: 16),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Your zero-rated access is sponsored by Ethio Telecom.',
                  style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 12),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPlanCard(
    BuildContext context, {
    required String title,
    required String price,
    required String description,
    required bool isPopular,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: isPopular ? Border.all(color: AppTheme.primaryColor, width: 2) : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (isPopular)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              margin: const EdgeInsets.only(bottom: 8),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor,
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                'MOST POPULAR',
                style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              Text(price, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
            ],
          ),
          const SizedBox(height: 8),
          Text(description, style: TextStyle(color: Colors.white.withOpacity(0.7))),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: isPopular ? AppTheme.primaryColor : Colors.white10,
                foregroundColor: Colors.white,
              ),
              child: const Text('Upgrade Now'),
            ),
          ),
        ],
      ),
    );
  }
}

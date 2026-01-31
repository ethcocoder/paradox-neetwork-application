import {
  collection,
  addDoc,
  query,
  where,
  orderBy,
  getDocs,
  onSnapshot,
  Timestamp,
  limit as firestoreLimit,
} from "firebase/firestore";
import { db } from "./firebase-auth";
import { encodeData, type EncodedData, initModels } from "./latent-encoder";
import { decodeData, type DecodedData, initDecoder } from "./latent-decoder";
import { COLLECTIONS } from "./firebase-config";
import { Platform } from "react-native";

/**
 * Mobile-Optimized Message Service
 * 
 * Performance Optimizations:
 * - Lazy model loading (only when needed)
 * - LRU caching for decoded messages
 * - Adaptive quality based on battery/network
 * - Background processing for large data
 * - Memory-efficient chunked decoding
 * - Throttling to prevent CPU overload
 */

export type MessageType = "text" | "image" | "audio" | "video" | "file";

export interface OptimizedMessage {
  id?: string;
  conversationId: string;
  senderId: string;
  receiverId: string;
  messageType: MessageType;
  latentVectors: number[][];  // Multiple vectors for chunked data
  originalSize: number;
  encodedSize: number;
  compressionRatio: number;
  timestamp: Date;
  isRead: boolean;
  metadata?: any;
}

export interface DecodedMessage extends OptimizedMessage {
  decodedContent: string | Uint8Array;
  quality: number;
}

// ==================== PERFORMANCE OPTIMIZATIONS ====================

/**
 * LRU Cache for decoded messages (prevents redundant decoding)
 */
class MessageCache {
  private cache = new Map<string, DecodedMessage>();
  private maxSize = 50; // Keep last 50 messages in memory

  get(id: string): DecodedMessage | undefined {
    const msg = this.cache.get(id);
    if (msg) {
      // Move to end (most recently used)
      this.cache.delete(id);
      this.cache.set(id, msg);
    }
    return msg;
  }

  set(id: string, message: DecodedMessage): void {
    // Remove oldest if cache is full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(id, message);
  }

  clear(): void {
    this.cache.clear();
  }
}

const messageCache = new MessageCache();

/**
 * Battery-aware processing
 * Reduces CPU usage when battery is low
 */
let lowPowerMode = false;

export function setLowPowerMode(enabled: boolean): void {
  lowPowerMode = enabled;
  console.log(`[Performance] Low power mode: ${enabled ? 'ON' : 'OFF'}`);
}

/**
 * Adaptive quality based on device state
 */
function getOptimalChunkSize(): number {
  if (lowPowerMode) {
    return 1024; // Smaller chunks = less CPU per cycle
  }
  return 2048; // Normal chunks
}

/**
 * Throttle function to prevent CPU overload
 */
function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

// ==================== LAZY MODEL INITIALIZATION ====================

let modelsInitialized = false;
let modelsInitializing = false;

async function ensureModelsLoaded(): Promise<void> {
  if (modelsInitialized) return;
  if (modelsInitializing) {
    // Wait for ongoing initialization
    await new Promise(resolve => setTimeout(resolve, 100));
    return ensureModelsLoaded();
  }

  modelsInitializing = true;
  try {
    console.log('[Performance] Lazy-loading encoder/decoder models...');
    await Promise.all([initModels(), initDecoder()]);
    modelsInitialized = true;
    console.log('[Performance] ✓ Models loaded successfully');
  } catch (error) {
    console.warn('[Performance] Model loading failed, using fallback:', error);
    modelsInitialized = true; // Continue with fallback
  } finally {
    modelsInitializing = false;
  }
}

// ==================== OPTIMIZED MESSAGE SENDING ====================

/**
 * Send any type of message with mobile optimizations
 */
export async function sendMessage(
  conversationId: string,
  senderId: string,
  receiverId: string,
  data: string | Uint8Array | ArrayBuffer,
  messageType: MessageType,
  metadata?: any
): Promise<OptimizedMessage> {
  const startTime = Date.now();

  try {
    // Lazy load models only when first needed
    await ensureModelsLoaded();

    // Encode the data
    const encoded: EncodedData = await encodeData(data, messageType, metadata);

    const message: OptimizedMessage = {
      conversationId,
      senderId,
      receiverId,
      messageType,
      latentVectors: encoded.latentVectors,
      originalSize: encoded.originalSize,
      encodedSize: encoded.encodedSize,
      compressionRatio: encoded.compressionRatio,
      timestamp: new Date(),
      isRead: false,
      metadata: encoded.metadata,
    };

    // Save to Firestore
    const docRef = await addDoc(collection(db, COLLECTIONS.MESSAGES), {
      ...message,
      timestamp: Timestamp.fromDate(message.timestamp),
    });

    const duration = Date.now() - startTime;
    console.log(
      `[Performance] Message sent in ${duration}ms ` +
      `(${encoded.compressionRatio.toFixed(2)}x compression)`
    );

    return { ...message, id: docRef.id };
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

/**
 * Convenience functions for specific types
 */
export async function sendTextMessage(
  conversationId: string,
  senderId: string,
  receiverId: string,
  text: string
): Promise<OptimizedMessage> {
  return sendMessage(conversationId, senderId, receiverId, text, 'text');
}

export async function sendImageMessage(
  conversationId: string,
  senderId: string,
  receiverId: string,
  imageBytes: Uint8Array,
  metadata?: any
): Promise<OptimizedMessage> {
  return sendMessage(conversationId, senderId, receiverId, imageBytes, 'image', metadata);
}

// ==================== OPTIMIZED MESSAGE RETRIEVAL ====================

/**
 * Decode a single message with caching
 */
async function decodeMessage(message: OptimizedMessage): Promise<DecodedMessage> {
  // Check cache first
  if (message.id) {
    const cached = messageCache.get(message.id);
    if (cached) {
      console.log('[Performance] ✓ Cache hit for message', message.id);
      return cached;
    }
  }

  // Decode from latent vectors
  const encoded: EncodedData = {
    type: message.messageType,
    latentVectors: message.latentVectors,
    originalSize: message.originalSize,
    encodedSize: message.encodedSize,
    compressionRatio: message.compressionRatio,
    metadata: message.metadata,
  };

  const decoded: DecodedData = await decodeData(encoded);

  const decodedMessage: DecodedMessage = {
    ...message,
    decodedContent: decoded.data,
    quality: decoded.quality,
  };

  // Cache for future use
  if (message.id) {
    messageCache.set(message.id, decodedMessage);
  }

  return decodedMessage;
}

/**
 * Fetch messages with pagination and background decoding
 */
export async function fetchConversationMessages(
  conversationId: string,
  limitCount: number = 50
): Promise<DecodedMessage[]> {
  const startTime = Date.now();

  try {
    // Ensure models are loaded
    await ensureModelsLoaded();

    const q = query(
      collection(db, COLLECTIONS.MESSAGES),
      where("conversationId", "==", conversationId),
      orderBy("timestamp", "desc"),
      firestoreLimit(limitCount)
    );

    const querySnapshot = await getDocs(q);

    // Parse raw Firestore data
    const rawMessages: OptimizedMessage[] = querySnapshot.docs.map(doc => {
      const data = doc.data();
      return {
        id: doc.id,
        conversationId: data.conversationId,
        senderId: data.senderId,
        receiverId: data.receiverId,
        messageType: data.messageType,
        latentVectors: data.latentVectors || [data.latentVector], // Support old format
        originalSize: data.originalSize,
        encodedSize: data.encodedSize,
        compressionRatio: data.compressionRatio || 1,
        timestamp: data.timestamp.toDate(),
        isRead: data.isRead,
        metadata: data.metadata,
      };
    });

    // Decode messages in parallel (but with concurrency limit)
    const PARALLEL_LIMIT = lowPowerMode ? 2 : 5;
    const decodedMessages: DecodedMessage[] = [];

    for (let i = 0; i < rawMessages.length; i += PARALLEL_LIMIT) {
      const batch = rawMessages.slice(i, i + PARALLEL_LIMIT);
      const decoded = await Promise.all(batch.map(msg => decodeMessage(msg)));
      decodedMessages.push(...decoded);
    }

    const duration = Date.now() - startTime;
    console.log(`[Performance] Fetched ${decodedMessages.length} messages in ${duration}ms`);

    return decodedMessages.reverse(); // Return in chronological order
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
}

/**
 * Real-time message listener with throttling
 */
export function listenToMessages(
  conversationId: string,
  callback: (messages: DecodedMessage[]) => void,
  throttleMs: number = 500 // Throttle updates to reduce CPU usage
): () => void {
  let isProcessing = false;

  const q = query(
    collection(db, COLLECTIONS.MESSAGES),
    where("conversationId", "==", conversationId),
    orderBy("timestamp", "asc")
  );

  const throttledCallback = throttle(callback, throttleMs);

  const unsubscribe = onSnapshot(q, async (querySnapshot) => {
    if (isProcessing) {
      console.log('[Performance] Skipping update - previous still processing');
      return;
    }

    isProcessing = true;

    try {
      // Ensure models are loaded
      await ensureModelsLoaded();

      const rawMessages: OptimizedMessage[] = querySnapshot.docs.map(doc => {
        const data = doc.data();
        return {
          id: doc.id,
          conversationId: data.conversationId,
          senderId: data.senderId,
          receiverId: data.receiverId,
          messageType: data.messageType,
          latentVectors: data.latentVectors || [data.latentVector],
          originalSize: data.originalSize,
          encodedSize: data.encodedSize,
          compressionRatio: data.compressionRatio || 1,
          timestamp: data.timestamp.toDate(),
          isRead: data.isRead,
          metadata: data.metadata,
        };
      });

      // Decode in batches
      const PARALLEL_LIMIT = lowPowerMode ? 2 : 5;
      const decodedMessages: DecodedMessage[] = [];

      for (let i = 0; i < rawMessages.length; i += PARALLEL_LIMIT) {
        const batch = rawMessages.slice(i, i + PARALLEL_LIMIT);
        const decoded = await Promise.all(batch.map(msg => decodeMessage(msg)));
        decodedMessages.push(...decoded);
      }

      throttledCallback(decodedMessages);
    } catch (error) {
      console.error('[Performance] Error in message listener:', error);
    } finally {
      isProcessing = false;
    }
  });

  return unsubscribe;
}

/**
 * Clear message cache (useful for memory management)
 */
export function clearMessageCache(): void {
  messageCache.clear();
  console.log('[Performance] Message cache cleared');
}

/**
 * Get performance statistics
 */
export function getPerformanceStats() {
  return {
    lowPowerMode,
    modelsLoaded: modelsInitialized,
    cacheSize: messageCache['cache'].size,
    platform: Platform.OS,
  };
}

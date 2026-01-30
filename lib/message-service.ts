import {
  collection,
  addDoc,
  query,
  where,
  orderBy,
  getDocs,
  onSnapshot,
  Timestamp,
} from "firebase/firestore";
import { db } from "./firebase-auth";
import { encodeText, encodeImage, estimateBandwidthSavings } from "./latent-encoder";
import { decodeText, decodeImage } from "./latent-decoder";
import { COLLECTIONS } from "./firebase-config";

export interface EncodedMessage {
  id?: string;
  conversationId: string;
  senderId: string;
  receiverId: string;
  messageType: "text" | "image";
  latentVector: number[];
  originalSize: number;
  encodedSize: number;
  bandwidthSavingsPercent: number;
  timestamp: Date;
  isRead: boolean;
}

export interface DecodedMessage extends EncodedMessage {
  decodedContent: string | { description: string; colorProfile: any };
}

/**
 * Send an encoded text message
 */
export async function sendTextMessage(
  conversationId: string,
  senderId: string,
  receiverId: string,
  text: string
): Promise<EncodedMessage> {
  try {
    // Encode text to latent vector
    const latentVector = encodeText(text);
    const originalSize = new TextEncoder().encode(text).length;
    const { encodedSize, savingsPercent } = estimateBandwidthSavings(originalSize);

    const message: EncodedMessage = {
      conversationId,
      senderId,
      receiverId,
      messageType: "text",
      latentVector,
      originalSize,
      encodedSize,
      bandwidthSavingsPercent: savingsPercent,
      timestamp: new Date(),
      isRead: false,
    };

    // Save to Firestore
    const docRef = await addDoc(collection(db, COLLECTIONS.MESSAGES), {
      ...message,
      timestamp: Timestamp.fromDate(message.timestamp),
    });

    return { ...message, id: docRef.id };
  } catch (error) {
    console.error("Error sending text message:", error);
    throw error;
  }
}

/**
 * Send an encoded image message
 */
export async function sendImageMessage(
  conversationId: string,
  senderId: string,
  receiverId: string,
  imageData: Uint8Array
): Promise<EncodedMessage> {
  try {
    // Encode image to latent vector
    const latentVector = encodeImage(imageData);
    const originalSize = imageData.length;
    const { encodedSize, savingsPercent } = estimateBandwidthSavings(originalSize);

    const message: EncodedMessage = {
      conversationId,
      senderId,
      receiverId,
      messageType: "image",
      latentVector,
      originalSize,
      encodedSize,
      bandwidthSavingsPercent: savingsPercent,
      timestamp: new Date(),
      isRead: false,
    };

    // Save to Firestore
    const docRef = await addDoc(collection(db, COLLECTIONS.MESSAGES), {
      ...message,
      timestamp: Timestamp.fromDate(message.timestamp),
    });

    return { ...message, id: docRef.id };
  } catch (error) {
    console.error("Error sending image message:", error);
    throw error;
  }
}

/**
 * Fetch messages for a conversation
 */
export async function fetchConversationMessages(
  conversationId: string
): Promise<DecodedMessage[]> {
  try {
    const q = query(
      collection(db, COLLECTIONS.MESSAGES),
      where("conversationId", "==", conversationId),
      orderBy("timestamp", "asc")
    );

    const querySnapshot = await getDocs(q);
    const messages: DecodedMessage[] = [];

    for (const doc of querySnapshot.docs) {
      const data = doc.data() as any;
      const message: EncodedMessage = {
        id: doc.id,
        conversationId: data.conversationId,
        senderId: data.senderId,
        receiverId: data.receiverId,
        messageType: data.messageType,
        latentVector: data.latentVector,
        originalSize: data.originalSize,
        encodedSize: data.encodedSize,
        bandwidthSavingsPercent: data.bandwidthSavingsPercent,
        timestamp: data.timestamp.toDate(),
        isRead: data.isRead,
      };

      // Decode message
      let decodedContent;
      if (data.messageType === "text") {
        decodedContent = decodeText(data.latentVector);
      } else {
        decodedContent = decodeImage(data.latentVector);
      }

      messages.push({
        ...message,
        decodedContent,
      });
    }

    return messages;
  } catch (error) {
    console.error("Error fetching messages:", error);
    throw error;
  }
}

/**
 * Listen to real-time message updates for a conversation
 */
export function listenToMessages(
  conversationId: string,
  callback: (messages: DecodedMessage[]) => void
): () => void {
  const q = query(
    collection(db, COLLECTIONS.MESSAGES),
    where("conversationId", "==", conversationId),
    orderBy("timestamp", "asc")
  );

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const messages: DecodedMessage[] = [];

    for (const doc of querySnapshot.docs) {
      const data = doc.data() as any;
      const message: EncodedMessage = {
        id: doc.id,
        conversationId: data.conversationId,
        senderId: data.senderId,
        receiverId: data.receiverId,
        messageType: data.messageType,
        latentVector: data.latentVector,
        originalSize: data.originalSize,
        encodedSize: data.encodedSize,
        bandwidthSavingsPercent: data.bandwidthSavingsPercent,
        timestamp: data.timestamp.toDate(),
        isRead: data.isRead,
      };

      // Decode message
      let decodedContent;
      if (data.messageType === "text") {
        decodedContent = decodeText(data.latentVector);
      } else {
        decodedContent = decodeImage(data.latentVector);
      }

      messages.push({
        ...message,
        decodedContent,
      });
    }

    callback(messages);
  });

  return unsubscribe;
}

/**
 * Get conversation statistics
 */
export async function getConversationStats(
  conversationId: string
): Promise<{
  totalMessages: number;
  totalBandwidthSaved: number;
  averageSavingsPercent: number;
}> {
  try {
    const messages = await fetchConversationMessages(conversationId);

    const totalMessages = messages.length;
    const totalBandwidthSaved = messages.reduce(
      (sum, msg) => sum + (msg.originalSize - msg.encodedSize),
      0
    );
    const averageSavingsPercent =
      messages.length > 0
        ? messages.reduce((sum, msg) => sum + msg.bandwidthSavingsPercent, 0) /
          messages.length
        : 0;

    return {
      totalMessages,
      totalBandwidthSaved,
      averageSavingsPercent,
    };
  } catch (error) {
    console.error("Error getting conversation stats:", error);
    throw error;
  }
}

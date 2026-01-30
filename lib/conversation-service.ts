import {
  collection,
  addDoc,
  query,
  where,
  getDocs,
  onSnapshot,
  Timestamp,
  doc,
  updateDoc,
  orderBy,
  limit,
} from "firebase/firestore";
import { db } from "./firebase-auth";
import { COLLECTIONS } from "./firebase-config";

export interface Conversation {
  id?: string;
  participants: string[]; // [userId1, userId2]
  lastMessage?: string;
  lastMessageTime?: Date;
  lastMessageSender?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Create a new conversation between two users
 */
export async function createConversation(
  userId1: string,
  userId2: string
): Promise<Conversation> {
  try {
    // Check if conversation already exists
    const existing = await getConversation(userId1, userId2);
    if (existing) {
      return existing;
    }

    const conversation: Conversation = {
      participants: [userId1, userId2].sort(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const docRef = await addDoc(collection(db, COLLECTIONS.CONVERSATIONS), {
      ...conversation,
      createdAt: Timestamp.fromDate(conversation.createdAt),
      updatedAt: Timestamp.fromDate(conversation.updatedAt),
    });

    return { ...conversation, id: docRef.id };
  } catch (error) {
    console.error("Error creating conversation:", error);
    throw error;
  }
}

/**
 * Get conversation between two users
 */
export async function getConversation(
  userId1: string,
  userId2: string
): Promise<Conversation | null> {
  try {
    const sortedIds = [userId1, userId2].sort();

    const q = query(
      collection(db, COLLECTIONS.CONVERSATIONS),
      where("participants", "==", sortedIds)
    );

    const querySnapshot = await getDocs(q);

    if (querySnapshot.empty) {
      return null;
    }

    const doc = querySnapshot.docs[0];
    const data = doc.data() as any;

    return {
      id: doc.id,
      participants: data.participants,
      lastMessage: data.lastMessage,
      lastMessageTime: data.lastMessageTime?.toDate(),
      lastMessageSender: data.lastMessageSender,
      createdAt: data.createdAt.toDate(),
      updatedAt: data.updatedAt.toDate(),
    };
  } catch (error) {
    console.error("Error getting conversation:", error);
    return null;
  }
}

/**
 * Get all conversations for a user
 */
export async function getUserConversations(userId: string): Promise<Conversation[]> {
  try {
    const q = query(
      collection(db, COLLECTIONS.CONVERSATIONS),
      where("participants", "array-contains", userId),
      orderBy("updatedAt", "desc")
    );

    const querySnapshot = await getDocs(q);
    const conversations: Conversation[] = [];

    for (const doc of querySnapshot.docs) {
      const data = doc.data() as any;
      conversations.push({
        id: doc.id,
        participants: data.participants,
        lastMessage: data.lastMessage,
        lastMessageTime: data.lastMessageTime?.toDate(),
        lastMessageSender: data.lastMessageSender,
        createdAt: data.createdAt.toDate(),
        updatedAt: data.updatedAt.toDate(),
      });
    }

    return conversations;
  } catch (error) {
    console.error("Error getting user conversations:", error);
    return [];
  }
}

/**
 * Update conversation with last message info
 */
export async function updateConversationLastMessage(
  conversationId: string,
  lastMessage: string,
  senderId: string
): Promise<void> {
  try {
    const conversationRef = doc(db, COLLECTIONS.CONVERSATIONS, conversationId);
    await updateDoc(conversationRef, {
      lastMessage,
      lastMessageSender: senderId,
      lastMessageTime: Timestamp.fromDate(new Date()),
      updatedAt: Timestamp.fromDate(new Date()),
    });
  } catch (error) {
    console.error("Error updating conversation:", error);
    throw error;
  }
}

/**
 * Listen to user conversations in real-time
 */
export function listenToUserConversations(
  userId: string,
  callback: (conversations: Conversation[]) => void
): () => void {
  const q = query(
    collection(db, COLLECTIONS.CONVERSATIONS),
    where("participants", "array-contains", userId),
    orderBy("updatedAt", "desc")
  );

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const conversations: Conversation[] = [];

    for (const doc of querySnapshot.docs) {
      const data = doc.data() as any;
      conversations.push({
        id: doc.id,
        participants: data.participants,
        lastMessage: data.lastMessage,
        lastMessageTime: data.lastMessageTime?.toDate(),
        lastMessageSender: data.lastMessageSender,
        createdAt: data.createdAt.toDate(),
        updatedAt: data.updatedAt.toDate(),
      });
    }

    callback(conversations);
  });

  return unsubscribe;
}

/**
 * Get other participant in conversation
 */
export function getOtherParticipant(
  conversation: Conversation,
  currentUserId: string
): string {
  return conversation.participants.find((id) => id !== currentUserId) || "";
}

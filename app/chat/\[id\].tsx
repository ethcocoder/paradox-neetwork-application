import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
} from "react-native";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import { useAuth } from "@/hooks/use-auth";
import {
  listenToMessages,
  sendTextMessage,
  sendImageMessage,
  DecodedMessage,
} from "@/lib/message-service";
import { getOtherParticipant } from "@/lib/conversation-service";
import { doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase-auth";
import { COLLECTIONS } from "@/lib/firebase-config";

export default function ChatScreen() {
  const { id: conversationId } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const [messages, setMessages] = useState<DecodedMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [otherUser, setOtherUser] = useState<any>(null);
  const flatListRef = useRef<FlatList>(null);
  const router = useRouter();

  useEffect(() => {
    if (!conversationId || !user) return;

    // Fetch other user info
    const fetchOtherUser = async () => {
      try {
        // In a real app, we'd get the conversation first to find the other participant
        // For now, we'll assume we can find it or just show the ID
        const convRef = doc(db, COLLECTIONS.CONVERSATIONS, conversationId);
        const convSnap = await getDoc(convRef);
        if (convSnap.exists()) {
          const data = convSnap.data();
          const otherId = data.participants.find((p: string) => p !== user.uid);
          if (otherId) {
            const userRef = doc(db, COLLECTIONS.USERS, otherId);
            const userSnap = await getDoc(userRef);
            if (userSnap.exists()) {
              setOtherUser(userSnap.data());
            }
          }
        }
      } catch (error) {
        console.error("Error fetching other user:", error);
      }
    };

    fetchOtherUser();

    // Listen to messages
    const unsubscribe = listenToMessages(conversationId, (newMessages) => {
      setMessages(newMessages);
      setLoading(false);
      // Scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    });

    return () => unsubscribe();
  }, [conversationId, user]);

  const handleSend = async () => {
    if (!inputText.trim() || !user || !conversationId || !otherUser) return;

    const text = inputText.trim();
    setInputText("");
    setSending(true);

    try {
      await sendTextMessage(
        conversationId,
        user.uid,
        otherUser.uid,
        text
      );
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const renderMessage = ({ item }: { item: DecodedMessage }) => {
    const isMe = item.senderId === user?.uid;

    return (
      <View
        style={[
          styles.messageContainer,
          isMe ? styles.myMessage : styles.theirMessage,
        ]}
      >
        <View
          style={[
            styles.bubble,
            isMe ? styles.myBubble : styles.theirBubble,
          ]}
        >
          {item.messageType === "text" ? (
            <Text style={[styles.messageText, isMe ? styles.myText : styles.theirText]}>
              {typeof item.decodedContent === "string" ? item.decodedContent : "Decoded content error"}
            </Text>
          ) : (
            <View>
               <Text style={styles.imagePlaceholder}>[Encoded Image Decoded]</Text>
               <Text style={styles.imageDescription}>
                 {typeof item.decodedContent === 'object' ? (item.decodedContent as any).description : 'Image'}
               </Text>
            </View>
          )}
        </View>
        <View style={styles.savingsContainer}>
            <Text style={styles.savingsText}>
                Saved {item.bandwidthSavingsPercent.toFixed(1)}% bandwidth
            </Text>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0a7ea4" />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
      keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
    >
      <Stack.Screen 
        options={{ 
          title: otherUser?.displayName || "Chat",
          headerBackTitle: "Back"
        }} 
      />
      
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id || Math.random().toString()}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      <View style={styles.inputContainer}>
        <TouchableOpacity style={styles.attachButton}>
          <Text style={styles.attachButtonText}>+</Text>
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          placeholder="Type a message..."
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <TouchableOpacity
          style={[styles.sendButton, !inputText.trim() && styles.disabledButton]}
          onPress={handleSend}
          disabled={!inputText.trim() || sending}
        >
          {sending ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  messageList: {
    padding: 16,
    paddingBottom: 32,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: "80%",
  },
  myMessage: {
    alignSelf: "flex-end",
  },
  theirMessage: {
    alignSelf: "flex-start",
  },
  bubble: {
    padding: 12,
    borderRadius: 20,
  },
  myBubble: {
    backgroundColor: "#0a7ea4",
    borderBottomRightRadius: 4,
  },
  theirBubble: {
    backgroundColor: "#f0f0f0",
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
  },
  myText: {
    color: "#fff",
  },
  theirText: {
    color: "#000",
  },
  savingsContainer: {
    marginTop: 4,
  },
  savingsText: {
    fontSize: 10,
    color: "#9ba1a6",
    textAlign: "right",
  },
  inputContainer: {
    flexDirection: "row",
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: "#e5e7eb",
    alignItems: "center",
    backgroundColor: "#fff",
  },
  attachButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#f0f0f0",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 8,
  },
  attachButtonText: {
    fontSize: 24,
    color: "#0a7ea4",
  },
  input: {
    flex: 1,
    backgroundColor: "#f5f5f5",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    marginLeft: 8,
    backgroundColor: "#0a7ea4",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    justifyContent: "center",
  },
  disabledButton: {
    backgroundColor: "#9ba1a6",
  },
  sendButtonText: {
    color: "#fff",
    fontWeight: "bold",
  },
  imagePlaceholder: {
    color: "#fff",
    fontStyle: "italic",
  },
  imageDescription: {
    color: "#fff",
    fontSize: 12,
    marginTop: 4,
  }
});

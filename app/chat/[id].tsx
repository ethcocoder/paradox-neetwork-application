import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
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
  DecodedMessage,
} from "@/lib/message-service";
import { doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase-auth";
import { COLLECTIONS } from "@/lib/firebase-config";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { Ionicons } from "@expo/vector-icons";
import Animated, { FadeIn, SlideInRight, SlideInLeft } from "react-native-reanimated";

export default function ChatScreen() {
  const { id: conversationId } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const colors = useColors();
  const [messages, setMessages] = useState<DecodedMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [otherUser, setOtherUser] = useState<any>(null);
  const flatListRef = useRef<FlatList>(null);
  const router = useRouter();

  useEffect(() => {
    if (!conversationId || !user) return;

    const fetchOtherUser = async () => {
      try {
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

    const unsubscribe = listenToMessages(conversationId, (newMessages) => {
      setMessages(newMessages);
      setLoading(false);
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
      await sendTextMessage(conversationId, user.uid, otherUser.uid || otherUser.id, text);
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const renderMessage = ({ item, index }: { item: DecodedMessage, index: number }) => {
    const isMe = item.senderId === user?.uid;

    return (
      <Animated.View
        entering={isMe ? SlideInRight : SlideInLeft}
        className={`mb-4 max-w-[85%] ${isMe ? 'self-end' : 'self-start'}`}
      >
        <View className={`p-4 rounded-[24px] ${isMe ? 'bg-primary rounded-tr-sm' : 'bg-surface rounded-tl-sm border border-border/50 shadow-sm'}`}>
          {item.messageType === "text" ? (
            <Text className={`text-base leading-6 ${isMe ? 'text-white font-medium' : 'text-foreground'}`}>
              {typeof item.decodedContent === "string" ? item.decodedContent : "Error decoding message"}
            </Text>
          ) : (
            <View className="items-center">
              <View className="bg-black/10 p-4 rounded-xl items-center w-full">
                <Ionicons name="image" size={32} color={isMe ? 'white' : colors.primary} />
                <Text className={`text-xs mt-2 ${isMe ? 'text-white' : 'text-muted'}`}>Neural Image Asset</Text>
              </View>
              <Text className={`text-xs mt-2 ${isMe ? 'text-white/80' : 'text-muted'}`}>
                {typeof item.decodedContent === 'object' ? (item.decodedContent as any).description : 'Paradox Image Encoding'}
              </Text>
            </View>
          )}
        </View>
        <View className={`mt-1 flex-row items-center ${isMe ? 'justify-end' : 'justify-start'}`}>
          <Ionicons name="flash-outline" size={10} color={colors.muted} />
          <Text className="text-[9px] font-mono text-muted ml-1 uppercase">
            SAVED {item.bandwidthSavingsPercent.toFixed(1)}% BANDWIDTH
          </Text>
        </View>
      </Animated.View>
    );
  };

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center bg-background">
        <ActivityIndicator size="large" color={colors.primary} />
        <Text className="mt-4 text-muted font-medium">Synchronizing Node...</Text>
      </View>
    );
  }

  return (
    <ScreenContainer className="flex-1">
      <Stack.Screen
        options={{
          headerShown: true,
          headerTitle: () => (
            <View className="flex-row items-center">
              <View className="w-8 h-8 rounded-lg bg-primary/20 items-center justify-center mr-2">
                <Text className="text-primary font-bold text-xs">
                  {(otherUser?.displayName || "U").charAt(0).toUpperCase()}
                </Text>
              </View>
              <View>
                <Text className="text-sm font-bold text-foreground">{otherUser?.displayName || "Paradox Node"}</Text>
                <View className="flex-row items-center">
                  <View className="w-1.5 h-1.5 rounded-full bg-success mr-1" />
                  <Text className="text-[10px] text-muted font-bold uppercase tracking-tighter">Encrypted Session</Text>
                </View>
              </View>
            </View>
          ),
          headerStyle: { backgroundColor: colors.background },
          headerShadowVisible: false,
          headerTintColor: colors.primary,
        }}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1"
        keyboardVerticalOffset={Platform.OS === "ios" ? 100 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id || Math.random().toString()}
          contentContainerStyle={{ padding: 20, paddingBottom: 40 }}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />

        <View className="px-4 pb-10 pt-2 bg-background/80 backdrop-blur-xl">
          <View className="flex-row items-end bg-surface border border-border/50 rounded-[28px] p-2 shadow-sm">
            <TouchableOpacity className="w-12 h-12 items-center justify-center rounded-full active:bg-primary/10">
              <Ionicons name="add" size={24} color={colors.primary} />
            </TouchableOpacity>

            <TextInput
              className="flex-1 min-h-[44px] max-h-[120px] px-3 pt-3 text-foreground text-[16px]"
              placeholder="Send neural message..."
              placeholderTextColor={colors.muted}
              value={inputText}
              onChangeText={setInputText}
              multiline
              blurOnSubmit={false}
            />

            <TouchableOpacity
              onPress={handleSend}
              disabled={!inputText.trim() || sending}
              className={`w-12 h-12 items-center justify-center rounded-full ${inputText.trim() ? 'bg-primary' : 'bg-muted/20'}`}
            >
              {sending ? (
                <ActivityIndicator color="white" size="small" />
              ) : (
                <Ionicons name="send" size={20} color="white" />
              )}
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}

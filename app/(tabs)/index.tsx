import { ScrollView, Text, View, TouchableOpacity, FlatList, RefreshControl } from "react-native";
import { useState, useEffect } from "react";
import { useRouter } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { useAuth } from "@/hooks/use-auth";
import { listenToUserConversations, Conversation } from "@/lib/conversation-service";
import { Ionicons } from "@expo/vector-icons";
import { useColors } from "@/hooks/use-colors";

export default function HomeScreen() {
  const router = useRouter();
  const colors = useColors();
  const { user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user?.uid) return;

    setLoading(true);
    const unsubscribe = listenToUserConversations(user.uid, (convos) => {
      setConversations(convos);
      setLoading(false);
    });

    return unsubscribe;
  }, [user?.uid]);

  const handleNewChat = () => {
    router.push("/new-chat");
  };

  const handleConversationPress = (conversation: Conversation) => {
    router.push({
      pathname: "/chat/[id]",
      params: { id: conversation.id },
    });
  };

  const renderConversationItem = ({ item }: { item: Conversation }) => {
    const otherParticipant = item.participants.find((id) => id !== user?.uid) || "Unknown";
    const displayName = otherParticipant.split("@")[0];

    return (
      <TouchableOpacity
        onPress={() => handleConversationPress(item)}
        className="bg-surface rounded-2xl p-4 mb-3 border border-border active:opacity-70"
      >
        <View className="flex-row items-center justify-between">
          <View className="flex-1">
            <Text className="text-lg font-semibold text-foreground">{displayName}</Text>
            {item.lastMessage && (
              <Text className="text-sm text-muted mt-1 line-clamp-1">{item.lastMessage}</Text>
            )}
            {item.lastMessageTime && (
              <Text className="text-xs text-muted mt-1">
                {new Date(item.lastMessageTime).toLocaleDateString()}
              </Text>
            )}
          </View>
          <Ionicons name="chevron-forward" size={24} color={colors.muted} />
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <ScreenContainer className="p-4">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-6">
        <View>
          <Text className="text-3xl font-bold text-foreground">Paradox</Text>
          <Text className="text-sm text-muted">Ultra-low bandwidth messaging</Text>
        </View>
        <TouchableOpacity
          onPress={handleNewChat}
          className="bg-primary rounded-full p-3 active:opacity-80"
        >
          <Ionicons name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      {/* Conversations List */}
      {conversations.length === 0 ? (
        <View className="flex-1 items-center justify-center gap-4">
          <Ionicons name="chatbubble-outline" size={64} color={colors.muted} />
          <Text className="text-lg font-semibold text-foreground">No conversations yet</Text>
          <Text className="text-sm text-muted text-center px-4">
            Start a new conversation to begin messaging with ultra-low bandwidth
          </Text>
          <TouchableOpacity
            onPress={handleNewChat}
            className="bg-primary px-6 py-3 rounded-full mt-4 active:opacity-80"
          >
            <Text className="text-background font-semibold">New Chat</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={conversations}
          renderItem={renderConversationItem}
          keyExtractor={(item) => item.id || ""}
          scrollEnabled={false}
          refreshControl={
            <RefreshControl refreshing={loading} onRefresh={() => setLoading(true)} />
          }
        />
      )}
    </ScreenContainer>
  );
}

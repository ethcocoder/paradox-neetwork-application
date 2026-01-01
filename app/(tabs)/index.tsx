import { ScrollView, Text, View, TouchableOpacity, FlatList, RefreshControl, TextInput, Image } from "react-native";
import { useState, useEffect, useMemo } from "react";
import { useRouter } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { useAuth } from "@/hooks/use-auth";
import { listenToUserConversations, Conversation } from "@/lib/conversation-service";
import { Ionicons } from "@expo/vector-icons";
import { useColors } from "@/hooks/use-colors";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";

export default function HomeScreen() {
  const router = useRouter();
  const colors = useColors();
  const { user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!user?.uid) return;

    setLoading(true);
    const unsubscribe = listenToUserConversations(user.uid, (convos) => {
      setConversations(convos);
      setLoading(false);
    });

    return unsubscribe;
  }, [user?.uid]);

  const filteredConversations = useMemo(() => {
    if (!search) return conversations;
    return conversations.filter(c =>
      c.participants.some(p => p.toLowerCase().includes(search.toLowerCase())) ||
      c.lastMessage?.toLowerCase().includes(search.toLowerCase())
    );
  }, [conversations, search]);

  const handleNewChat = () => {
    router.push("/new-chat");
  };

  const handleConversationPress = (conversation: Conversation) => {
    router.push({
      pathname: "/chat/[id]",
      params: { id: conversation.id },
    });
  };

  const renderConversationItem = ({ item, index }: { item: Conversation, index: number }) => {
    const otherParticipant = item.participants.find((id) => id !== user?.uid) || "Unknown";
    const displayName = otherParticipant.split("@")[0];
    const initial = displayName.charAt(0).toUpperCase();

    return (
      <Animated.View key={item.id} entering={FadeInDown.delay(index * 100)}>
        <TouchableOpacity
          onPress={() => handleConversationPress(item)}
          className="bg-surface rounded-3xl p-4 mb-3 border border-border/50 active:opacity-70 shadow-sm"
        >
          <View className="flex-row items-center">
            {/* Avatar */}
            <View className="w-14 h-14 rounded-2xl bg-primary/10 items-center justify-center mr-4 border border-primary/20">
              <Text className="text-xl font-bold text-primary">{initial}</Text>
            </View>

            <View className="flex-1">
              <View className="flex-row items-center justify-between">
                <Text className="text-base font-bold text-foreground">{displayName}</Text>
                {item.lastMessageTime && (
                  <Text className="text-xs text-muted">
                    {new Date(item.lastMessageTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </Text>
                )}
              </View>

              <View className="flex-row items-center justify-between mt-1">
                {item.lastMessage ? (
                  <Text className="text-sm text-muted line-clamp-1 flex-1 pr-4" numberOfLines={1}>
                    {item.lastMessage}
                  </Text>
                ) : (
                  <Text className="text-sm italic text-muted/60">No messages yet</Text>
                )}
                <View className="w-5 h-5 rounded-full bg-primary items-center justify-center">
                  <Ionicons name="chevron-forward" size={12} color="white" />
                </View>
              </View>
            </View>
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <ScreenContainer className="flex-1">
      <ScrollView
        className="flex-1 px-4 pt-4"
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={() => setLoading(true)} tintColor={colors.primary} />
        }
      >
        {/* Advanced Header */}
        <Animated.View entering={FadeInUp} className="flex-row items-center justify-between mb-8">
          <View>
            <Text className="text-sm font-medium text-primary uppercase tracking-widest">Network</Text>
            <Text className="text-4xl font-black text-foreground tracking-tight">Paradox</Text>
          </View>
          <TouchableOpacity
            onPress={() => router.push("/profile")}
            className="w-12 h-12 rounded-2xl bg-surface border border-border items-center justify-center shadow-sm"
          >
            <Ionicons name="person-outline" size={24} color={colors.foreground} />
          </TouchableOpacity>
        </Animated.View>

        {/* Global Search */}
        <View className="bg-surface border border-border/50 rounded-2xl px-4 py-3 flex-row items-center mb-8 shadow-sm">
          <Ionicons name="search-outline" size={20} color={colors.muted} />
          <TextInput
            placeholder="Search conversations..."
            placeholderTextColor={colors.muted}
            className="ml-3 flex-1 text-foreground text-base"
            value={search}
            onChangeText={setSearch}
          />
        </View>

        {/* Quick Actions */}
        <View className="flex-row items-center justify-between mb-6">
          <Text className="text-lg font-bold text-foreground">Recent Chats</Text>
          <TouchableOpacity
            onPress={handleNewChat}
            className="flex-row items-center bg-primary/10 px-4 py-2 rounded-xl"
          >
            <Ionicons name="add" size={18} color={colors.primary} />
            <Text className="text-primary font-bold ml-1">New</Text>
          </TouchableOpacity>
        </View>

        {/* Conversations List */}
        {filteredConversations.length === 0 ? (
          <View className="py-20 items-center justify-center">
            <View className="w-24 h-24 rounded-full bg-surface items-center justify-center mb-4 border border-border">
              <Ionicons name="chatbubbles-outline" size={40} color={colors.muted} />
            </View>
            <Text className="text-xl font-bold text-foreground">Quiet in here...</Text>
            <Text className="text-sm text-muted text-center mt-2 px-10">
              Start a highly encrypted, ultra-low bandwidth conversation.
            </Text>
          </View>
        ) : (
          <View className="pb-10">
            {filteredConversations.map((item, index) => renderConversationItem({ item, index }))}
          </View>
        )}
      </ScrollView>
    </ScreenContainer>
  );
}

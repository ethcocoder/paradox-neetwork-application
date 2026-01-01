import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter, Stack } from "expo-router";
import { useAuth } from "@/hooks/use-auth";
import { collection, query, getDocs, where } from "firebase/firestore";
import { db } from "@/lib/firebase-auth";
import { COLLECTIONS } from "@/lib/firebase-config";
import { createConversation } from "@/lib/conversation-service";
import { Ionicons } from "@expo/vector-icons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";

export default function NewChatScreen() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const { user: currentUser } = useAuth();
  const router = useRouter();
  const colors = useColors();

  useEffect(() => {
    const fetchUsers = async () => {
      if (!currentUser) return;
      try {
        const q = query(
          collection(db, COLLECTIONS.USERS),
          where("uid", "!=", currentUser.uid)
        );
        const querySnapshot = await getDocs(q);
        const userList = querySnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));
        setUsers(userList);
      } catch (error) {
        console.error("Error fetching users:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [currentUser]);

  const handleStartChat = async (otherUser: any) => {
    if (!currentUser) return;
    try {
      const conversation = await createConversation(currentUser.uid, otherUser.uid);
      router.replace({
        pathname: "/chat/[id]",
        params: { id: conversation.id },
      });
    } catch (error) {
      Alert.alert("Error", "Failed to start conversation");
    }
  };

  const filteredUsers = users.filter((u) =>
    u.displayName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderUserItem = ({ item, index }: { item: any, index: number }) => {
    const displayName = item.displayName || "Unknown Node";
    const initial = displayName.charAt(0).toUpperCase();

    return (
      <Animated.View entering={FadeInDown.delay(index * 50)}>
        <TouchableOpacity
          onPress={() => handleStartChat(item)}
          className="flex-row items-center bg-surface p-4 mb-3 rounded-3xl border border-border/50 active:opacity-70 shadow-sm"
        >
          <View className="w-12 h-12 rounded-2xl bg-primary/10 items-center justify-center mr-4 border border-primary/20">
            <Text className="text-lg font-bold text-primary">{initial}</Text>
          </View>
          <View className="flex-1">
            <Text className="text-base font-bold text-foreground">{displayName}</Text>
            <Text className="text-xs text-muted font-medium">{item.email}</Text>
          </View>
          <View className="w-8 h-8 rounded-full bg-primary/5 items-center justify-center">
            <Ionicons name="add" size={18} color={colors.primary} />
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <ScreenContainer className="flex-1">
      <Stack.Screen
        options={{
          title: "New Transmission",
          headerShown: true,
          headerStyle: { backgroundColor: colors.background },
          headerShadowVisible: false,
          headerTintColor: colors.primary,
          headerTitleStyle: { fontWeight: '900' }
        }}
      />

      <View className="px-4 pt-4 flex-1">
        {/* Advanced Search */}
        <Animated.View entering={FadeInUp} className="bg-surface border border-border/50 rounded-2xl px-4 py-3 flex-row items-center mb-6 shadow-sm">
          <Ionicons name="search-outline" size={20} color={colors.muted} />
          <TextInput
            placeholder="Search network nodes..."
            placeholderTextColor={colors.muted}
            className="ml-3 flex-1 text-foreground text-base"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </Animated.View>

        <Text className="text-xs font-bold text-muted uppercase tracking-widest mb-4 ml-2">Available Nodes</Text>

        {loading ? (
          <View className="flex-1 items-center justify-center">
            <ActivityIndicator size="large" color={colors.primary} />
            <Text className="mt-4 text-muted font-medium">Scanning Network...</Text>
          </View>
        ) : (
          <FlatList
            data={filteredUsers}
            renderItem={renderUserItem}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: 40 }}
            ListEmptyComponent={
              <View className="py-20 items-center justify-center">
                <Ionicons name="planet-outline" size={64} color={colors.muted} className="opacity-20" />
                <Text className="text-muted font-bold mt-4">Node Disconnected</Text>
              </View>
            }
          />
        )}
      </View>
    </ScreenContainer>
  );
}

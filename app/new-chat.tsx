import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
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

export default function NewChatScreen() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const { user: currentUser } = useAuth();
  const router = useRouter();

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

  const renderUserItem = ({ item }: { item: any }) => (
    <TouchableOpacity
      style={styles.userItem}
      onPress={() => handleStartChat(item)}
    >
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>
          {item.displayName?.charAt(0).toUpperCase() || "?"}
        </Text>
      </View>
      <View style={styles.userInfo}>
        <Text style={styles.userName}>{item.displayName || "Unknown User"}</Text>
        <Text style={styles.userEmail}>{item.email}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#9ba1a6" />
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: "New Chat", headerBackTitle: "Back" }} />
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9ba1a6" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search users..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0a7ea4" />
        </View>
      ) : (
        <FlatList
          data={filteredUsers}
          renderItem={renderUserItem}
          keyExtractor={(item) => item.id}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No users found</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
    margin: 16,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  userItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: "#0a7ea4",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 16,
  },
  avatarText: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#11181c",
  },
  userEmail: {
    fontSize: 14,
    color: "#687076",
  },
  emptyContainer: {
    padding: 32,
    alignItems: "center",
  },
  emptyText: {
    color: "#9ba1a6",
    fontSize: 16,
  },
});

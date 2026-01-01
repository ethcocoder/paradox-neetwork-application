import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Alert,
  ScrollView,
} from "react-native";
import { useRouter, Stack } from "expo-router";
import { useAuth } from "@/hooks/use-auth";
import { Ionicons } from "@expo/vector-icons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const colors = useColors();

  const handleLogout = () => {
    Alert.alert(
      "Logout",
      "Are you sure you want to logout of Paradox?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Logout",
          style: "destructive",
          onPress: async () => {
            try {
              await logout();
              router.replace("/(auth)/login");
            } catch (error) {
              Alert.alert("Error", "Failed to logout");
            }
          },
        },
      ]
    );
  };

  if (!user) return null;

  return (
    <ScreenContainer className="flex-1">
      <ScrollView className="flex-1 px-4 pt-4" showsVerticalScrollIndicator={false}>
        <Stack.Screen options={{ title: "Identity", headerShown: false }} />

        {/* Profile Header */}
        <Animated.View entering={FadeInUp} className="items-center py-10">
          <View className="w-28 h-28 rounded-3xl bg-primary items-center justify-center shadow-xl shadow-primary/40 border-4 border-surface">
            <Text className="text-white text-4xl font-black">
              {user.displayName?.charAt(0).toUpperCase() || "?"}
            </Text>
          </View>
          <Text className="text-2xl font-black text-foreground mt-6 tracking-tight">{user.displayName || "Paradox User"}</Text>
          <Text className="text-muted text-base mt-1 font-medium">{user.email}</Text>

          <TouchableOpacity className="mt-6 bg-surface border border-border px-6 py-2 rounded-2xl shadow-sm active:opacity-70">
            <Text className="text-foreground font-bold">Edit Profile</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* Info Grid */}
        <Animated.View entering={FadeInDown.delay(200)} className="bg-surface rounded-3xl p-6 border border-border/50 mb-6 shadow-sm">
          <Text className="text-xs font-bold text-muted uppercase tracking-widest mb-4">Security Protocol</Text>

          <View className="flex-row items-center justify-between py-3 border-b border-border/10">
            <View className="flex-row items-center">
              <View className="w-10 h-10 rounded-xl bg-success/10 items-center justify-center mr-3">
                <Ionicons name="shield-checkmark" size={20} color={colors.success} />
              </View>
              <Text className="text-base font-semibold text-foreground">Encryption</Text>
            </View>
            <Text className="text-success font-bold">AES-256 Active</Text>
          </View>

          <View className="flex-row items-center justify-between py-3">
            <View className="flex-row items-center">
              <View className="w-10 h-10 rounded-xl bg-primary/10 items-center justify-center mr-3">
                <Ionicons name="finger-print" size={20} color={colors.primary} />
              </View>
              <Text className="text-base font-semibold text-foreground">Biometrics</Text>
            </View>
            <TouchableOpacity className="bg-primary/20 px-3 py-1 rounded-lg">
              <Text className="text-primary font-bold text-xs">Enable</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Menu Section */}
        <Animated.View entering={FadeInDown.delay(400)} className="mb-10">
          <Text className="text-xs font-bold text-muted uppercase tracking-widest mb-4 ml-2">Preferences</Text>

          <TouchableOpacity className="bg-surface rounded-3xl flex-row items-center p-4 border border-border/50 mb-3 shadow-sm">
            <Ionicons name="notifications-outline" size={24} color={colors.primary} className="mr-4" />
            <Text className="text-base font-semibold text-foreground flex-1 ml-4">Notifications</Text>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </TouchableOpacity>

          <TouchableOpacity className="bg-surface rounded-3xl flex-row items-center p-4 border border-border/50 mb-3 shadow-sm">
            <Ionicons name="color-palette-outline" size={24} color={colors.accent} className="mr-4" />
            <Text className="text-base font-semibold text-foreground flex-1 ml-4">Appearance</Text>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </TouchableOpacity>

          <TouchableOpacity className="bg-surface rounded-3xl flex-row items-center p-4 border border-border/50 mb-3 shadow-sm">
            <Ionicons name="help-buoy-outline" size={24} color={colors.success} className="mr-4" />
            <Text className="text-base font-semibold text-foreground flex-1 ml-4">Support</Text>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleLogout}
            className="bg-error/10 rounded-3xl flex-row items-center p-4 border border-error/20 mt-4 active:bg-error/20"
          >
            <Ionicons name="log-out-outline" size={24} color={colors.error} className="mr-4" />
            <Text className="text-base font-bold text-error flex-1 ml-4 text-center">Terminate Session</Text>
          </TouchableOpacity>
        </Animated.View>

        <View className="items-center pb-20">
          <Text className="text-muted text-xs font-medium">Paradox Network v1.0.0 (Master)</Text>
          <Text className="text-muted/40 text-[10px] mt-1 font-mono">NODE-ID: {user.uid.substring(0, 12)}</Text>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

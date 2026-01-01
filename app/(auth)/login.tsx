import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import { signIn, signUp } from "@/lib/firebase-auth";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { Ionicons } from "@expo/vector-icons";
import Animated, { FadeIn, FadeInDown, FadeInUp } from "react-native-reanimated";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const colors = useColors();

  const handleAuth = async () => {
    if (!email || !password || (isSignUp && !displayName)) {
      Alert.alert("Error", "Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      if (isSignUp) {
        await signUp(email, password, displayName);
      } else {
        await signIn(email, password);
      }
      router.replace("/(tabs)");
    } catch (error: any) {
      Alert.alert("Authentication Error", error.message || "Failed to authenticate");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenContainer className="flex-1">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1"
      >
        <ScrollView contentContainerStyle={{ flexGrow: 1 }} showsVerticalScrollIndicator={false}>
          <View className="flex-1 justify-center px-8 py-10">
            {/* Logo Section */}
            <Animated.View entering={FadeInUp} className="items-center mb-12">
              <View className="w-20 h-20 bg-primary rounded-[30px] items-center justify-center shadow-2xl shadow-primary/40 rotate-3">
                <Ionicons name="flash" size={40} color="white" />
              </View>
              <Text className="text-4xl font-black text-foreground mt-6 tracking-tighter">PARADOX</Text>
              <Text className="text-muted font-medium tracking-widest uppercase text-[10px] mt-1">Advanced Neural Network</Text>
            </Animated.View>

            {/* Title & Subtitle */}
            <Animated.View entering={FadeInDown.delay(200)}>
              <Text className="text-3xl font-bold text-foreground mb-2">
                {isSignUp ? "Enlist Now" : "Welcome Back"}
              </Text>
              <Text className="text-muted text-base mb-8 font-medium">
                {isSignUp ? "Join the high-speed communication node." : "Secure authentication required."}
              </Text>
            </Animated.View>

            {/* Form */}
            <Animated.View entering={FadeInDown.delay(400)} className="gap-y-4">
              {isSignUp && (
                <View className="bg-surface border border-border/50 rounded-2xl px-4 py-3 flex-row items-center shadow-sm">
                  <Ionicons name="person-outline" size={20} color={colors.muted} />
                  <TextInput
                    placeholder="Display Name"
                    placeholderTextColor={colors.muted}
                    className="ml-3 flex-1 text-foreground text-base"
                    value={displayName}
                    onChangeText={setDisplayName}
                    autoCapitalize="words"
                  />
                </View>
              )}

              <View className="bg-surface border border-border/50 rounded-2xl px-4 py-3 flex-row items-center shadow-sm">
                <Ionicons name="mail-outline" size={20} color={colors.muted} />
                <TextInput
                  placeholder="Email Protocol"
                  placeholderTextColor={colors.muted}
                  className="ml-3 flex-1 text-foreground text-base"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>

              <View className="bg-surface border border-border/50 rounded-2xl px-4 py-3 flex-row items-center shadow-sm">
                <Ionicons name="lock-closed-outline" size={20} color={colors.muted} />
                <TextInput
                  placeholder="Access Key"
                  placeholderTextColor={colors.muted}
                  className="ml-3 flex-1 text-foreground text-base"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                />
              </View>

              <TouchableOpacity
                onPress={handleAuth}
                disabled={loading}
                className="bg-primary rounded-2xl py-4 items-center justify-center shadow-xl shadow-primary/30 mt-4 active:opacity-90"
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text className="text-white text-lg font-bold tracking-tight">
                    {isSignUp ? "INITIALIZE ACCOUNT" : "AUTHENTICATE"}
                  </Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => setIsSignUp(!isSignUp)}
                className="mt-6 items-center"
              >
                <Text className="text-muted font-medium">
                  {isSignUp
                    ? "Existing terminal session? "
                    : "No access credentials yet? "}
                  <Text className="text-primary font-bold">{isSignUp ? "Sign In" : "Sign Up"}</Text>
                </Text>
              </TouchableOpacity>
            </Animated.View>

            {/* Footer decoration */}
            <Animated.View entering={FadeIn.delay(800)} className="mt-auto pt-10 items-center">
              <Text className="text-muted/30 text-[10px] font-mono uppercase">Node Protocol 7.2 | Encrypted End-to-End</Text>
            </Animated.View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}

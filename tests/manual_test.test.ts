
import { describe, it, expect, vi, beforeAll } from 'vitest';

// Mock Platform for Node environment before importing other modules
vi.mock("react-native", () => ({
  Platform: {
    OS: "web",
  },
}));

// Mock firebase modules since we are in a headless environment and might not have full browser env
// However, the user wants to test the "chat creation work", which implies real interaction or a very good mock.
// Given the user's request, I should try to run the real code if possible, but Firebase often requires a browser or specific setup.
// Let's see if we can use the actual firebase JS SDK in this environment.

import { signUp, signIn, signOutUser } from "../lib/firebase-auth";
import { createConversation, getUserConversations } from "../lib/conversation-service";

describe('Paradox App Functionality', () => {
  const testEmail = `test_${Date.now()}@example.com`;
  const testPassword = "password123";
  const testDisplayName = "Test User";
  let userId: string;

  it('should sign up a new user', async () => {
    console.log("Testing Sign Up...");
    const userProfile = await signUp(testEmail, testPassword, testDisplayName);
    expect(userProfile).toBeDefined();
    expect(userProfile.uid).toBeDefined();
    userId = userProfile.uid;
    console.log("Sign Up Successful:", userId);
  }, 20000);

  it('should sign in the user', async () => {
    console.log("Testing Sign In...");
    const signedInUser = await signIn(testEmail, testPassword);
    expect(signedInUser.uid).toBe(userId);
    console.log("Sign In Successful:", signedInUser.uid);
  }, 20000);

  it('should create a conversation', async () => {
    console.log("Testing Chat Creation...");
    const conversation = await createConversation(userId, "dummy_user_id_for_test");
    expect(conversation).toBeDefined();
    expect(conversation.id).toBeDefined();
    console.log("Chat Creation Successful:", conversation.id);
  }, 20000);

  it('should get user conversations', async () => {
    console.log("Testing Get Conversations...");
    const conversations = await getUserConversations(userId);
    expect(conversations.length).toBeGreaterThan(0);
    console.log("Found Conversations:", conversations.length);
  }, 20000);

  it('should sign out', async () => {
    console.log("Testing Sign Out...");
    await signOutUser();
    console.log("Sign Out Successful");
  }, 20000);
});

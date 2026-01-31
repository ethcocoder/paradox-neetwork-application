import { Platform } from "react-native";

// Types for consistency
export interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  createdAt: Date;
  avatar?: string;
}

// We'll export these variables which will be initialized based on the platform
let auth: any;
let db: any;
let firebaseAuth: any; // The module itself for auth methods
let firebaseFirestore: any; // The module itself for firestore methods

// Platform-specific initialization
if (Platform.OS === "web") {
  // Web: Use JS SDK
  const { initializeApp, getApp, getApps } = require("firebase/app");
  const { getAuth, initializeAuth, browserLocalPersistence } = require("firebase/auth");
  const { getFirestore } = require("firebase/firestore");
  const { firebaseConfig } = require("./firebase-config");

  const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
  auth = getAuth(app);
  db = getFirestore(app);

  // Auth methods from JS SDK
  firebaseAuth = require("firebase/auth");
  firebaseFirestore = require("firebase/firestore");
} else {
  // Mobile: Use Native SDK (@react-native-firebase)
  const nativeAuth = require("@react-native-firebase/auth").default;
  const nativeFirestore = require("@react-native-firebase/firestore").default;

  auth = nativeAuth();
  db = nativeFirestore();

  // Auth methods from Native SDK
  firebaseAuth = require("@react-native-firebase/auth").default;
  firebaseFirestore = require("@react-native-firebase/firestore").default;
}

export { auth, db };

/**
 * Sign up a new user with email and password
 */
export async function signUp(
  email: string,
  password: string,
  displayName: string
): Promise<UserProfile> {
  try {
    let user;
    if (Platform.OS === "web") {
      const { createUserWithEmailAndPassword } = firebaseAuth;
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      user = userCredential.user;
    } else {
      const userCredential = await auth.createUserWithEmailAndPassword(email, password);
      user = userCredential.user;
    }

    // Create user profile in Firestore
    const userProfile: UserProfile = {
      uid: user.uid,
      email: user.email || "",
      displayName,
      createdAt: new Date(),
    };

    if (Platform.OS === "web") {
      const { doc, setDoc } = firebaseFirestore;
      await setDoc(doc(db, "users", user.uid), userProfile);
    } else {
      await db.collection("users").doc(user.uid).set(userProfile);
    }

    return userProfile;
  } catch (error) {
    console.error("Sign up error:", error);
    throw error;
  }
}

/**
 * Sign in with email and password
 */
export async function signIn(
  email: string,
  password: string
): Promise<UserProfile> {
  try {
    let user;
    if (Platform.OS === "web") {
      const { signInWithEmailAndPassword } = firebaseAuth;
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      user = userCredential.user;
    } else {
      const userCredential = await auth.signInWithEmailAndPassword(email, password);
      user = userCredential.user;
    }

    // Fetch user profile from Firestore
    let data;
    if (Platform.OS === "web") {
      const { doc, getDoc } = firebaseFirestore;
      const userDocSnap = await getDoc(doc(db, "users", user.uid));
      if (userDocSnap.exists()) {
        data = userDocSnap.data();
      }
    } else {
      const userDocSnap = await db.collection("users").doc(user.uid).get();
      if (userDocSnap.exists) {
        data = userDocSnap.data();
      }
    }

    if (data) {
      return data as UserProfile;
    } else {
      throw new Error("User profile not found");
    }
  } catch (error) {
    console.error("Sign in error:", error);
    throw error;
  }
}

/**
 * Sign out the current user
 */
export async function signOutUser(): Promise<void> {
  try {
    if (Platform.OS === "web") {
      const { signOut } = firebaseAuth;
      await signOut(auth);
    } else {
      await auth.signOut();
    }
  } catch (error) {
    console.error("Sign out error:", error);
    throw error;
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUserProfile(): Promise<UserProfile | null> {
  const user = auth.currentUser;
  if (!user) return null;

  try {
    let data;
    if (Platform.OS === "web") {
      const { doc, getDoc } = firebaseFirestore;
      const userDocSnap = await getDoc(doc(db, "users", user.uid));
      if (userDocSnap.exists()) {
        data = userDocSnap.data();
      }
    } else {
      const userDocSnap = await db.collection("users").doc(user.uid).get();
      if (userDocSnap.exists) {
        data = userDocSnap.data();
      }
    }

    if (data) return data as UserProfile;
  } catch (error) {
    console.error("Error fetching user profile:", error);
  }

  return null;
}

/**
 * Listen to authentication state changes
 */
export function onAuthStateChange(
  callback: (user: any | null) => void
): () => void {
  if (Platform.OS === "web") {
    const { onAuthStateChanged } = firebaseAuth;
    return onAuthStateChanged(auth, callback);
  } else {
    return auth.onAuthStateChanged(callback);
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return auth.currentUser !== null;
}

/**
 * Get current user ID
 */
export function getCurrentUserId(): string | null {
  return auth.currentUser?.uid || null;
}

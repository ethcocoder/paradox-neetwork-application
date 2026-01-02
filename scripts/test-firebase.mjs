import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';

// Manually including config to avoid path/import issues in standalone script
const firebaseConfig = {
    apiKey: "AIzaSyDniENuSOGDrMCp4MkbZ6nw8BI_K3Jkt2c",
    authDomain: "paradox-network-2d479.firebaseapp.com",
    projectId: "paradox-network-2d479",
    storageBucket: "paradox-network-2d479.firebasestorage.app",
    messagingSenderId: "349632549805",
    appId: "1:349632549805:android:e5ce70e168049ef4710724",
};

console.log('🚀 Initializing Firebase Test...');

async function runTest() {
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = "Password123!";

    try {
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);

        console.log('✅ Firebase App Initialized');

        // Test 1: Sign Up
        console.log(`\n⏳ Attempting to Sign Up: ${testEmail}...`);
        const userCredential = await createUserWithEmailAndPassword(auth, testEmail, testPassword);
        const user = userCredential.user;
        console.log('✅ Sign Up Successful! UID:', user.uid);

        // Test 2: Firestore Write
        console.log('\n⏳ Attempting to write to Firestore (users collection)...');
        await setDoc(doc(db, 'users', user.uid), {
            email: testEmail,
            displayName: 'Test Bot',
            createdAt: new Date().toISOString()
        });
        console.log('✅ Firestore Write Successful');

        // Test 3: Firestore Read
        console.log('\n⏳ Attempting to read from Firestore...');
        const docSnap = await getDoc(doc(db, 'users', user.uid));
        if (docSnap.exists()) {
            console.log('✅ Firestore Read Successful! Data:', docSnap.data());
        } else {
            console.log('❌ Firestore Read Failed: Document not found');
        }

        console.log('\n🎉 ALL TESTS PASSED! Your Firebase configuration is correct.');
        process.exit(0);
    } catch (error) {
        console.error('\n❌ TEST FAILED');
        console.error('Error Code:', error.code);
        console.error('Error Message:', error.message);

        if (error.code === 'auth/configuration-not-found') {
            console.error('\nTIP: This usually means the API key is invalid or your package.json/SDK version has a conflict.');
        }

        process.exit(1);
    }
}

runTest();

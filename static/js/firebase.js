import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    signOut
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

// ==========================================
// Firebase Config
// ==========================================

// Replace these values with your Firebase project values
// Do NOT commit real secrets if you don't want them on GitHub.

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCm8FFxomYy0E_K6ZhW38iZWIbnvr0xPqo",
  authDomain: "ai-nano-counter-87b7c.firebaseapp.com",
  databaseURL: "https://ai-nano-counter-87b7c-default-rtdb.firebaseio.com",
  projectId: "ai-nano-counter-87b7c",
  storageBucket: "ai-nano-counter-87b7c.firebasestorage.app",
  messagingSenderId: "552178964022",
  appId: "1:552178964022:web:220b8c24e619fd7eebaa97",
  measurementId: "G-D14DY41KWL"
};

// ==========================================
// Initialize Firebase
// ==========================================

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

const provider = new GoogleAuthProvider();

provider.setCustomParameters({
    prompt: "select_account"
});

// ==========================================
// Google Login
// ==========================================

window.googleLogin = async function () {

    try {

        const result = await signInWithPopup(auth, provider);

        const idToken = await result.user.getIdToken();

        const response = await fetch("/verify_token", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                idToken: idToken
            })

        });

        const data = await response.json();

        if (data.success) {

            window.location.href = data.redirect;

        } else {

            alert(data.message);

        }

    } catch (error) {

        console.error(error);

        alert(error.message);

    }

};

// ==========================================
// Logout
// ==========================================

window.logout = async function () {

    try {

        await signOut(auth);

    } catch (e) {

        console.log(e);

    }

    window.location.href = "/logout";

};
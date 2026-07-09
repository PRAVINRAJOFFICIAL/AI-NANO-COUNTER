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

const firebaseConfig = {

    apiKey: "",

    authDomain: "",

    projectId: "",

    storageBucket: "",

    messagingSenderId: "",

    appId: ""

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
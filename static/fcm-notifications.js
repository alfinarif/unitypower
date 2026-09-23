// 2. Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBM4LBoYge8cYXsApqlENCcmlQPgfTXDus",
  authDomain: "unitypoweradmin.firebaseapp.com",
  projectId: "unitypoweradmin",
  storageBucket: "unitypoweradmin.firebasestorage.app",
  messagingSenderId: "971726673464",
  appId: "1:971726673464:web:af98af9c0b85d04b6ef8cd",
  measurementId: "G-FG4MGHTBJ9"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// 3. Register the local Service Worker explicitly if it's in a custom directory
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js')
    .then((registration) => {
        console.log('Service Worker registered with scope:', registration.scope);
    }).catch((err) => {
        console.error('Service Worker registration failed:', err);
    });
}

// 4. Request permission and fetch the token
function requestNotificationPermission() {
    Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
            // Fetch the token using the VAPID key
            messaging.getToken({ vapidKey: 'BFlTAkDwdI1Eb7VkO4XrYjyJ1bBKca8kCprMI6sQz7_p-A2eEKeCClJlmw-ZdhnySA-Ro8bRaZ7iugs3MPglVCY' })
            .then((currentToken) => {
                if (currentToken) {
                    console.log("Token generated: ", currentToken);
                    sendTokenToBackend(currentToken);
                } else {
                    console.log('No registration token available.');
                }
            }).catch((err) => {
                console.log('An error occurred while retrieving token. ', err);
            });
        }
    });
}

function sendTokenToBackend(token) {
    fetch('/api/save-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Built-in Django template tag
        },
        body: JSON.stringify({ token: token })
    });
}

console.log('FCM File called successfully.....!')
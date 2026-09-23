importScripts('https://gstatic.com');
importScripts('https://gstatic.com');

firebase.initializeApp({
  apiKey: "AIzaSyBM4LBoYge8cYXsApqlENCcmlQPgfTXDus",
  authDomain: "unitypoweradmin.firebaseapp.com",
  projectId: "unitypoweradmin",
  storageBucket: "unitypoweradmin.firebasestorage.app",
  messagingSenderId: "971726673464",
  appId: "1:971726673464:web:af98af9c0b85d04b6ef8cd"
});

const messaging = firebase.messaging();

// Handles background events when web page is closed
messaging.onBackgroundMessage((payload) => {
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/images/icon.png'
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});

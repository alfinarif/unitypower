import { onMessage } from "https://gstatic.com";

// Add this to listen for alerts when the web page is open
onMessage(messaging, (payload) => {
  console.log('Foreground message received: ', payload);
  
  // Example: Display a simple web browser alert box
  alert(`${payload.notification.title}\n\n${payload.notification.body}`);
  
  // Alternatively, you can trigger a custom Bootstrap toast or custom UI banner here!
});

// // Function to toggle chatbot visibility
// function toggleChat() {
//     var chatbox = document.getElementById("chatbox");
//     if (chatbox.style.display === "block") {
//         chatbox.style.display = "none";
//     } else {
//         chatbox.style.display = "block";
//     }
// }


function toggleChat() {
    let chatbox = document.getElementById("chatbox");
    chatbox.style.display = chatbox.style.display === "flex" ? "none" : "flex";
}

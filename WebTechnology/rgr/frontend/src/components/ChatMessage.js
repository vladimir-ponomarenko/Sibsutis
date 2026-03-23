import React from "react";
import "../ChatMessage.css";

const ChatMessage = ({ author, text, likes = 0, active = false }) => {
  return (
    <div
      className={`chat-message ${
        author === "Вы" ? "own-message" : "other-message"
      }`}
    >
      <div className="chat-message-left">
        <span className="chat-message-author">{author}</span>
        <span className="chat-message-body">{text}</span>
      </div>
      <span className={`chat-message-likes ${active ? "likes-active" : ""}`}>
        ❤ {likes}
      </span>
    </div>
  );
};

export default ChatMessage;

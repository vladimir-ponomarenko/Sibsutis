import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import ChatMessage from "./ChatMessage";
import "../VideoPlayer.css";

const VideoPlayer = () => {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [chatName, setChatName] = useState("Владимир");
  const [isEditingName, setIsEditingName] = useState(false);
  const [draftName, setDraftName] = useState("Владимир");
  const [showComposer, setShowComposer] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/videos/${id}/`
        );
        setVideo(response.data);
      } catch (error) {
        console.error("Failed to fetch video", error);
      }
    };

    fetchVideo();

    const demoMessages = [
      { author: "Женя", text: "Всем привет", likes: 1567 },
      { author: "Женя", text: "Всем привет", likes: 567 },
      { author: "Женя", text: "Всем привет", likes: 67 },
      { author: "Женя", text: "Всем привет", likes: 7 },
      { author: "Женя", text: "Всем привет", likes: 7651 },
      { author: "Женя", text: "Всем привет", likes: 651 },
      { author: "Женя", text: "Всем привет", likes: 51 },
      { author: "Женя", text: "Всем привет", likes: 1 },
      { author: "Женя", text: "Всем привет", likes: 0 },
      { author: "Модератор", text: "Проверка связи", likes: 0 },
    ];
    setMessages(demoMessages);
  }, [id]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() === "") return;

    const message = {
      author: chatName || "Вы",
      text: newMessage.trim(),
      likes: 0,
    };

    setMessages([...messages, message]);
    setNewMessage("");
  };

  if (!video) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="video-page-container">
      <div className="video-container">
        <div className="video-wrapper">
          <video controls className="video-player">
            <source src={video.video_file} type="video/mp4" />
            Ваш браузер не поддерживает тег video.
          </video>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-tabs">
          <div className="chat-tab active">Чат</div>
          <div className="chat-tab">Вопрос / ответ</div>
        </div>
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <ChatMessage
              key={index}
              author={msg.author}
              text={msg.text}
              likes={msg.likes}
              active={msg.active}
            />
          ))}
          <div ref={chatEndRef} />
        </div>
        {!showComposer ? (
          <button
            className="chat-cta-button"
            type="button"
            onClick={() => setShowComposer(true)}
          >
            Хотите отправить сообщение?
            <br />
            Кликните на эту кнопку
          </button>
        ) : (
          <>
            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Текст"
                className="chat-input"
              />
              <button type="submit" className="send-button">
                Отправить
              </button>
            </form>
            <div className="chat-name-row">
              <span className="chat-name-label">Имя в чате:</span>
              {isEditingName ? (
                <input
                  className="chat-name-input"
                  value={draftName}
                  onChange={(e) => setDraftName(e.target.value)}
                  onBlur={() => {
                    const clean = draftName.trim() || "Владимир";
                    setChatName(clean);
                    setDraftName(clean);
                    setIsEditingName(false);
                  }}
                />
              ) : (
                <span className="chat-name-value">{chatName}</span>
              )}
              <button
                type="button"
                className="chat-name-edit"
                onClick={() => setIsEditingName(true)}
              >
                Ред.
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VideoPlayer;

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchVideos, streamUrl } from "../api.js";

const imgYadroPattern = "https://www.figma.com/api/mcp/asset/68f34f7c-96ce-49bf-bc96-83f1c2a226a6";
const imgLogo = "https://www.figma.com/api/mcp/asset/85055626-e7ee-455b-a5a6-470258ee3c87";
const imgPlayerMask = "https://www.figma.com/api/mcp/asset/e4aa2568-f587-4b0e-92bb-826045f07be9";
const imgPlayer = "https://www.figma.com/api/mcp/asset/eebf5637-a345-454c-a60c-ed93a2a1fad0";
const imgUserCircle = "https://www.figma.com/api/mcp/asset/2098ff98-d10a-4563-9b2c-24b825c44135";
const imgUserCircleInner = "https://www.figma.com/api/mcp/asset/9a22a001-3d48-4aff-aaff-d8f953ed4808";
const imgUserCircleFace = "https://www.figma.com/api/mcp/asset/4378998f-2e58-407c-9e85-d7eac144a256";
const imgUserCircleBody = "https://www.figma.com/api/mcp/asset/8bdfd9d7-b125-4200-bf19-7ff2a268ccc7";
const imgLike = "https://www.figma.com/api/mcp/asset/d4231aba-3fd9-411e-a9c8-18d6722b0912";
const imgLikeActive = "https://www.figma.com/api/mcp/asset/47f09b67-5b7c-4885-88aa-457807aa45ff";

function UserCircle() {
  return (
    <div className="user-circle">
      <img className="user-circle-layer" src={imgUserCircle} alt="" />
      <img className="user-circle-layer" src={imgUserCircleInner} alt="" />
      <img className="user-circle-layer" src={imgUserCircleFace} alt="" />
      <img className="user-circle-layer" src={imgUserCircleBody} alt="" />
    </div>
  );
}

const messages = [
  { id: 1, name: "Женя", text: "Всем привет", likes: 567, active: false },
  { id: 2, name: "Женя", text: "Всем привет", likes: 11, active: false },
  { id: 3, name: "Женя", text: "Всем привет", likes: 0, active: false },
  { id: 4, name: "Женя", text: "Всем привет", likes: 15, active: true },
  { id: 5, name: "Женя", text: "Всем привет", likes: 42, active: false },
  { id: 6, name: "Женя", text: "Всем привет", likes: 0, active: false },
];

function Translation() {
  const [videos, setVideos] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    let active = true;
    fetchVideos()
      .then((data) => {
        if (active) {
          setVideos(data);
        }
      })
      .catch(() => {
        if (active) {
          setVideos([]);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const currentVideo = useMemo(() => {
    if (videos.length === 0) return null;
    return videos[currentIndex % videos.length];
  }, [videos, currentIndex]);

  const handleNextVideo = () => {
    if (videos.length > 1) {
      setCurrentIndex((prev) => (prev + 1) % videos.length);
    }
  };

  return (
    <section className="page-translation">
      <div className="pattern-bg" style={{ backgroundImage: `url(${imgYadroPattern})` }} />
      <header className="top-bar">
        <img className="logo" src={imgLogo} alt="Logo" />
        <div className="top-actions">
          <Link to="/register">Регистрация</Link>
          <UserCircle />
        </div>
      </header>
      <div className="player-layout">
        <div className="player-panel" onClick={handleNextVideo}>
          <div className="player-mask" style={{ maskImage: `url(${imgPlayerMask})` }}>
            {currentVideo ? (
              <video
                className="video-player"
                controls
                src={streamUrl(currentVideo.id)}
                poster={currentVideo.thumbnail_url || ""}
              />
            ) : (
              <img src={imgPlayer} alt="" />
            )}
          </div>
          <p className="player-hint">
            {currentVideo
              ? `Сейчас: ${currentVideo.title}. Кликните по видео, чтобы переключить.`
              : "Видео пока нет. Перейдите в /videos для загрузки."}
          </p>
        </div>
        <aside className="chat-panel">
          <div className="chat-tabs">
            <div className="tab active">
              Чат
              <span className="tab-underline" />
            </div>
            <div className="tab">Вопрос / ответ</div>
          </div>
          <div className="chat-messages">
            <div className="chat-list">
              {messages.map((item) => (
                <div className="chat-message" key={item.id}>
                  <div>
                    <p className="chat-name">{item.name}</p>
                    <p className="chat-text">{item.text}</p>
                  </div>
                  <div className="chat-likes">
                    <img src={item.active ? imgLikeActive : imgLike} alt="" />
                    <span className={item.active ? "like-active" : ""}>
                      {item.likes}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="scroll-bar">
              <div className="scroll-thumb" />
            </div>
          </div>
          <Link className="primary-btn two-line" to="/messages">
            <span>Хотите отправить сообщение?</span>
            <span>Кликните на эту кнопку</span>
          </Link>
          <Link className="secondary-link" to="/videos">
            Перейти к загрузке и управлению видео
          </Link>
        </aside>
      </div>
    </section>
  );
}

export default Translation;

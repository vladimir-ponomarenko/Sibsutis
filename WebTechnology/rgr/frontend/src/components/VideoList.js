import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "../VideoList.css";

const VideoList = () => {
  const [videos, setVideos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get("http://localhost:8000/api/videos/");
        setVideos(response.data);
      } catch (error) {
        console.error("Failed to fetch videos", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVideos();
  }, []);

  const getThumbnailUrl = (videoId) => {
    return `http://localhost:8000/api/videos/${videoId}/thumbnail`;
  };

  return (
    <div className="video-list-container">

      {isLoading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading videos...</p>
        </div>
      ) : videos.length === 0 ? (
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24">
            <path d="M18,9H16V7H18M18,13H16V11H18M18,17H16V15H18M8,9H6V7H8M8,13H6V11H8M8,17H6V15H8M18,3V5H16V3H8V5H6V3H4V21H6V19H8V21H16V19H18V21H20V3H18Z" />
          </svg>
          <p>No videos found</p>
        </div>
      ) : (
        <div className="video-feed">
          {videos.map((video) => (
            <Link
              to={`/video/${video.id}`}
              key={video.id}
              className="video-card"
            >
              <div className="thumbnail-container">
                <img
                  src={getThumbnailUrl(video.id)}
                  alt={video.title}
                  className="video-thumbnail"
                  onError={(e) => {
                    e.target.src =
                      "https://via.placeholder.com/320x180?text=No+Thumbnail";
                  }}
                />
                <div className="duration-badge">
                  {video.duration || "00:00"}
                </div>
              </div>
              <div className="video-info">
                <h3 className="video-title">{video.title}</h3>
                <p className="video-description">
                  {video.description || "No description available"}
                </p>
                <div className="video-meta">
                  <span className="upload-date">{video.upload_date || ""}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default VideoList;

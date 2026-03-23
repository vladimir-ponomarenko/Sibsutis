import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setStatus("Загрузка...");
      const response = await axios.post("http://localhost:8000/api/login/", {
        username,
        password,
      });
      onLogin(response.data.access, username);
      navigate("/videos");
    } catch (error) {
      setStatus("Ошибка входа. Проверьте данные.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="auth-tabs">
        <button
          type="button"
          className="auth-tab"
          onClick={() => navigate("/register")}
        >
          Регистрация
        </button>
        <button type="button" className="auth-tab active">
          Авторизация
        </button>
      </div>
      <h2>Данные для авторизации</h2>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Имя пользователя"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Пароль"
        required
      />
      <button type="submit" className="login-btn">
        Отправить
      </button>
      {status && <div className="status-text">{status}</div>}
    </form>
  );
};

export default Login;

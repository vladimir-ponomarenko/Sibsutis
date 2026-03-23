import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Register = ({ onRegister }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setStatus("Регистрация...");
      await axios.post("http://localhost:8000/api/register/", {
        username,
        password,
        email,
      });
      onRegister();
      setStatus("Успешно. Перенаправляем на вход...");
      setTimeout(() => navigate("/login"), 800);
    } catch (error) {
      setStatus("Ошибка регистрации");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <div className="auth-tabs">
        <button type="button" className="auth-tab active">
          Регистрация
        </button>
        <button
          type="button"
          className="auth-tab"
          onClick={() => navigate("/login")}
        >
          Авторизация
        </button>
      </div>
      <h2>Данные для регистрации</h2>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Имя пользователя"
        required
      />
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Электронная почта"
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

export default Register;

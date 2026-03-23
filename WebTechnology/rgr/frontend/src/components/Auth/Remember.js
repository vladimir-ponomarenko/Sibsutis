import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Remember = () => {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setStatus("Запрос отправлен. Проверьте почту.");
  };

  return (
    <form onSubmit={handleSubmit} className="remember-form">
      <h2>Восстановление доступа</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <button type="submit" className="login-btn">
        Отправить код
      </button>
      <button
        type="button"
        className="register-btn"
        onClick={() => navigate("/login")}
      >
        Вернуться ко входу
      </button>
      {status && <div className="status-text">{status}</div>}
    </form>
  );
};

export default Remember;

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, saveTokens } from "../api.js";

const imgBackground = "https://www.figma.com/api/mcp/asset/15bfa046-1e5d-4f43-8266-2a4e802dd0b5";
const imgLogo = "https://www.figma.com/api/mcp/asset/90ffcb53-1d45-4709-9cec-fc600a77a65b";

function Login() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus("Вход...");
    setError("");
    const formData = new FormData(event.target);
    try {
      const data = await login({
        username: formData.get("username"),
        password: formData.get("password"),
      });
      saveTokens(data);
      navigate("/videos");
    } catch (err) {
      setStatus("");
      setError(err.message);
    }
  };

  return (
    <section className="page-auth-figma" style={{ backgroundImage: `url(${imgBackground})` }}>
      <header className="top-bar">
        <img className="logo" src={imgLogo} alt="Logo" />
      </header>
      <div className="auth-center">
        <div className="tabs">
          <div className="tab active">
            Вход
            <span className="tab-underline" />
          </div>
        </div>
        <form className="auth-card figma-card narrow" onSubmit={handleSubmit}>
          <label className="field">
            <span>Имя пользователя</span>
            <div className="field-input">
              <input name="username" placeholder="Ваш логин" required />
            </div>
          </label>
          <label className="field">
            <span>Пароль</span>
            <div className="field-input">
              <input name="password" type="password" placeholder="Пароль" required />
            </div>
          </label>
          <button className="primary-btn" type="submit">Войти</button>
          {status && <p className="status-text">{status}</p>}
          {error && <p className="error-text">{error}</p>}
        </form>
      </div>
    </section>
  );
}

export default Login;

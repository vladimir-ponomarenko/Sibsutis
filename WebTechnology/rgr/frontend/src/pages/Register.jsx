import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../api.js";

const imgBackground = "https://www.figma.com/api/mcp/asset/15bfa046-1e5d-4f43-8266-2a4e802dd0b5";
const imgLogo = "https://www.figma.com/api/mcp/asset/90ffcb53-1d45-4709-9cec-fc600a77a65b";
const imgRequired = "https://www.figma.com/api/mcp/asset/a101db0d-41eb-4dd7-a486-8f373061f144";

function Register() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus("Отправка...");
    setError("");
    const formData = new FormData(event.target);
    try {
      await register({
        username: formData.get("username"),
        email: formData.get("email"),
        password: formData.get("password"),
      });
      setStatus("Регистрация успешна. Перенаправляем на вход...");
      setTimeout(() => navigate("/login"), 800);
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
            Регистрация
            <span className="tab-underline" />
          </div>
          <Link className="tab" to="/remember">Код доступа</Link>
        </div>
        <form className="auth-card figma-card" onSubmit={handleSubmit}>
          <div className="auth-group">
            <p className="group-title">Данные для авторизации</p>
            <label className="field">
              <span>Электронная почта</span>
              <div className="field-input">
                <input name="email" type="email" placeholder="my_email@ma" required />
                <img src={imgRequired} alt="" />
              </div>
            </label>
            <label className="field">
              <span>Пароль</span>
              <div className="field-input">
                <input name="password" type="password" placeholder="Введите пароль" required />
                <img src={imgRequired} alt="" />
              </div>
            </label>
          </div>
          <div className="auth-group">
            <p className="group-title">Прочие данные</p>
            <label className="field">
              <span>Фамилия</span>
              <div className="field-input">
                <input name="last_name" placeholder="Ваша фамилия" />
                <img src={imgRequired} alt="" />
              </div>
            </label>
            <label className="field">
              <span>Имя</span>
              <div className="field-input">
                <input name="first_name" placeholder="Ваше имя" />
                <img src={imgRequired} alt="" />
              </div>
            </label>
            <label className="field">
              <span>Имя пользователя</span>
              <div className="field-input">
                <input name="username" placeholder="Ваш логин" required />
                <img src={imgRequired} alt="" />
              </div>
            </label>
          </div>
          <button className="primary-btn" type="submit">Отправить</button>
          <p className="form-note">* поле, обязательное для заполнения</p>
          {status && <p className="status-text">{status}</p>}
          {error && <p className="error-text">{error}</p>}
        </form>
      </div>
    </section>
  );
}

export default Register;

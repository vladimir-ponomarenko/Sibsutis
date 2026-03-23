import { useState } from "react";
import { Link } from "react-router-dom";

const imgBackground = "https://www.figma.com/api/mcp/asset/59eba4fa-8897-4cc4-8935-ee70e16be9c3";
const imgLogo = "https://www.figma.com/api/mcp/asset/05c921b1-d57b-4d50-b4eb-ee763c5abb33";

function Remember() {
  const [status, setStatus] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    setStatus("Если почта есть в базе, код будет отправлен.");
  };

  return (
    <section className="page-auth-figma" style={{ backgroundImage: `url(${imgBackground})` }}>
      <header className="top-bar">
        <img className="logo" src={imgLogo} alt="Logo" />
      </header>
      <div className="auth-center">
        <div className="tabs">
          <Link className="tab" to="/register">Регистрация</Link>
          <div className="tab active">
            Код доступа
            <span className="tab-underline light" />
          </div>
        </div>
        <form className="auth-card figma-card narrow" onSubmit={handleSubmit}>
          <label className="field">
            <span>Укажите электронную почту для восстановления кода</span>
            <div className="field-input">
              <input name="email" type="email" placeholder="mail@mail.com" required />
            </div>
          </label>
          <button className="primary-btn" type="submit">Отправить код</button>
          {status && <p className="status-text">{status}</p>}
        </form>
      </div>
    </section>
  );
}

export default Remember;

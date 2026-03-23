const imgYadroPattern = "https://www.figma.com/api/mcp/asset/7553f20a-c54a-4d8e-b6bc-370d1e0ab07a";

function Bg2x() {
  return (
    <section className="page-translation">
      <div className="pattern-bg" style={{ backgroundImage: `url(${imgYadroPattern})` }} />
      <div className="bg2x-content">
        <p>Ссылка на оптимизированное изображение 2x</p>
        <a
          href="https://disk.yandex.ru/i/LP1QFuxfakDMOQ"
          target="_blank"
          rel="noreferrer"
        >
          https://disk.yandex.ru/i/LP1QFuxfakDMOQ
        </a>
      </div>
    </section>
  );
}

export default Bg2x;

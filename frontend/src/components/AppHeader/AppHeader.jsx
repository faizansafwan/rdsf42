export default function AppHeader({ cutoffTime, cutoffTz }) {
  return (
    <header className="app-header">
      <div className="app-header__bar">
        <div className="app-header__inner">
          <img
            src="/favicon.svg"
            alt=""
            width={40}
            height={40}
            className="app-header__mark"
            aria-hidden
          />
          <div className="app-header__titles">
            <h1 className="app-header__name">Tric Focast</h1>
            <p className="app-header__tagline">
              UK day-ahead wind forecast accuracy · Elexon WINDFOR vs FUELHH · January 2026
            </p>
          </div>
        </div>
      </div>
      <div className="app-header__lede-wrap">
        <p className="app-header__lede">
          Compares selected D-1 WINDFOR forecasts against wind outturn. Decision cutoff:{" "}
          <strong>
            {cutoffTime} {cutoffTz}
          </strong>{" "}
          on the day before each delivery day (assumed, configurable — not verified against
          official GB auction gate closure). Only forecasts published at or before this time
          are used.
        </p>
      </div>
    </header>
  );
}

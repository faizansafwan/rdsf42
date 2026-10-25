import { useState } from "react";
import DateRangePicker from "./components/DateRangePicker/DateRangePicker";
import MetricsSummaryCards from "./components/MetricsSummaryCards/MetricsSummaryCards";
import ForecastVsActualChart from "./components/ForecastVsActualChart/ForecastVsActualChart";
import ErrorBarChart from "./components/ErrorBarChart/ErrorBarChart";
import DataQualityBanner from "./components/DataQualityBanner/DataQualityBanner";
import PublishTimeHistogram from "./components/PublishTimeHistogram/PublishTimeHistogram";
import { useWindCompare } from "./hooks/useWindCompare";
import { useWindMetrics } from "./hooks/useWindMetrics";
import { usePublishTimeDistribution } from "./hooks/usePublishTimeDistribution";

const DEFAULT_START = "2026-01-01";
const DEFAULT_END = "2026-01-31";

export default function App() {
  const [start, setStart] = useState(DEFAULT_START);
  const [end, setEnd] = useState(DEFAULT_END);
  const [resolution, setResolution] = useState("30min");

  const compareQuery = useWindCompare(start, end, resolution);
  const metricsQuery = useWindMetrics(start, end);
  const publishQuery = usePublishTimeDistribution(start);

  const loading = compareQuery.isLoading || metricsQuery.isLoading;
  const error = compareQuery.error || metricsQuery.error;

  const compareBody = compareQuery.data;
  const metricsBody = metricsQuery.data;

  return (
    <div className="layout">
      <header>
        <h1>UK day-ahead wind forecast accuracy</h1>
        <p>
          Compares Elexon WINDFOR (D-1 selection at configurable gate closure) against
          FUELHH wind outturn for January 2026.
        </p>
      </header>

      <DateRangePicker
        start={start}
        end={end}
        resolution={resolution}
        onStartChange={setStart}
        onEndChange={setEnd}
        onResolutionChange={setResolution}
      />

      {error && (
        <div className="banner error" role="alert">
          {error.message}
          <button
            type="button"
            className="retry"
            onClick={() => {
              compareQuery.refetch();
              metricsQuery.refetch();
            }}
          >
            Retry
          </button>
        </div>
      )}

      {loading && <div className="skeleton" aria-busy="true" />}

      {!loading && !error && (
        <>
          <DataQualityBanner
            stale={compareBody?.stale}
            lastUpdated={compareBody?.last_updated}
            quality={compareBody?.quality}
          />
          <MetricsSummaryCards
            metrics={metricsBody?.metrics}
            excludedCount={metricsBody?.metrics?.mape_excluded_count ?? 0}
            floorMw={metricsBody?.metrics?.mape_floor_mw ?? 50}
          />
          <section className="panel">
            <h2>Forecast vs actual</h2>
            <ForecastVsActualChart data={compareBody?.data} />
          </section>
          <section className="panel">
            <h2>Forecast error by interval</h2>
            <p style={{ fontSize: "0.85rem", color: "#64748b", marginTop: 0 }}>
              Error = actual − forecast. Positive bars = under-forecast (actual higher
              than expected).
            </p>
            <ErrorBarChart data={compareBody?.data} />
          </section>
          <section className="panel">
            <h2>Forecast publish times (delivery day {start})</h2>
            <PublishTimeHistogram
              histogram={publishQuery.data?.histogram}
              date={start}
            />
          </section>
        </>
      )}

      <footer>
        Contains BMRS data © Elexon Limited copyright and database right. Source:{" "}
        <a href="https://www.elexon.co.uk/glossary/bmrs/" rel="noreferrer">
          Elexon BMRS
        </a>
        . Built with AI-assisted development (Cursor).
      </footer>
    </div>
  );
}

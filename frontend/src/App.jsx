import { useState } from "react";
import DateRangePicker from "./components/DateRangePicker/DateRangePicker";
import MetricsSummaryCards from "./components/MetricsSummaryCards/MetricsSummaryCards";
import ForecastVsActualChart from "./components/ForecastVsActualChart/ForecastVsActualChart";
import ErrorBarChart from "./components/ErrorBarChart/ErrorBarChart";
import DataQualityBanner from "./components/DataQualityBanner/DataQualityBanner";
import PublishTimeHistogram from "./components/PublishTimeHistogram/PublishTimeHistogram";
import SelectedForecastSummary from "./components/SelectedForecastSummary/SelectedForecastSummary";
import { useWindCompare } from "./hooks/useWindCompare";
import { useWindMetrics } from "./hooks/useWindMetrics";
import { usePublishTimeDistribution } from "./hooks/usePublishTimeDistribution";

const DEFAULT_START = "2026-01-01";
const DEFAULT_END = "2026-01-31";

export default function App() {
  const [start, setStart] = useState(DEFAULT_START);
  const [end, setEnd] = useState(DEFAULT_END);
  const [resolution, setResolution] = useState("30min");
  const [histogramDate, setHistogramDate] = useState(DEFAULT_START);

  const compareQuery = useWindCompare(start, end, resolution);
  const metricsQuery = useWindMetrics(start, end, resolution);
  const publishQuery = usePublishTimeDistribution(histogramDate);

  const loading = compareQuery.isLoading || metricsQuery.isLoading;
  const error = compareQuery.error || metricsQuery.error;

  const compareBody = compareQuery.data;
  const metricsBody = metricsQuery.data;
  const cutoffTime =
    compareBody?.decision_cutoff_local_time ??
    metricsBody?.decision_cutoff_local_time ??
    "11:00";
  const cutoffTz =
    compareBody?.decision_timezone ?? metricsBody?.decision_timezone ?? "Europe/London";

  return (
    <div className="layout">
      <header>
        <h1>UK day-ahead wind forecast accuracy</h1>
        <p>
          Compares Elexon WINDFOR (D-1 selection) against FUELHH wind outturn for January
          2026. Decision cutoff:{" "}
          <strong>
            {cutoffTime} {cutoffTz}
          </strong>{" "}
          on the day before each delivery day — only forecasts published at or before this
          time are used.
        </p>
      </header>

      <DateRangePicker
        start={start}
        end={end}
        resolution={resolution}
        onStartChange={(v) => {
          setStart(v);
          if (v > histogramDate) setHistogramDate(v);
        }}
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
          <MetricsSummaryCards metrics={metricsBody?.metrics} resolution={resolution} />
          <section className="panel">
            <h2>Forecast vs actual</h2>
            <ForecastVsActualChart data={compareBody?.data} />
          </section>
          <section className="panel">
            <h2>Selected forecast at gate closure</h2>
            <SelectedForecastSummary data={compareBody?.data} />
          </section>
          <section className="panel">
            <h2>Forecast error by interval</h2>
            <p className="panel-caption">
              Error = actual − forecast. Positive bars = under-forecast (actual higher than
              expected).
            </p>
            <ErrorBarChart data={compareBody?.data} />
          </section>
          <section className="panel">
            <h2>Publish-time audit (D-1 selection)</h2>
            <PublishTimeHistogram
              distribution={publishQuery.data}
              histogramDate={histogramDate}
              onDateChange={setHistogramDate}
              error={publishQuery.error}
              isLoading={publishQuery.isLoading}
            />
          </section>
        </>
      )}

    </div>
  );
}

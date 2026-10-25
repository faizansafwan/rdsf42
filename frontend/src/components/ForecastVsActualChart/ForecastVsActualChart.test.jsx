import { render, screen } from "@testing-library/react";
import ForecastVsActualChart from "./ForecastVsActualChart";

describe("ForecastVsActualChart", () => {
  it("renders chart container for mock series", () => {
    render(
      <ForecastVsActualChart
        data={[
          {
            start_time: "2026-01-01T00:00:00Z",
            actual_mw: 5000,
            forecast_mw: 4800,
          },
        ]}
      />
    );
    expect(screen.getByTestId("forecast-chart")).toBeInTheDocument();
  });
});

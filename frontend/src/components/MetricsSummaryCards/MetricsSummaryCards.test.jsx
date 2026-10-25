import { render, screen } from "@testing-library/react";
import MetricsSummaryCards from "./MetricsSummaryCards";

describe("MetricsSummaryCards", () => {
  it("renders metric values including MAPE exclusion detail", () => {
    render(
      <MetricsSummaryCards
        resolution="30min"
        metrics={{
          mae: 1200,
          rmse: 1500,
          mape: 8.5,
          smape: 7.2,
          bias: -300,
          mape_excluded_count: 37,
          mape_floor_mw: 100,
        }}
      />
    );
    expect(screen.getByTestId("metrics-cards")).toBeInTheDocument();
    expect(screen.getByText("MAE")).toBeInTheDocument();
    expect(screen.getByText("1,200 MW")).toBeInTheDocument();
    expect(
      screen.getByText("8.5% (37 low-wind intervals excluded, below 100 MW)")
    ).toBeInTheDocument();
  });
});

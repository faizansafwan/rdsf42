import { render, screen } from "@testing-library/react";
import MetricsSummaryCards from "./MetricsSummaryCards";

describe("MetricsSummaryCards", () => {
  it("renders metric values from mock data", () => {
    render(
      <MetricsSummaryCards
        metrics={{
          mae: 1200,
          rmse: 1500,
          mape: 8.5,
          smape: 7.2,
          bias: -300,
        }}
        excludedCount={12}
        floorMw={50}
      />
    );
    expect(screen.getByTestId("metrics-cards")).toBeInTheDocument();
    expect(screen.getByText("MAE")).toBeInTheDocument();
    expect(screen.getByText("1,200 MW")).toBeInTheDocument();
    expect(screen.getByText(/Excluded 12 intervals/)).toBeInTheDocument();
  });
});

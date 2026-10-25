from app.services.metrics import compute_metrics


def test_metrics_hand_computed():
    # actuals: 100, 200 | forecasts: 90, 220
    # errors: 10, -20 | abs: 10, 20
    # mae = 15, rmse = sqrt((100+400)/2) = sqrt(250) ≈ 15.811
    # bias = (10 + -20)/2 = -5
    actuals = [100.0, 200.0]
    forecasts = [90.0, 220.0]
    m = compute_metrics(actuals, forecasts, mape_floor_mw=50.0)
    assert m.n_points == 2
    assert m.mae == 15.0
    assert abs(m.rmse - (250**0.5)) < 1e-9
    assert m.bias == -5.0
    assert m.mape_excluded_count == 0
    assert abs(m.mape - ((10 / 100 + 20 / 200) / 2 * 100)) < 1e-9


def test_mape_excludes_low_actuals():
    actuals = [10.0, 200.0]
    forecasts = [5.0, 180.0]
    m = compute_metrics(actuals, forecasts, mape_floor_mw=50.0)
    assert m.mape_excluded_count == 1
    assert abs(m.mape - (20 / 200 * 100)) < 1e-9

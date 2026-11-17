# Demand Planning Standard Operating Procedure

## Purpose

This SOP guides Demand Planners through weekly review of sales performance, forecast accuracy, and promotional effectiveness using the `weekly_metrics.csv` business export.

## Key Metrics

### Forecast Error %

Measures how far actual sales deviated from the forecast.

```
forecast_error_percent = abs(sales_volume_units - forecast_volume_units) / forecast_volume_units * 100
```

| Threshold | Interpretation | Action |
|-----------|----------------|--------|
| < 10% | Acceptable accuracy | Monitor only |
| 10–25% | Moderate miss | Investigate drivers |
| > 25% | Severe miss | Escalate to supply chain |

**Example:** Classic Potato Chips shows forecast_volume_units of 10,000 but sales_volume_units of 15,000 — a 50% under-forecast triggering stockouts.

### Promotion Return Ratio

Measures whether marketing spend generated incremental revenue.

```
promotion_return_ratio = gross_sales_revenue / marketing_promotion_spend
```

| Threshold | Interpretation | Action |
|-----------|----------------|--------|
| > 8.0 | Strong ROI | Scale promotion |
| 4.0–8.0 | Acceptable ROI | Optimize targeting |
| < 4.0 | Inefficient spend | Pause and review |

**Example:** Fresh Orange Juice in SOUTH shows marketing_promotion_spend up 12% while gross_sales_revenue drops 8% — promotion_return_ratio collapses, indicating wasted spend.

## Weekly Review Checklist

1. Filter `weekly_metrics.csv` by operating_region and week_number.
2. Rank products by forecast_error_percent (descending).
3. Flag any product where promotion_return_ratio < 4.0.
4. Compare against Spark Cola 500ml (healthy control benchmark).
5. Document findings and recommended forecast adjustments.

## Escalation

Escalate to the Supply Chain Lead when:
- forecast_error_percent exceeds 25% for two consecutive weeks
- promotion_return_ratio drops below 3.0 in any region

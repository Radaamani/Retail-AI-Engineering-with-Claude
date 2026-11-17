# Inventory Replenishment Standard Operating Procedure

## Purpose

This SOP defines when and how much to restock using the `regional_inventory.csv` business export.

## Replenishment Trigger

An item requires replenishment when current stock falls to or below the reorder trigger:

```
if current_stock_units <= reorder_trigger_level:
    order_units = reorder_trigger_level + safety_stock_units - current_stock_units
```

| Field | Meaning |
|-------|---------|
| current_stock_units | Units available in the regional warehouse |
| reorder_trigger_level | Stock level that triggers a purchase order |
| safety_stock_units | Buffer to absorb demand variability |
| supplier_lead_days | Days until the supplier delivers |

## Worked Example

Premium Ground Coffee in NORTH:
- current_stock_units = 900
- reorder_trigger_level = 1,500
- safety_stock_units = 500

Since 900 ≤ 1,500, reorder is triggered:
```
order_units = 1500 + 500 - 900 = 1,100 units
```

With supplier_lead_days = 14, place the order immediately to avoid stockout during the lead window.

## Priority Classification

| Condition | Priority | Action |
|-----------|----------|--------|
| current_stock_units ≤ reorder_trigger_level AND supplier_lead_days > 10 | Critical | Expedite order |
| current_stock_units ≤ reorder_trigger_level | High | Standard replenishment |
| current_stock_units ≤ reorder_trigger_level + safety_stock_units | Medium | Plan next cycle |
| Above safety buffer | Low | No action |

## Weekly Review Checklist

1. Open `regional_inventory.csv` and sort by current_stock_units ascending.
2. Apply the replenishment formula to every row where stock ≤ reorder_trigger_level.
3. Cross-reference `weekly_metrics.csv` for demand trends (growing demand + thin buffer = highest risk).
4. Submit purchase orders grouped by supplier_lead_days (longer lead = higher urgency).

## Escalation

Escalate to the Operations Manager when:
- Any SKU has current_stock_units below safety_stock_units
- supplier_lead_days exceeds 10 and a replenishment order has not been placed

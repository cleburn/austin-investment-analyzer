# Claude Code Workflow Instructions

## Development Methodology

**Always discuss logic, confirm data understanding, and validate methodology before generating code. Wait for explicit approval before implementation.**

### Workflow Rules:

1. **Plan Before Coding**
   - Discuss the approach and logic first
   - Confirm understanding of the data structure and requirements
   - Validate the methodology with the user
   - Wait for explicit "yes" or "proceed" before writing code

2. **No Assumptions**
   - Ask clarifying questions when requirements are ambiguous
   - Verify data sources and column names before using them
   - Confirm calculations and formulas before implementing

3. **Incremental Progress**
   - Break complex tasks into smaller, reviewable steps
   - Show intermediate results for validation
   - Test assumptions with sample data before full implementation

4. **Communication**
   - Explain trade-offs and alternatives
   - Present options when multiple valid approaches exist
   - Be transparent about limitations and uncertainties

## Git Commit Guidelines

- Focus on what changed and why, not how
- Do NOT include mentions of Claude, AI assistance, or tool credits
- Do NOT include "Co-Authored-By" attributions
- Use clear, concise language

---

## Project Status (Updated Apr 2026)

### Overview
Real estate investment analysis app with ML-powered appreciation predictions. Helps users identify neighborhoods with strong ROI potential across Texas and Florida metros.

### Current Model: Model C (24-Month Lookback)

**Architecture:**
- **Type**: RandomForest price prediction model
- **Training Data**: 2002-2024 (36,370 examples)
- **Price Range**: $170,000 - $1,000,000 (training population bounds)
- **Min History**: 24 months of price data required
- **Features**: 14 features including cagr_2yr (not 3yr/5yr due to lookback constraint)

**Forward Validation (Nov 2025 – Mar 2026, 5 months past training cutoff):**
- **MAPE**: 2.45–2.63% (improving over the window)
- **R²**: ≥ 0.99 across all months
- **Coverage**: 4,197 neighborhoods with predictions (Mar 2026 snapshot)

**Appreciation Derivation:**
```
appreciation_rate = (predicted_price - current_price) / current_price * 100
```

### Key Files

```
app.py                                    # Main Streamlit app
process_data.py                           # Data processing script
config/metros.yaml                        # Metro configuration
config/metro_config.py                    # Config loader
config/zillow_filter.py                   # Shared Zillow data filtering utility

ml/models/predictor.py                    # Appreciation predictor (loads CSV)
ml/artifacts/model_c/price_model.joblib   # Trained Model C
ml/artifacts/model_c/model_info.json      # Model metadata

notebooks/08_clean_pipeline_v2.ipynb      # Canonical ML pipeline

data/processed/appreciation_predictions_current.csv  # Pre-computed predictions
data/processed/neighborhoods_multi_metro.csv         # App neighborhood data
```

### Critical Implementation Details

**1. Sanity Caps on Appreciation:**
- All predictions capped to -10% to +15% annual
- Applied in notebook during prediction generation
- Also applied in app.py for fallback values (baseline_cagr)

**2. Conservative Multi-Year Projection:**
- Year 1: Use ML prediction (capped -10% to +15%)
- Years 2+: min(ML rate, 7%) for positive, 0% for negative
- Prevents unrealistic compounding of high appreciation rates

**3. Negative Appreciation Floor:**
- Declining markets: Year 1 decline only, then flat
- Prevents unrealistic depreciation to $0 over long holds

**4. Metro Key Matching:**
- Keys are `{neighborhood}_{city}_{display_metro}` (e.g., `Downtown_Dallas_dallas`)
- City is included to disambiguate duplicate neighborhood names within a metro
- Predictions use `display_metro` (dallas, fort_worth, miami, fort_lauderdale)
- NOT `training_metro` (dfw, south_florida)
- Key format must match across: predictor.py, app.py, and the predictions CSV

**5. Price Filter:**
- Only neighborhoods within $170k-$1M get ML predictions
- Outside this range falls back to baseline_cagr (also capped)

### Data Flow

```
Zillow ZHVI data (raw)
    ↓
config/zillow_filter.py (metro filtering via metros.yaml)
    ↓
08_clean_pipeline_v2.ipynb (feature extraction, model training)
    ↓
appreciation_predictions_current.csv (pre-computed)
    ↓
predictor.py (loads CSV, provides lookup)
    ↓
app.py (uses predictions for ROI calculations)
```

### Metros Supported

**Training Groups (9):**
- DFW (combined: dallas, fort_worth)
- South Florida (combined: miami, fort_lauderdale)
- austin, houston, san_antonio, waco
- tampa, orlando, jacksonville

**Display Metros (11):**
- dallas, fort_worth, austin, houston, san_antonio, waco
- miami, fort_lauderdale, tampa, orlando, jacksonville

**Removed:** Abilene (Feb 2026) — only 11 neighborhoods, 7.90% MAPE in forward validation (3x worse than average). Too small a sample for reliable predictions.

### Important Data Processing Details

- **State filtering**: Shared utility (`config/zillow_filter.py`) and process_data.py filter Zillow data by City AND State using metros.yaml as the source of truth, preventing same-named cities from wrong states (e.g., Richmond TX vs Richmond VA)
- **Annualized ROI clamping**: The annualized ROI formula clamps `(1 + roi/100)` to a floor of 0 before exponentiation to prevent complex/NaN results when total ROI < -100%
- **Capital gains tax floor**: Sell scenario caps `cap_gains_tax` at 0 (no tax credit for losses)
- **LTR tier boundaries**: `get_ltr_rate()` uses `<=` for tier boundaries so exact threshold prices match their intended tier
- **Neighborhood identity**: `city` column is included in neighborhoods_multi_metro.csv and used in ML key matching to avoid duplicate-name collisions. Both prediction and historical fallback keys use `{name}_{city}_{metro}` format.
- **Occupancy guard**: `process_data.py` sets occupancy to 0 when `availability_365 <= 0` to prevent division-by-zero inflation in STR income calculations

### Known Limitations

1. **Price bounds**: Homes outside $170k-$1M don't get ML predictions
2. **1-year horizon**: Model predicts 1 year ahead; multi-year is extrapolated with caps
3. **Fort Worth outliers**: Several Fort Worth neighborhoods show >20% prediction error; may need investigation when more data is available
4. **STR merge within metros**: Airbnb data lacks a city column, so same-named neighborhoods in different cities within one metro (e.g., "Downtown" in Dallas vs Irving) share STR metrics. Cross-metro contamination doesn't occur (merge runs per display metro).
5. **Inside Airbnb public CSV is no longer drop-in usable** (Apr 2026): the 2026-01-20 Dallas scrape returned an `listings.csv.gz` with `price`, `host_neighbourhood`, and `estimated_revenue_l365d` 100% blank — schema columns exist but values are empty. `process_data.py` requires both `price` (for STR income) and `host_neighbourhood` (for grouping). The Aug 2025 Airbnb files in `data/raw/` predate this change and remain the production source. Refreshing STR data now requires merging Inside Airbnb's `calendar.csv.gz` (per-listing nightly prices) onto the listings file and switching grouping to `neighbourhood_cleansed` — non-trivial pipeline change deferred to a future cycle.

### Future Enhancements (Deferred)

- FRED economic data integration (interest rates, employment)
- Confidence intervals for predictions
- Multi-horizon models (3yr, 5yr direct prediction)
- Longer-horizon forward validation (Jan-Mar 2026 data) to test model over 3+ month window before making model adjustments

### Design Decisions

- **ML as default**: Predictions are always used, not a toggle
- **Conservative projections**: Cap long-term appreciation at 7%/year
- **Pre-computed predictions**: CSV lookup, not real-time inference
- **Single canonical notebook**: 08_clean_pipeline_v2.ipynb does everything

---

## Monthly Forward-Validation Protocol

When new Zillow ZHVI data is released:

### Step 1: Forward-Validate Current Model
Before updating the app data, test how well the existing model predicts the new actuals:

1. Download new ZHVI file to `~/Downloads/`
2. Run forward validation: extract features from the previous month's data, predict with Model C, compare to new month's actuals
3. Evaluate overall metrics (MAPE, MAE, R²) and break down by metro and price tier
4. Identify any metros or neighborhoods with degraded accuracy
5. Decide: if model still performs well, proceed to update; if gaps emerge, investigate improvements first

**Baseline benchmarks (5-month forward validation, Apr 2026):**

| Window               | MAPE  | MAE      | R²     | Within 5% | Direction |
|----------------------|-------|----------|--------|-----------|-----------|
| Nov 2025 (1-month)   | 2.63% | $10,112  | 0.9918 | 87.2%     | 70.6%     |
| Dec 2025 (2-month)   | 2.53% | $10,258  | 0.9912 | 88.6%     | —         |
| Jan 2026 (3-month)   | 2.58% | $10,889  | 0.9901 | 87.5%     | 63.9%     |
| Feb 2026 (4-month)   | 2.54% | $10,690  | 0.9901 | 88.3%     | 61.2%     |
| Mar 2026 (5-month)   | 2.45% | $10,191  | 0.9909 | 89.0%     | 59.0%     |

No aggregate drift — MAPE and R² actually improving over the window. Direction accuracy declining (70.6% → 59.0%) which is expected for a 1-year-trained model evaluated on 1-month gaps. Apr 2026 watchlist: **Waco** (n=13, MAPE creeping 3.86% → 5.51%, eyed for removal next cycle), **Jacksonville** (Mar 2026 spike to 4.42% MAPE, magnitude not direction error).

### Step 2: Update Data and Regenerate Predictions
```bash
# 1. Copy new ZHVI file:
cp ~/Downloads/Neighborhood_zhvi_*.csv data/raw/zillow_zhvi_neighborhoods.csv

# 2. Regenerate predictions (uses trained Model C + new data):
#    Run prediction generation script with updated features

# 3. Regenerate neighborhood data:
python process_data.py

# 4. Commit and push:
git add data/processed/appreciation_predictions_current.csv data/processed/neighborhoods_multi_metro.csv
git commit -m "Update predictions with [Month Year] Zillow data"
git push
```

Streamlit Cloud will auto-redeploy with new predictions.

**Note:** The model file (`price_model.joblib`) stays local - only the predictions CSV and neighborhood data are pushed.

### Step 3: Longer-Horizon Validation
Next validation: ~May-Jun 2026 with data through Apr-May 2026 (7+ month window from training cutoff). Look for MAPE drift above 3.5% or R² below 0.98 as triggers for retraining. Specific decision points for next cycle: remove Waco if MAPE keeps climbing, investigate Jacksonville magnitude error.

# Export data dictionary

All source data is synthetic. ISO timestamps use a fictional UTC plant clock.

## DIM_DATE

Grain: one row per dimension key

| Column | Type | Definition |
|---|---|---|
| DATE_ID | object | Production date on batch fact; event start date on downtime fact |

## DIM_INSPECTION

Grain: one row per dimension key

| Column | Type | Definition |
|---|---|---|
| INSPECTION_STATUS | object | inspection status |

## DIM_MACHINE

Grain: one row per dimension key

| Column | Type | Definition |
|---|---|---|
| MACHINE_ID | object | machine id |
| LINE_ID | object | line id |

## DIM_MODEL

Grain: one row per dimension key

| Column | Type | Definition |
|---|---|---|
| MODEL_ID | object | model id |

## DIM_SHIFT

Grain: one row per dimension key

| Column | Type | Definition |
|---|---|---|
| SHIFT_ID | object | shift id |

## FACT_BATCH_QUALITY

Grain: one row per batch

| Column | Type | Definition |
|---|---|---|
| BATCH_ID | object | batch id |
| START_TIME | object | start time |
| END_TIME | object | end time |
| LINE_ID | object | line id |
| SHIFT_ID | object | shift id |
| MODEL_ID | object | model id |
| MACHINE_ID | object | machine id |
| DATE_ID | object | Production date on batch fact; event start date on downtime fact |
| PRODUCTION_VOLUME | int64 | Vehicles in batch; vehicle-level defect counts unavailable |
| TEMPERATURE_C | float64 | Mean valid pre-completion sensor temperature, Celsius |
| HUMIDITY_PCT | float64 | Mean valid pre-completion relative humidity, percent |
| PRESSURE_BAR | float64 | Mean valid pre-completion pressure, bar |
| INSPECTION_ID | object | inspection id |
| INSPECTION_TIME | object | inspection time |
| FAILED | int64 | Initial batch inspection label: 1 fail, 0 pass |
| DEFECT_CATEGORY | object | defect category |
| RISK_SCORE | float64 | Uncalibrated model probability-like score, 0–1; not proof of defect |
| RISK_FLAG | int64 | risk flag |
| SCORE_TIME | object | score time |
| SPLIT | object | split |
| SCORE_SCOPE | object | HELD_OUT for test; DEVELOPMENT_ONLY otherwise |
| INSPECTED_BATCHES | int64 | inspected batches |
| FAILED_BATCHES | int64 | failed batches |
| FIRST_PASS_BATCHES | int64 | first pass batches |
| INSPECTION_STATUS | object | inspection status |

## FACT_DOWNTIME

Grain: one row per event

| Column | Type | Definition |
|---|---|---|
| EVENT_ID | object | event id |
| MACHINE_ID | object | machine id |
| DOWNTIME_START | object | downtime start |
| EVENT_CATEGORY | object | event category |
| DOWNTIME_END | object | downtime end |
| DATE_ID | object | Production date on batch fact; event start date on downtime fact |
| DOWNTIME_MINUTES | float64 | downtime minutes |

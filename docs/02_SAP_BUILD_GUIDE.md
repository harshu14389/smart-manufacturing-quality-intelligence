# SAP build guide — checkpoints for a beginner

This is a guided manual tenant build, not a one-click SAP deployment. Interface wording and permissions vary by tenant/version. If a named control is absent, stop at that checkpoint and share the screen; do not guess an unrelated action. The source of truth is the exact CSV header and your tenant's technical name.

## A. Prepare
1. Run the local project successfully first.
2. Open your Datasphere tenant in a browser and sign in.
3. Open your existing authorised space. Confirm that you can create local tables and views. Use the same working Datasphere–SAC connection as your previous projects if available.
4. Keep this guide open beside the browser (Windows + Left Arrow / Windows + Right Arrow snap windows).

## B. Import the seven CSVs
1. Open Data Builder for your space.
2. Choose the import/create-table-from-CSV action offered by your tenant.
3. Browse to the extracted project → data → sap_import.
4. Import each file below separately. Use the filename without .csv as its technical name. Check first row as column headers and comma delimiter. Preview before finishing.
5. Check types before deployment: IDs and categories are strings; counts and flags integers; sensor values/risk/downtime decimal; timestamp columns timestamp; DATE_ID date or consistently formatted date string.
6. Set the key listed below if the table editor supports it. Save, deploy and check row counts. Do not rename tables after writing SQL references.

| Table | Key | Expected rows |
|---|---|---:|
| FACT_BATCH_QUALITY | BATCH_ID | 3600 |
| FACT_DOWNTIME | EVENT_ID | 515 |
| DIM_MACHINE | MACHINE_ID | 3 |
| DIM_SHIFT | SHIFT_ID | 3 |
| DIM_MODEL | MODEL_ID | 3 |
| DIM_DATE | DATE_ID | 150 |
| DIM_INSPECTION | INSPECTION_STATUS | 2 |

If a CSV numeric column becomes text, fix its type before creating measures. DIM_DATE is a simple date lookup; a full time dimension with calendar hierarchy is an optional later extension.

## C. Create dimensions
For each DIM table, create a graphical view, add the matching table, expose its columns and set semantic usage to Dimension. Use technical view names D_MACHINE, D_SHIFT, D_MODEL, D_DATE, D_INSPECTION. Set the listed key as key, save and deploy. For D_MACHINE retain LINE_ID as an attribute.

## D. Create batch fact
1. Create a graphical view named V_BATCH_QUALITY and add FACT_BATCH_QUALITY.
2. Expose its columns. Set semantic usage to Fact where supported.
3. Add many-to-one associations on matching keys to D_MACHINE, D_SHIFT, D_MODEL, D_DATE and D_INSPECTION. Map MACHINE_ID→MACHINE_ID, and similarly for other keys. Verify the dimensions are unique before marking cardinality.
4. Define INSPECTED_BATCHES, FAILED_BATCHES, FIRST_PASS_BATCHES and PRODUCTION_VOLUME as SUM measures. RISK_SCORE may be AVG only when labelled Mean Estimated Risk. Do not sum temperatures or risk.
5. Keep BATCH_ID, LINE_ID, SPLIT, SCORE_SCOPE, DEFECT_CATEGORY and other context as attributes for investigation. Save and deploy.
6. Create an analytic model AM_PAINT_QUALITY on this fact. Include associations and measures. If formula measures are supported, create the weighted KPI formulas in 01_PROJECT_GUIDE.md. Otherwise create them in SAC from the additive totals.
7. In preview verify 3600 inspected batches and compare failed totals with the local daily_quality.csv sum. Rate must equal total failures divided by total inspections.

## E. Create downtime fact
Create V_DOWNTIME from FACT_DOWNTIME, with Fact semantic usage, DOWNTIME_MINUTES SUM, and many-to-one associations to D_MACHINE and D_DATE. Keep EVENT_CATEGORY available. Deploy; create AM_PAINT_DOWNTIME. Never attach events to batch rows by date or line. Local total downtime can be checked by summing the CSV.

## F. Optional SQL consumption views
The two datasphere_*.sql files contain SELECT bodies for SQL views, not CREATE TABLE scripts. Copy a body into a new SQL view only after source tables exist. Select text using Ctrl + A in the file, Ctrl + C, click SQL editor and Ctrl + V. Validate, save and deploy with names V_DAILY_QUALITY_SQL and V_DAILY_DOWNTIME_SQL. A valid SQL view alone is not an analytic model.

## G. SAC story
1. Open SAC and use your authorised Datasphere connection.
2. Create a story and select AM_PAINT_QUALITY as a live model if exposed by your connection. If unavailable, check deployment, space permissions and connection settings; do not claim CSV import is a live Datasphere connection.
3. Page 1 — Quality Overview: inspected batches, failed batches, batch defect rate and batch first-pass yield; charts by LINE_ID, SHIFT_ID, MODEL_ID and DEFECT_CATEGORY. Exclude category None for the defect-type chart. Add date/line/shift/model filters.
4. Page 2 — Operations: add AM_PAINT_DOWNTIME; minutes by machine and category plus trend by DATE_ID. Keep model-specific filters separate unless linked dimensions have been configured and verified.
5. Page 3 — Risk Investigation: use quality model, filter SCORE_SCOPE to HELD_OUT. Table: BATCH_ID, SCORE_TIME, sensor means, RISK_SCORE, RISK_FLAG, INSPECTION_STATUS, DEFECT_CATEGORY. Use batch ID to maintain batch grain. Add text: “Estimated risk is a prioritisation aid; inspection confirms outcomes.”
6. Page 4 — Model Evaluation: add actual test metrics from outputs/model_evaluation.json and confusion-matrix image as local evaluation evidence. Clearly label these as local Python results.
7. Confirm the same filters and totals in local exports and SAC. Save your story. Export a PDF and capture model screenshots only after building them.

## H. Evidence checklist
Save real evidence in Evidence/: deployed model and association screenshots; SAC pages; reconciled batch example; exported story PDF. Avoid credentials and tenant secrets. Document your actual build date and any changes from this guide. Do not describe SAP deployment as completed until these checks are done.

## Official SAP references
Checked 24 October 2026.
- https://help.sap.com/docs/sap_datasphere/c8a54ee704e94e15926551293243fd1d/1c674aa858fa475fb36492972e418beb.html
- https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/e5fbe9e2cb93484dab8b1963145e565f.html

# Smart Manufacturing Intelligence & Predictive Quality Platform

An automotive paint-shop portfolio project using Python, SQL, SAP Datasphere and SAP Analytics Cloud to explore production quality, downtime events and estimated batch risk.

**All data in this project is synthetic.** This is a portfolio demonstration, not a deployed industrial production system.

## Project overview

The project brings together production batches, process readings, inspection results and machine downtime events. It supports investigation of observed quality patterns and comparison of estimated batch risk with initial inspection outcomes.

The prediction point is batch completion, before inspection. Risk scores are prioritisation aids and do not confirm that a batch is defective.

## What I built

- **Python:** Generated and processed synthetic data, performed validation checks and trained a classification model to estimate batch defect risk.
- **SQL:** Created transformations and validation logic for manufacturing data.
- **SAP Datasphere:** Built and deployed manufacturing quality and downtime analytical models.
- **SAP Analytics Cloud:** Built a four-page story covering quality overview, first-pass yield over time, batch risk versus inspection results, and downtime event counts by category.

The local pipeline run produced **3,600 batches** and reported **26 validation checks passed**.

## Dashboard

The exported SAP Analytics Cloud story is available in the `Evidence/` folder:

[View the dashboard PDF](Evidence/mart%20Manufacturing%20Intelligence%20(1).pdf)

The downtime chart shows the **number of events**, not their total duration.

## Project structure

- `src/` — data generation, cleaning, validation, modelling and exports.
- `data/raw/` — synthetic production, sensor, inspection and event data.
- `data/sap_import/` — facts and dimensions prepared for SAP upload.
- `sql/` — local transformations and Datasphere view bodies.
- `outputs/` — model evaluation, confusion matrix, correlations and validation results.
- `docs/` — architecture, data dictionary, KPI definitions and build instructions.
- `Evidence/` — exported SAP Analytics Cloud dashboard.

## Run the project

Use Python 3.11 or 3.12. Follow `START_HERE_WINDOWS.md` to set up the environment and install the dependencies, then run:

```bash
python src/run_project.py
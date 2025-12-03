# Final Project – Data Mining with Airflow + Apriori

Mini data mining pipeline that simulates a daily market-basket analysis using Apache Airflow and a pure-Python implementation of the Apriori algorithm. The repo includes sample transactions, cleaning logic, Apriori mining, rule generation, and a report generator so the pipeline can be demonstrated locally.

## Scenario and Dataset
- **Use case:** analyze daily grocery-style transactions (bread, milk, butter, etc.) to learn product affinities.
- **Sample data:** `data/raw/transactions.csv` with 12 transactions, each containing 1–3 items.
- **Cleaning:** items are title-cased, deduplicated per basket, and stored as JSON arrays in `data/processed/cleaned_transactions.csv`.

## Repository Layout
```
project/
├─ dags/
│  └─ apriori_pipeline_dag.py
├─ data/
│  ├─ raw/transactions.csv
│  └─ processed/cleaned_transactions.csv
├─ models/                   # Reserved for serialized models (not used in this sample)
├─ results/
│  ├─ frequent_itemsets.csv
│  ├─ rules.csv
│  ├─ summary_report.md
│  └─ report.md
└─ scripts/
   ├─ load_data.py
   ├─ apriori.py
   └─ generate_report.py
```

## Airflow DAG
The DAG (`dags/apriori_pipeline_dag.py`) orchestrates three sequential Python tasks:
1. **`extract_and_clean`** – runs `scripts/load_data.clean_transactions` to sanitize raw CSV data.
2. **`run_apriori`** – executes `scripts/apriori.run_apriori_pipeline` (manual Apriori algorithm, rule mining, and CSV/markdown outputs).
3. **`generate_report`** – calls `scripts/generate_report.generate_report` to compile a concise markdown summary.

## Running Everything Step by Step

### Prerequisites
- Python 3.10+ available on your machine.
- (Optional but recommended) a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
- No extra packages are needed; the scripts only use the Python standard library.

### Local pipeline (fastest demo, no Airflow)
1. **Clone or unzip the repo** and move into it:
   ```bash
   cd Final-Project-DataMining
   ```
2. **Clean the raw transactions** into JSON arrays:
   ```bash
   python scripts/load_data.py
   ```
   - Produces `data/processed/cleaned_transactions.csv`.
3. **Run the Apriori mining step** to get frequent itemsets and rules:
   ```bash
   python scripts/apriori.py
   ```
   - Produces `results/frequent_itemsets.csv` and `results/rules.csv`.
4. **Generate the human-readable report**:
   ```bash
   python scripts/generate_report.py
   ```
   - Produces `results/report.md` and `results/summary_report.md`.
5. **Review outputs** in the `results/` directory. The markdown reports summarize the mined patterns.

### Running in Airflow with Docker Compose
Use Docker if you want an isolated Airflow stack (webserver + scheduler + Postgres):
1. **Set an Airflow UID (Linux/macOS):**
   ```bash
   export AIRFLOW_UID=$(id -u)
   ```
   If you skip this on macOS/Windows, Docker Desktop will fall back to a default value (50000).
2. **Start the Airflow metadata DB and initialize users/db schema:**
   ```bash
   docker compose up airflow-init
   ```
   This step also creates the `logs/`, `plugins/`, `data/`, and `results/` folders with the right permissions.
3. **Launch the webserver + scheduler + Postgres in the background:**
   ```bash
   docker compose up -d
   ```
   - Web UI: http://localhost:8080 (default creds: `airflow` / `airflow`).
4. **Trigger the DAG** named `apriori_pipeline` from the UI or CLI:
   ```bash
   docker compose exec airflow-webserver airflow dags trigger apriori_pipeline
   ```
   The DAG will run the same three tasks as the local demo: extract/clean → Apriori mining → report generation. Outputs are mounted to the host under `results/`.

### Running Airflow directly (without Docker)
If you prefer a local install instead of containers:
1. **Install Airflow (one-time)** following the official constraints file for your Python version.
2. **Set the project as AIRFLOW_HOME** (or mount it inside your Airflow deployment):
   ```bash
   export AIRFLOW_HOME="$PWD"
   ```
3. **Initialize and start Airflow services** from the project root:
   ```bash
   airflow db init
   airflow scheduler &
   airflow webserver -p 8080 &
   ```
4. **Ensure the DAG can import the scripts**: the DAG already appends the repo root to `sys.path`, so no extra PYTHONPATH configuration is needed if you run from the project root.
5. **Trigger the DAG** named `apriori_pipeline`:
   ```bash
   airflow dags trigger apriori_pipeline
   ```
   Alternatively, trigger it from the Airflow UI. Each run executes the same three tasks as the local demo: extract/clean → Apriori mining → report generation.

## Apriori Implementation (manual, no mlxtend)
- Candidate generation and pruning with the classic Apriori strategy.
- Support, confidence, and lift metrics.
- Configurable thresholds via `AprioriConfig` (default: support=0.2, confidence=0.4, lift=1.0).
- Supports small item universes (5–20 items) and runs quickly on the provided toy data.

## Sample Results (from the included dataset)
- **Top frequent items:** Milk (50% support), Bread (50%), Butter (41.7%).
- **Example rules:** `Eggs -> Milk` (support=0.25, confidence=1.0, lift=2.0), `Butter -> Milk` (support=0.25, confidence=0.6, lift=1.2).
- Full outputs live in `results/frequent_itemsets.csv`, `results/rules.csv`, and `results/report.md`.

## Architecture Diagram
```mermaid
flowchart LR
    A[Raw transactions CSV] --> B[Clean & normalize (load_data.py)]
    B --> C[Cleaned CSV]
    C --> D[Apriori mining (apriori.py)]
    D --> E[Frequent itemsets CSV]
    D --> F[Association rules CSV]
    E --> G[Markdown reports]
    F --> G
    G --> H[Results folder / dashboards]
```

## Short Report (2–4 pages condensed)
- **Problem:** discover item affinities in small daily market-basket data to inform promotions and co-location.
- **Dataset:** 12 synthetic grocery transactions (1–3 items each) stored in CSV, then cleaned into JSON item arrays.
- **Pipeline:** Airflow DAG with extract/clean → Apriori mining → reporting; runnable via Python scripts for quick demos.
- **Algorithm:** Manual Apriori with candidate generation/pruning, support filtering, and rule creation using confidence + lift.
- **Results:** 9 frequent itemsets and 8 association rules produced at the default thresholds. Strongest rule: `Eggs -> Milk` (lift 2.0).
- **Challenges & improvements:**
  - No external libraries allowed, so CSV/JSON handling and reporting are implemented with the Python standard library.
  - Future work: parameterize thresholds via Airflow variables, add trend comparison across daily batches, and visualize support over time.

## Deliverables Checklist
- [x] Airflow DAG (`dags/apriori_pipeline_dag.py`)
- [x] Python scripts (loading/cleaning, Apriori, reporting)
- [x] Sample data and generated outputs
- [x] README with architecture diagram and short report

# EUR-Lex Use Cases

This section showcases practical examples of how to use `bulletin-fetcher` to query and analyze acts from the Official Journal of the European Union.

## Overview

All use cases leverage the `EurlexBulletinClient` to query the EUR-Lex SPARQL endpoint and retrieve official acts with different filtering criteria. The examples demonstrate how to:

- Query acts by date range, keywords, institution, and language
- Export results to DataFrames for data analysis
- Visualize temporal trends and institutional patterns
- Generate reproducible datasets for research

---

## Case 1: Temporal Evolution of Acts on Artificial Intelligence

**File**: `scripts/use_cases/case_1_ai_evolution.ipynb`

Tracks legislative activity on Artificial Intelligence over a 9-year period (2017-2026) by querying acts from the Official Journal and visualizing their monthly distribution as a time-series chart. This helps identify when AI-related legislation peaked in the EU.

**Run**: Open the notebook and execute the cells to query the EUR-Lex endpoint and generate the temporal trend chart.

---

## Case 2: Institutional Comparison

**File**: `scripts/use_cases/case_2_institution_comparison.ipynb`

Compares the legislative output across different EU institutions by analyzing all acts published in a specific year (2025). Generates a bar chart ranking the top institutions by the number of acts issued, revealing which institutions are most active in legislative activity.

**Run**: Open the notebook and execute the cells to retrieve institutional statistics and generate the ranking chart.

---

## Case 3: Reproducible Dataset

**File**: `scripts/use_cases/case_3_reproducible_dataset.py`

Generates a reproducible dataset of EU acts for research purposes. Queries acts mentioning "disease" in the title (2017-2023) and exports them to CSV format. Any researcher running this script will obtain identical results, ensuring reproducibility of studies and analyses.

The generated CSV includes metadata: CELEX URI, title, publication date, category, and issuing institution.

**Run**:

```bash
python scripts/use_cases/case_3_reproducible_dataset.py
```

This produces `dataset_eu_disease_acts_2017_2023.csv` in the same directory.

---

## Case 4: Analyzing Tariff-Related Acts in the EU Official Journal

**File**: `scripts/use_cases/case_4_tariff_analysis.ipynb`

Performs an in-depth analysis of tariff-related legislation (2023-2025) using NLP techniques. Queries acts containing "tariff" and analyzes their distribution by category, then extracts geopolitical entities (countries, regions) mentioned in the act descriptions using the spaCy library to identify which countries/regions are most frequently referenced in EU tariff legislation.

Generates multiple visualizations and detailed statistics about tariff acts and their referenced entities.

**Run**: Open the notebook and execute the cells to retrieve tariff acts, generate category charts, and extract entity references.

---

## Running the Examples

### Prerequisites

Install the required dependencies:

```bash
pip install bulletin-fetcher[all]
```

### Execution

**For Case 3 (Python script)**:

```bash
cd scripts/use_cases
python case_3_reproducible_dataset.py
```

**For Cases 1, 2, and 4 (Jupyter notebooks)**:

1. Open the notebook in Jupyter Lab or Jupyter Notebook.
2. Execute the cells sequentially to run the queries and generate the visualizations.

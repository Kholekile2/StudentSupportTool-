# Student Support Insights Tool

An AI-enabled tool that helps programme staff identify which learners need support and which communities are not yet being reached — so that support can be offered early and recruitment can be extended to those most under-represented.

Built as the integrated final assignment for the Future-Innovation Lab (SFIA Level 3), the tool answers two questions about a programme of learners:

- **Who is struggling among the learners we already serve?**
- **Which communities are we not reaching at all?**

The tool is designed so that identifying a learner's need triggers **support**, not **judgement** — every signal it surfaces is paired with a concrete supportive action.

---

## Built with

- **Python 3.11**
- **Streamlit** — the prototype UI framework
- **pandas** — data manipulation and validation
- **Plotly** — interactive charts
- **pytest** — automated testing

A full list with pinned versions is in `requirements.txt`.

---

## What the tool does

| Page | What it does |
|---|---|
| **Dashboard** | Aggregate view. 4 colour-coded KPIs, 8 filters (slicers), 6 charts organised in three story rows: Reach, Struggle, Voice. No individual learners are named on this page. |
| **Learner Detail** | Individual view. Pick one learner, see their profile, the suggested support actions (always paired with reasons), and an accountability form to record what was done. |
| **About** | Embedded ethics statement — what the tool will and will not do, POPIA alignment, the route a learner can take to challenge a decision. |

---

## Project structure

```
StudentSupportTool/
├── app.py                       # The Dashboard page (main entry)
├── pages/
│   ├── 1_Learner_Detail.py      # Individual learner view
│   └── 2_About.py               # Embedded ethics statement
├── utils/
│   ├── data_loader.py           # Single entry point for all data + validation
│   └── recommendations.py       # Rule-based suggestion engine
├── data/
│   └── learners.csv             # Synthetic SA learner dataset (51 rows)
├── tests/
│   └── test_data_loader.py      # 8 pytest test cases
├── bug_log.md                   # 4 documented bugs found during testing
├── requirements.txt             # Pinned dependency versions
├── .gitignore                   # Files not committed to Git
└── README.md                    # This file
```

---

## How to run the tool

### 1. Clone the repository

```
git clone https://github.com/Kholekile2/StudentSupportTool-.git
cd StudentSupportTool-
```

### 2. Create and activate a Python virtual environment

On **Windows (PowerShell)**:
```
python -m venv venv
venv\Scripts\Activate.ps1
```

On **macOS / Linux**:
```
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### 3. Install the dependencies

```
pip install -r requirements.txt
```

### 4. Run the app

```
streamlit run app.py
```

Your default browser will open at `http://localhost:8501`. If it does not open automatically, paste that address into a browser manually.

### 5. To stop the app

Press `Ctrl + C` in the terminal.

---

## How to use the tool

### Browse the dashboard

- The dashboard loads with the full synthetic dataset of 51 learners.
- Use the **sidebar filters** to narrow the view by age, area, province, device access, internet, employment, confidence band, or attendance risk.
- The four **KPIs** at the top update as you filter:
  - 🔵 Learners in view
  - 🔴 High attendance risk %
  - 🟠 Phone-only access %
  - 🟢 Provinces reached
- Click **Reset all filters** to clear everything.

### Upload your own data

In the sidebar, use the **Upload new data** uploader to load a different CSV. The file must follow the same schema as the default dataset (see Data Dictionary in the appendices). If a required column is missing, the tool will fail loudly with a message naming the missing columns — it will not guess.

### Look at an individual learner

- Navigate to **Learner Detail** in the sidebar.
- Pick a learner ID from the dropdown.
- The page surfaces:
  - **What the learner said they need** (their own voice, always first)
  - **Suggested support actions** with reasons and priority
  - **Profile** paired with support implications (never raw signals)
  - **Confidence and risk bands** paired with suggested responses
  - **Data quality notes** for the specific learner, if any
- Use the **Record what was done** form to log any action taken. This is the accountability step from the to-be process diagram, made real.

### Read the ethics statement

The **About** page explains in plain language what the tool will and will not do, how it aligns with POPIA, and how a learner can challenge a decision based on it.

---

## How to run the tests

From the project root, with the virtual environment active:

```
pytest -v
```

You should see 8 tests pass in under a second. The test suite covers:
- Confidence-band derivation logic
- Validation of duplicate IDs, invalid provinces, out-of-range scores
- Design rules: every learner receives at least one suggestion; the learner's stated need always appears first.

Tests 7 and 8 are **design-rule tests** — they enforce ethical design rules in code, not just in policy. If any of those rules is broken in a future change, the test fails.

---

## Known limitations

- **Schema-bound.** Uploaded CSVs must match the column names in the data dictionary. Differently-named columns or different value spellings (e.g. "KZN" vs "KwaZulu-Natal") would need a normalisation step before upload.
- **In-session memory.** Actions recorded on the Learner Detail page persist for the current browser session only. A production deployment would persist these to a database.
- **Synthetic data only.** The dataset is fully synthetic. No real learners are represented. A production deployment requires real intake data, real consent, and legal review.
- **No machine learning.** The recommendation engine is rule-based by design — every suggestion is traceable to a specific rule in `utils/recommendations.py`. This is for transparency and auditability, not because ML would have been infeasible.

---

## Project context

This tool was built as the SFIA Level 3 integrated final assessment, demonstrating six skills together:

| Skill | Where it is evidenced |
|---|---|
| **AIDE** — AI & Data Ethics | About page, design rules enforced in code, this README's limitations section |
| **BSMO** — Business Modelling | Stakeholder map, value proposition (in the integrated report) |
| **BPRE** — Process Improvement | As-is and to-be process diagrams (in the integrated report) |
| **PROG** — Programming | The full Streamlit prototype, tests, bug log |
| **DAAN** — Data Analytics | Dashboard charts, insights, data dictionary, synthetic dataset |
| **METL** — Methods & Tools | Tools list, Git history, project structure, this README |

The full integrated report is available in the project submission.

---

## Author

Kholekile — Future-Innovation Lab intern, Cohort 5, 2026.

---

## Repository

[github.com/Kholekile2/StudentSupportTool-](https://github.com/Kholekile2/StudentSupportTool-)
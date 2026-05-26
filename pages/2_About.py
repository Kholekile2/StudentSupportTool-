"""
2_About.py
-----------
In-app ethics, privacy, and accountability statement.

This page is the consolidated AIDE artefact embedded in the tool.
It tells anyone using the tool, in plain language:
  - what the tool does and doesn't do
  - what it refuses to automate
  - who is accountable
  - what laws apply
  - how to challenge or correct a decision
"""

import streamlit as st


st.set_page_config(
    page_title="About — Student Support Insights Tool",
    page_icon="ℹ️",
    layout="wide",
)


st.title("ℹ️ About this tool")
st.caption("Ethics, privacy, accountability — read this before relying on the tool.")


# ====== WHAT THIS TOOL IS FOR ======
st.subheader("What this tool is for")
st.markdown(
    """
    The Student Support Insights Tool helps programme staff identify learners
    who may benefit from support, using data that learners themselves provided
    at intake. It answers two questions:

    - **Who is struggling among the learners we already serve?** — so support
      can be offered early, before disengagement.
    - **Which communities are we not reaching?** — so recruitment can extend
      the opportunity to under-represented areas.

    The tool's purpose is to make support *flow toward* learners. It is not a
    risk-scoring system that ranks learners for prioritisation. A flag on this
    tool is a prompt to a human, not a verdict on a person.
    """
)


# ====== WHAT THIS TOOL WILL NOT DO ======
st.subheader("What this tool will not do")
st.markdown(
    """
    These are firm boundaries, enforced in the design and the code:

    - **It will not make decisions about a learner.** Every flag, score, or
      suggestion routes to a human (the support coordinator) who decides what
      to do. The tool informs; humans decide.
    - **It will not display a risk indicator without a paired support action.**
      Every signal on the Learner Detail page comes with a concrete next step.
      No naked numbers, no orphan flags.
    - **It will not single out individuals on the dashboard.** Only aggregates
      appear on the dashboard view. Individual learners are visible only on
      their dedicated detail page, intentionally separated.
    - **It will not silently drop or "clean" bad data.** Data quality issues
      (out-of-range scores, duplicate IDs, invalid entries) are surfaced
      explicitly, so a human can verify before acting on them.
    - **It will not infer beyond what the rules define.** The recommendation
      logic is rule-based and fully readable in `utils/recommendations.py`.
      There is no machine learning model in this tool — by design, so every
      suggestion is auditable.
    """
)


# ====== WHAT MUST NOT BE AUTOMATED ======
st.subheader("What must not be automated")
st.markdown(
    """
    The brief explicitly asks where human review is required. These actions
    must never be taken by the tool alone:

    - **Deciding whether a learner stays in or leaves the programme.** The tool
      does not produce dismissal or retention recommendations.
    - **Allocating limited resources between learners.** The tool can highlight
      where support is needed, but the prioritisation between learners must be
      made by a human who can hold context the tool cannot see.
    - **Communicating with the learner about a flag.** Any conversation about a
      learner's support need is a human-to-human conversation, never an
      automated message generated from a flag.
    - **Acting on the "Unsure" response.** When a learner says they are unsure
      what they need, that is a request for a conversation — not a data point
      for the tool to infer from.
    """
)


# ====== ACCOUNTABILITY ======
st.subheader("Accountability")
st.markdown(
    """
    The tool includes a mandatory **"Record what was done"** step on every
    learner's detail page. A flag cannot be noticed and then silently forgotten:
    every action taken (or explicitly not taken, with a reason) is logged.

    In production, this log is retained alongside the learner record and is
    visible to the next staff member who opens that learner's page. The absence
    of a recorded action against an old flag is itself a signal — it tells the
    next reviewer that follow-up may still be needed.

    The accountability log is also the mechanism by which a learner can
    challenge a decision: every flag carries an evidence trail of what was
    inferred, why, and what was done about it.
    """
)


# ====== DATA HANDLING & POPIA ======
st.subheader("Data handling and POPIA")
st.markdown(
    """
    The dataset used in this prototype is **fully synthetic** — no real
    learners are represented. In production, learner data would be personal
    information governed by the **Protection of Personal Information Act
    (POPIA, South Africa)**.

    The tool's design respects POPIA in the following concrete ways:

    - **Minimal collection.** Only the columns defined in the data dictionary
      are used. The dictionary is the consent boundary — any new column would
      require explicit justification and re-consent.
    - **Anonymous identifiers.** Learners are referenced by a system-generated
      ID, not by name. The ID lets support be tracked over time without
      requiring the system to know who the person is.
    - **Aggregate by default.** Dashboard views never name individuals.
      Individual views are on a separate page, accessed deliberately.
    - **Honest data quality reporting.** A learner has a right to know how
      their data is being used. The data quality panel makes any issues with
      their specific record visible to staff before any action is taken.
    """
)


# ====== LIMITATIONS ======
st.subheader("Limitations of this prototype")
st.markdown(
    """
    Honest reporting of what the prototype does *not* yet do:

    - **Schema-bound.** The validation rules generalise across new datasets
      that match our data dictionary's schema — but a dataset with different
      column names, different value spellings (e.g. "KZN" vs "KwaZulu-Natal"),
      or new categories of data quality issues would require updates to the
      dictionary and the validator.
    - **In-session memory only.** Recorded actions persist only for the
      current browser session. A production deployment would persist them to
      a database.
    - **Small sample sizes are noisy.** Some charts use bands of n<5 or n<10
      learners. Sample-size honesty is built into the visualisations (lighter
      bars, caption warnings), but no chart on this tool should be read as
      a verdict where the sample is small.
    - **Synthetic data only.** The patterns in the prototype's dataset reflect
      realistic SA learner demographics by design, but they are not real
      learners. Production deployment requires real intake data, real consent,
      and real legal review.
    """
)


# ====== CONTACT / CHALLENGE ======
st.subheader("Challenging a decision")
st.markdown(
    """
    If a learner believes a flag against them is incorrect, or that they have
    been treated unfairly by an outcome influenced by this tool, the route is:

    1. Request the data quality report for their record from the support
       coordinator — every input that contributed to a suggestion is visible.
    2. Request the accountability log for their record — every action taken,
       and when, is logged.
    3. Correct any incorrect input at the source (intake survey or follow-up
       conversation). The tool re-runs its rules on corrected data and updates
       the suggestions.

    The tool is designed so that every suggestion is traceable to a specific
    rule applied to a specific data point. Nothing is hidden in a model that
    cannot be explained.
    """
)


# ====== CREDITS ======
st.divider()
st.caption(
    "Student Support Insights Tool — Future-Innovation Lab integrated assignment. "
    "Built as a prototype to demonstrate responsible identification of learner "
    "support needs."
)
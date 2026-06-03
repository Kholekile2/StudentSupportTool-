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
    who might benefit from support, based on information they shared at intake.
    It answers two questions:

    - **Who is struggling?** — so support can start early, before they disengage.
    - **Who are we not reaching?** — so recruitment can extend to underrepresented areas.

    Think of it as a **prompt to human judgment**, not an automated verdict. A flag on this
    tool means "look into this", not "this is definite".
    """
)


# ====== GUARDRAILS ======
st.subheader("What stays human")
st.markdown(
    """
    Some decisions always need a person. This tool will never:

    - **Decide a learner's place in the programme.** No dismissal or retention calls from automation.
    - **Rank learners against each other for resources.** The tool can say where support might help; humans decide who needs it most.
    - **Message a learner directly.** Any conversation with a learner happens person-to-person, not from an automated system.
    - **Act on an I'm unsure response.** When someone says they don't know what they need, that's a conversation starter, not data to be interpreted.
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


# ====== DATA & PRIVACY ======
st.subheader("Data and privacy")
st.markdown(
    """
    **This prototype uses fully synthetic data** — no real learners.
    When real data is used, it is governed by POPIA (Protection of Personal Information Act).

    We respect privacy by:
    - Using only data that learners consented to share at intake.
    - Identifying learners by ID, not name.
    - Never showing individual names on the dashboard — only grouped trends.
    - Surfacing data quality issues (wrong entries, odd values) so staff can verify them before using them.
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
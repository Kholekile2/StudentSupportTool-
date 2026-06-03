"""
1_Learner_Detail.py
--------------------
Individual learner view — pick one learner, see their profile,
suggested support actions, and record what was done.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.recommendations import recommend_for_learner


# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Learner Detail — Student Support Insights Tool",
    page_icon="👤",
    layout="wide",
)

# ====== AGREEMENT GUARD ======
# This page handles individual, named learners — the most ethically sensitive
# view in the tool. Refuse to render until the user has agreed on the
# Dashboard. Streamlit shares session state across pages, so the check is
# simple: if they agreed elsewhere, they're agreed here too.
if not st.session_state.get("user_agreed", False):
    st.title("👤 Learner Detail")
    st.warning(
        "⚠️ This page handles personal information about individual learners. "
        "Please open the **app** (Dashboard) page first and agree to the "
        "Responsible Use Agreement before viewing any learner."
    )
    st.info(
        "If you have not yet read the agreement, the **About** page in the "
        "sidebar explains the tool's ethics commitments — no agreement is "
        "required to read it."
    )
    st.stop()

# Show the session-identity banner so the user knows they're attributed.
st.caption(f"👤 Session: **{st.session_state['user_identifier']}**")

st.title("👤 Learner Detail")
st.caption(
    "Individual view — one learner at a time."
)


# ====== LOAD DATA ======
# Same data loader as the dashboard — validation is enforced here too.
try:
    df, report = load_data("data/learners.csv")
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()


# ====== LEARNER PICKER ======
# Dropdown to select one learner. Sorted by ID for predictable navigation.
learner_ids = sorted(df["learner_id"].dropna().unique().tolist())
if not learner_ids:
    st.warning("No learners in the dataset.")
    st.stop()

# Use a small text input for quick search alongside the dropdown.
col_picker, col_search = st.columns([2, 1])
with col_picker:
    selected_id = st.selectbox("Select a learner", learner_ids, key="learner_select")
with col_search:
    st.caption(f"{len(learner_ids)} learners available")


# ====== FETCH THE SELECTED LEARNER ======
# A learner_id might appear more than once (e.g. L013 is a deliberate duplicate).
# We fetch ALL matching rows and tell the user honestly if there are multiple.
matching_rows = df[df["learner_id"] == selected_id]
if len(matching_rows) > 1:
    st.warning(
        f"⚠️ {len(matching_rows)} rows share ID `{selected_id}`. "
        "This is a data quality issue — a human should verify which record is correct. "
        "Showing the first record below."
    )
learner = matching_rows.iloc[0].to_dict()  # take first row as a dict


# ====== LEARNER'S OWN VOICE — shown FIRST, always ======
# The single most important design rule: what the learner SAID they need
# appears before any signal the system inferred about them.
st.divider()
st.subheader("🗣️ What this learner said they need")

declared_need = learner.get("support_need")
if declared_need and str(declared_need) not in ("", "None right now", "Unsure", "nan"):
    st.success(f"**Stated support need:** {declared_need}")
    st.caption("This was the learner's own answer at intake. Address it before anything else.")
elif str(declared_need) == "Unsure":
    st.info(
        "The learner answered **'Unsure'** at intake. "
        "This is not a non-answer — it is a request for a conversation. "
        "Schedule a check-in before relying on inferred recommendations."
    )
else:
    st.info("The learner did not provide a stated support need.")


# ====== INFERRED RECOMMENDATIONS ======
st.subheader("💡 Suggested support actions")
st.caption("Each suggestion shows its reason, based on intake data.")

suggestions = recommend_for_learner(learner)

# Priority colour map — visual priority, not urgency-shaming.
priority_colors = {"high": "🔴", "medium": "🟠", "low": "🟢"}

for s in suggestions:
    icon = priority_colors.get(s["priority"], "⚪")
    with st.container(border=True):
        st.markdown(f"### {icon} {s['action']}")
        st.caption(f"**Why:** {s['reason']}  |  **Priority:** {s['priority']}")


# ====== LEARNER PROFILE — paired data ======
# Every signal shown here is accompanied by what it MEANS for support.
# No naked numbers. Every cell has context.
st.divider()
st.subheader("📋 Learner profile")
st.caption("Each data point is shown with what it means for support, never as a bare number.")

# Two-column layout: facts on the left, support implications on the right.
prof_col1, prof_col2 = st.columns([1, 1])

with prof_col1:
    st.markdown("**Demographics**")
    age = learner.get("age_band") or "—"
    province = learner.get("province") or "—"
    area = learner.get("area_type") or "—"
    st.write(f"Age band: **{age}**")
    st.write(f"Province: **{province}**")
    st.write(f"Area type: **{area}**")

    st.markdown("**Resources**")
    device = learner.get("device_access") or "—"
    internet = learner.get("internet_access") or "—"
    employment = learner.get("employment_status") or "—"
    st.write(f"Device access: **{device}**")
    st.write(f"Internet access: **{internet}**")
    st.write(f"Employment: **{employment}**")

with prof_col2:
    st.markdown("**What this means for support**")
    notes = []
    if device == "Phone only":
        notes.append("📱 Phone-only access → device loan would help.")
    if internet in ("Unstable", "Limited"):
        notes.append(f"📶 {internet} internet → data bundle + offline resources.")
    if employment == "Full-time":
        notes.append("💼 Full-time work → evening sessions + recorded materials.")
    if area == "Rural":
        notes.append("🌾 Rural location → offline-first study options matter more.")
    if not notes:
        notes.append("No specific resource flags. Check in to confirm.")
    for n in notes:
        st.write(n)


# ====== CONFIDENCE & RISK — paired with action ======
st.divider()
st.subheader("📊 Confidence & risk")
st.caption(
    "These are self-reported and inferred signals. Each is shown with a suggested "
    "response — never as a bare score that invites judgement."
)

# Three confidence columns + attendance risk.
rk_col1, rk_col2, rk_col3, rk_col4 = st.columns(4)

def _band_with_action(label, band, low_action, high_action_msg="Strength to build on."):
    """Helper to render a confidence band with a paired action message."""
    if band is None or pd.isna(band) or band == "":
        return f"{label}\n\n*(no data)*"
    if band == "Low":
        return f"{label}\n\n**Low**  →  {low_action}"
    if band == "Medium":
        return f"{label}\n\n**Medium**  →  Scaffolded practice in this area."
    if band == "High":
        return f"{label}\n\n**High**  →  {high_action_msg}"
    return f"{label}\n\n*(invalid score — see data quality notes)*"

with rk_col1:
    st.info(_band_with_action(
        "**Digital confidence**",
        learner.get("digital_confidence_band"),
        "Foundational digital literacy first.",
    ))
with rk_col2:
    st.info(_band_with_action(
        "**Programming confidence**",
        learner.get("programming_confidence_band"),
        "Pair with peer mentor for first 4 weeks.",
    ))
with rk_col3:
    st.info(_band_with_action(
        "**AI confidence**",
        learner.get("ai_confidence_band"),
        "Introduce AI basics in a low-stakes session.",
    ))
with rk_col4:
    risk = learner.get("attendance_risk")
    if risk == "High":
        st.error(f"**Attendance risk**\n\n**High**\n\nProactive contact within 1 week.")
    elif risk == "Medium":
        st.warning(f"**Attendance risk**\n\n**Medium**\n\nCheck-in within 2 weeks.")
    elif risk == "Low":
        st.success(f"**Attendance risk**\n\n**Low**\n\nLight-touch check-in.")
    else:
        st.info(f"**Attendance risk**\n\n*(no data)*")


# ====== DATA QUALITY FLAGS FOR THIS LEARNER ======
# Honest reporting of anything wrong with this specific row.
quality_flags = []
if selected_id in report["duplicate_ids"]:
    quality_flags.append(f"⚠️ This learner ID appears in {len(matching_rows)} rows — duplicate.")
for issue in report["out_of_range_confidence"]:
    if issue["learner_id"] == selected_id:
        quality_flags.append(
            f"⚠️ Out-of-range value: `{issue['column']}` = {issue['value']} (valid range 1–5)."
        )
for issue in report["invalid_province"]:
    if issue["learner_id"] == selected_id:
        quality_flags.append(f"⚠️ Invalid province entry: `{issue['value']}`.")

if quality_flags:
    st.divider()
    st.subheader("⚠️ Data quality notes for this learner")
    for flag in quality_flags:
        st.warning(flag)
    st.caption(
        "Verify these fields with the learner before acting on recommendations."
    )


# ====== ACCOUNTABILITY: RECORD WHAT WAS DONE ======
st.divider()
st.subheader("✅ Record what was done")
st.caption(
    "Log every action taken — so follow-up isn't forgotten."
)

with st.form(key=f"action_form_{selected_id}", clear_on_submit=True):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        action_taken = st.selectbox(
            "Action taken",
            [
                "Device loan offered",
                "Data bundle arranged",
                "Mentor pairing scheduled",
                "Check-in conversation held",
                "Evening/flexible scheduling arranged",
                "Referred to external support",
                "Other (see notes)",
            ],
        )
    with f_col2:
        action_date = st.date_input("Date")
    notes = st.text_area("Notes (what was offered, learner's response, next step)", height=80)
    submitted = st.form_submit_button("Record action")

    if submitted:
        # In a real deployment this would persist to a database.
        # For the prototype we store it in session_state so the demonstration is visible.
        if "action_log" not in st.session_state:
            st.session_state["action_log"] = []
        st.session_state["action_log"].append({
            "learner_id": selected_id,
            "action": action_taken,
            "date": str(action_date),
            "notes": notes,
        })
        st.success(f"Recorded for {selected_id}: {action_taken} on {action_date}.")

# Show history of recorded actions for this learner.
if "action_log" in st.session_state:
    history = [a for a in st.session_state["action_log"] if a["learner_id"] == selected_id]
    if history:
        st.markdown("**Actions recorded (this session):**")
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)


# ====== FOOTER ======
st.divider()
st.caption(
    "Designed so that identifying a learner's need triggers support, not judgement — "
    "and so the helping path is the easiest path."
)
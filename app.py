"""
app.py
-------
Student Support Insights Tool — Dashboard page.

Run with:  streamlit run app.py

What this page does:
  - Shows headline KPIs about who the programme is serving
  - Lets staff filter by province, area type, and risk band (slicers)
  - Renders six dashboard charts, organised in a single-screen grid
  -- Tells the story of enrolled learners primarily — who they are, where
    confidence and risk concentrate, and what they themselves are asking
    for. Surfaces reach gaps as a secondary signal.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data, VALID_PROVINCES, VALID_AREA_TYPES


# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Student Support Insights Tool",
    page_icon="🎓",
    layout="wide",
)

# ====== ETHICS & AGREEMENT GATE ======
# This gate enforces consent architecturally — until the user agrees, no data
# renders. The agreement is per-session and binding: the user identifies
# themselves and acknowledges accountability for misuse. Per-session means the
# user re-acknowledges each time the app is opened — "you agreed once forever"
# is consent theatre, not consent.
if "user_agreed" not in st.session_state:
    st.session_state["user_agreed"] = False
if "user_identifier" not in st.session_state:
    st.session_state["user_identifier"] = ""

if not st.session_state["user_agreed"]:
    st.title("🎓 Student Support Insights Tool")
    st.subheader("Before you continue — Responsible Use Agreement")
    st.markdown(
        """
        This tool is being used in a prototype with synthetic data. In real
        deployment, it will work with **real personal information about real
        learners** — protected by the Protection of Personal Information Act
        (POPIA, South Africa).

        Before continuing, please read the following carefully. You are not
        clicking through a banner — you are entering into a binding
        responsible-use commitment with the programme.
        """
    )

    st.markdown("#### What you are agreeing to")
    st.markdown(
        """
        1. **The data is real and protected.** Even where the prototype uses
           synthetic data, the production system will hold real personal
           information about real learners. I will treat all data accessed
           through this tool as personal information, regardless of whether
           it is currently synthetic or real.

        2. **The data may not be misused.** I will not copy, share, screenshot,
           export, or otherwise remove learner data for any purpose outside
           the support of the learners themselves. The export feature is for
           legitimate programme purposes only.

        3. **Misuse has consequences.** I understand that misuse of learner
           data — including sharing it outside authorised channels, using it
           to disadvantage a learner, or accessing it without a legitimate
           need — may constitute a breach of POPIA, may result in disciplinary
           action by the programme, and may carry legal consequences.

        4. **I am identifying myself.** By entering my name and role below,
           I am identifying myself as the person accountable for what is done
           with this tool in this session.

        5. **The tool is a prompt, not a decision-maker.** Every signal it
           surfaces is a prompt to a human decision. I will treat it as such.
           I will not use the tool to disadvantage, deprioritise, or remove
           any learner from the programme on the basis of a flag alone.

        6. **I will hear the learner first.** Where the learner has stated
           a need, I will hear that need before any signal the tool inferred
           about them.

        7. **I will record every action.** A flag without a recorded action
           is a learner forgotten. Every support action I take (or explicitly
           do not take, with a reason) will be logged on the learner's
           detail page.

        8. **I understand the spirit of the tool.** This tool is designed so
           that identifying a learner's need triggers **support**, not
           **judgement**. I commit to using it in that spirit.
        """
    )

    st.divider()
    st.markdown("#### Please identify yourself")
    st.caption(
        "Your name and role are logged with this session. This is the "
        "accountability layer — anonymity is not appropriate when working "
        "with personal data."
    )

    name_col, role_col = st.columns(2)
    with name_col:
        user_name = st.text_input(
            "Your full name",
            key="agreement_name",
            placeholder="e.g. Thandi Mokoena",
        )
    with role_col:
        user_role = st.text_input(
            "Your role",
            key="agreement_role",
            placeholder="e.g. Support Coordinator",
        )

    confirm = st.checkbox(
        "I have read and understood every clause above, and I agree to be "
        "bound by them for the duration of this session.",
        key="agreement_checkbox",
    )

    st.divider()
    agree_col1, agree_col2 = st.columns([1, 4])
    with agree_col1:
        ready_to_agree = bool(user_name.strip()) and bool(user_role.strip()) and confirm
        if st.button(
            "I agree — continue",
            type="primary",
            use_container_width=True,
            disabled=not ready_to_agree,
        ):
            st.session_state["user_agreed"] = True
            st.session_state["user_identifier"] = f"{user_name.strip()} ({user_role.strip()})"
            st.rerun()
    with agree_col2:
        if not ready_to_agree:
            st.caption(
                "⚠️ You must enter your name, your role, and tick the "
                "confirmation box before you can continue."
            )
        else:
            st.caption("Click the button to enter the tool.")

    # Allow people to read the full ethics statement without agreeing.
    st.divider()
    st.caption(
        "If you would like to read the full ethics statement before agreeing, "
        "open the **About** page in the sidebar — it does not require agreement."
    )

    st.stop()

# Once agreed: show a small banner identifying the current session user.
# This is the accountability surface — staff see who is "signed in" at all
# times, so the user is reminded their actions are attributed to them.
st.caption(f"👤 Session: **{st.session_state['user_identifier']}**")


# ====== HEADER ======
st.title("🎓 Student Support Insights Tool")
st.caption(
    "Aggregate view — no individual learners are named here. "
    "This dashboard helps the programme understand its enrolled learners — "
    "who they are, where confidence and risk concentrate, and what they themselves "
    "are asking for. As a secondary signal, gaps in reach are also visible."
)


# ====== SIDEBAR — privacy notice + slicers (filters) ======
with st.sidebar:
    st.header("🔍 Filters")
    st.caption("Narrow the view to a specific group. Filters combine — selecting Eastern Cape + Township shows only learners matching both.")

    # ----- Group 1: WHO ARE THEY? -----
    st.markdown("**Who are they?**")
    g1c1, g1c2 = st.columns(2)
    with g1c1:
        selected_age = st.selectbox("Age band", ["All ages", "18-21", "22-25", "26-30", "31+"], key="age_filter")
    with g1c2:
        selected_area = st.selectbox("Area type", ["All area types"] + sorted(VALID_AREA_TYPES), key="area_filter")
    selected_province = st.selectbox("Province", ["All provinces"] + sorted(VALID_PROVINCES), key="prov_filter")

    st.markdown("**What do they have?**")
    g2c1, g2c2 = st.columns(2)
    with g2c1:
        selected_device = st.selectbox(
            "Device access",
            ["All devices", "Phone only", "Phone + shared laptop", "Own laptop"],
            key="device_filter",
        )
    with g2c2:
        selected_internet = st.selectbox(
            "Internet access",
            ["All internet", "Stable", "Limited", "Unstable"],
            key="net_filter",
        )
    selected_employment = st.selectbox(
        "Employment status",
        ["All employment", "Unemployed", "Part-time", "Full-time", "Studying"],
        key="emp_filter",
    )

    st.markdown("**How are they doing?**")
    g3c1, g3c2 = st.columns(2)
    with g3c1:
        selected_confidence = st.selectbox(
            "Digital confidence band",
            ["All bands", "Low", "Medium", "High"],
            key="conf_filter",
        )
    with g3c2:
        selected_risk = st.selectbox(
            "Attendance risk",
            ["All risk bands", "High", "Medium", "Low"],
            key="risk_filter",
        )

    # Reset button — uses a callback so session_state can be modified BEFORE
    # the widgets are re-instantiated on the next run. Writing to a widget's
    # session_state key after the widget exists raises StreamlitAPIException.
    def _reset_all_filters():
        st.session_state["age_filter"] = "All ages"
        st.session_state["area_filter"] = "All area types"
        st.session_state["prov_filter"] = "All provinces"
        st.session_state["device_filter"] = "All devices"
        st.session_state["net_filter"] = "All internet"
        st.session_state["emp_filter"] = "All employment"
        st.session_state["conf_filter"] = "All bands"
        st.session_state["risk_filter"] = "All risk bands"

    st.button("Reset all filters", use_container_width=True, on_click=_reset_all_filters)

    st.divider()
    st.markdown("### 📤 Upload new data")
    uploaded_file = st.file_uploader(
        "Upload a learner CSV",
        type=["csv"],
        help="Must follow the same column structure as the default dataset. "
             "Any data quality issues will be flagged on the dashboard.",
    )
    if uploaded_file is not None:
        st.success(f"Loaded {uploaded_file.name}")
    else:
        st.caption("Using default synthetic dataset.")

    st.divider()
    st.markdown("### ℹ️ Privacy")
    st.caption(
        "All data shown is synthetic. In production this tool would be governed "
        "by POPIA. The tool never displays a risk indicator without a suggested "
        "support action — individual recommendations live on the Learner Detail page."
    )


# ====== LOAD DATA ======
# If the user uploaded a file, use that. Otherwise fall back to the default.
data_source = uploaded_file if uploaded_file is not None else "data/learners.csv"
try:
    df_all, report = load_data(data_source)
except (FileNotFoundError, ValueError) as e:
    st.error(f"❌ {e}")
    st.info(
        "The tool needs a CSV with these columns: learner_id, age_band, province, "
        "area_type, device_access, internet_access, digital_confidence, "
        "programming_confidence, ai_confidence, employment_status, support_need, "
        "attendance_risk."
    )
    st.stop()


# ====== APPLY FILTERS ======
# Start from the full dataset, narrow based on slicer selections.
df = df_all.copy()
if selected_age != "All ages":
    df = df[df["age_band"] == selected_age]
if selected_area != "All area types":
    df = df[df["area_type"] == selected_area]
if selected_province != "All provinces":
    df = df[df["province"] == selected_province]
if selected_device != "All devices":
    df = df[df["device_access"] == selected_device]
if selected_internet != "All internet":
    df = df[df["internet_access"] == selected_internet]
if selected_employment != "All employment":
    df = df[df["employment_status"] == selected_employment]
if selected_confidence != "All bands":
    df = df[df["digital_confidence_band"] == selected_confidence]
if selected_risk != "All risk bands":
    df = df[df["attendance_risk"] == selected_risk]

# Detect whether any filter is active.
filter_active = any([
    selected_age != "All ages",
    selected_area != "All area types",
    selected_province != "All provinces",
    selected_device != "All devices",
    selected_internet != "All internet",
    selected_employment != "All employment",
    selected_confidence != "All bands",
    selected_risk != "All risk bands",
])


# ====== KPI ROW ======
# Headline numbers — "at a glance, how are we doing?"
# Each KPI is wrapped in a coloured container that signals its meaning:
#   blue   = neutral information
#   red    = needs attention (high risk)
#   orange = caution (structural issue)
#   green  = positive signal (reach / equity)
st.subheader("Programme at a glance")

total = len(df)
high_risk = (df["attendance_risk"] == "High").sum()
high_risk_pct = (high_risk / total * 100) if total else 0
phone_only = (df["device_access"] == "Phone only").sum()
phone_only_pct = (phone_only / total * 100) if total else 0
provinces_reached = df["province"][df["province"].isin(VALID_PROVINCES)].nunique()

# Helper to render a coloured KPI tile.
def _kpi_tile(label, value, sub, bg_color, text_color="#FFFFFF"):
    st.markdown(
        f"""
        <div style="background-color:{bg_color};padding:18px;border-radius:10px;text-align:center;">
            <div style="color:{text_color};font-size:14px;opacity:0.85;">{label}</div>
            <div style="color:{text_color};font-size:30px;font-weight:700;margin:4px 0;">{value}</div>
            <div style="color:{text_color};font-size:12px;opacity:0.85;">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    _kpi_tile("Learners in view", str(total), "total in current filter", "#2E5A87")
with kpi2:
    _kpi_tile("High attendance risk", f"{high_risk_pct:.0f}%", f"{high_risk} learners", "#C0392B")
with kpi3:
    _kpi_tile("Phone-only access", f"{phone_only_pct:.0f}%", f"{phone_only} learners", "#E67E22")
with kpi4:
    _kpi_tile("Provinces reached", f"{provinces_reached} / 9", "out of 9 SA provinces", "#27AE60")



# ====== EXPORT — download the data currently in view ======
# Exports the filtered subset (respects slicer state). By default we exclude
# the deliberate dirt — out-of-range scores and duplicate rows — so that
# downstream users of the export aren't misled. An opt-in checkbox lets a
# data steward export the raw view for auditing.
with st.expander("📥 Export this view"):
    raw_export = st.checkbox(
        "Include rows with data quality issues (out-of-range scores, duplicates)",
        value=False,
        help=(
            "Off by default. Turn on only if you are auditing data quality; "
            "the rows included are flagged in the data quality panel above."
        ),
    )

    if raw_export:
        df_to_export = df.copy()
    else:
        # Exclude rows flagged in the validation report.
        bad_ids = set(report["duplicate_ids"])
        bad_ids.update(issue["learner_id"] for issue in report["out_of_range_confidence"])
        bad_ids.update(issue["learner_id"] for issue in report["invalid_province"])
        df_to_export = df[~df["learner_id"].isin(bad_ids)].copy()

    csv_bytes = df_to_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download CSV ({len(df_to_export)} rows)",
        data=csv_bytes,
        file_name="learner_data_export.csv",
        mime="text/csv",
        use_container_width=False,
    )
    st.caption(
        "The export contains exactly the rows currently visible after filtering. "
        "Treat exported data with the same care as the source — it is still "
        "personal information."
    )



# ====== DATA QUALITY (compact) ======
# Same honesty as before, just compressed into one expandable line.
issue_count = (
    len(report["duplicate_ids"])
    + len(report["out_of_range_confidence"])
    + len(report["invalid_province"])
)
with st.expander(f"📋 Data quality — {issue_count} issues found across {report['total_rows']} loaded rows"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate IDs", len(report["duplicate_ids"]))
    c2.metric("Out-of-range values", len(report["out_of_range_confidence"]))
    c3.metric("Invalid provinces", len(report["invalid_province"]))
    if report["duplicate_ids"]:
        st.write("Duplicates:", report["duplicate_ids"])
    if report["out_of_range_confidence"]:
        st.write("Out-of-range:")
        st.dataframe(pd.DataFrame(report["out_of_range_confidence"]))
    if report["invalid_province"]:
        st.write("Invalid provinces:")
        st.dataframe(pd.DataFrame(report["invalid_province"]))

st.divider()


# ====== CHART ROW 1 — Reach: who we serve, who we don't ======
st.subheader("Reach — which communities are we serving?")
row1_col1, row1_col2 = st.columns(2)

# --- Chart 1A: Learners by province (the reach question) ---
with row1_col1:
    # Count every valid SA province, including zero counts for ones we miss.
    prov_counts = (
        df[df["province"].isin(VALID_PROVINCES)]["province"]
        .value_counts()
        .reindex(sorted(VALID_PROVINCES), fill_value=0)
    )
    fig = px.bar(
        x=prov_counts.values, y=prov_counts.index, orientation="h",
        labels={"x": "Number of learners", "y": "Province"},
        text=[str(v) for v in prov_counts.values],  # explicit string conversion, NaN-safe
    )
    fig.update_traces(textposition="outside", marker_color="#2E5A87")
    fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=30, b=10),
                      title="Learners by SA province")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Empty bars = provinces the programme is not reaching.")

# --- Chart 1B: Area type distribution ---
with row1_col2:
    area_counts = (
        df["area_type"].value_counts()
        .reindex(["Urban", "Township", "Rural"], fill_value=0)
    )
    fig = px.pie(
        values=area_counts.values, names=area_counts.index, hole=0.45,
        color=area_counts.index,
        color_discrete_map={"Urban": "#2E5A87", "Township": "#6294C0", "Rural": "#AFCAE0"},
    )
    fig.update_traces(textinfo="label+percent", textposition="outside")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                      title="Learners by area type",
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ====== CHART ROW 2 — Struggle: who needs support ======
st.subheader("Struggle — where are confidence and risk concentrated?")
row2_col1, row2_col2 = st.columns(2)

# --- Chart 2A: Average programming confidence by province ---
# This is the chart your value-proposition rewrite called for.
with row2_col1:
    df_prog = df[df["province"].isin(VALID_PROVINCES)].copy()
    df_prog["prog_num"] = pd.to_numeric(df_prog["programming_confidence"], errors="coerce")

    # BUG FIX #2: rename aggregated columns away from "mean"/"count" to avoid
    # collision with pandas method names under heavily filtered (small) subsets.
    by_prov = (
        df_prog.groupby("province")["prog_num"]
        .agg(avg_score="mean", n="count")
        .reset_index()
    )
    by_prov = by_prov[by_prov["n"] > 0]

    if len(by_prov) > 0:
        by_prov = by_prov.sort_values("avg_score")

        # BUG FIX #2 (cont'd): NaN-safe label construction.
        by_prov["label"] = by_prov.apply(
            lambda r: f"{r['avg_score']:.1f} (n={int(r['n'])})" if pd.notna(r["avg_score"]) else "",
            axis=1,
        )
        # Dim small-sample bars — sample-size honesty principle.
        by_prov["color"] = by_prov["n"].apply(lambda n: "#2E5A87" if n >= 5 else "#9BB5CC")

        fig = px.bar(
            by_prov, x="avg_score", y="province", orientation="h",
            labels={"avg_score": "Avg programming confidence (1–5)", "province": ""},
            text="label",
        )
        fig.update_traces(textposition="outside", marker_color=by_prov["color"])
        fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=30, b=10),
                          title="Programming confidence by province", xaxis_range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Lighter bars = small samples (n<5); read with caution.")
    else:
        st.info("No learners match the current filters for this chart.")

# --- Chart 2B: Attendance risk by device access ---
with row2_col2:
    device_order = ["Phone only", "Phone + shared laptop", "Own laptop"]
    risk_order = ["High", "Medium", "Low"]
    risk_colors = {"High": "#C0392B", "Medium": "#E67E22", "Low": "#27AE60"}

    risk_df = df[df["device_access"].isin(device_order) & df["attendance_risk"].isin(risk_order)].copy()
    if len(risk_df):
        ct = pd.crosstab(risk_df["device_access"], risk_df["attendance_risk"])
        ct = ct.reindex(index=device_order, columns=risk_order, fill_value=0)

        # BUG FIX: when a device category has 0 learners in the filtered view,
        # dividing by zero produces NaN. We compute row sums first and skip empty rows.
        row_sums = ct.sum(axis=1)
        # Replace 0 row sums with NaN (a float), divide, then fill NaN back to 0.
        # Using NaN (not pd.NA) keeps the column dtype as float throughout — no
        # extension-type / NAType conversions to trip over.
        safe_sums = row_sums.replace(0, float("nan"))
        ct_pct = (ct.div(safe_sums, axis=0) * 100).fillna(0.0)

        ct_long = ct_pct.reset_index().melt(id_vars="device_access", var_name="risk", value_name="percent")
        # BUG FIX: build the label without astype(int), which fails on any leftover NaN.
        ct_long["label"] = ct_long["percent"].round(0).map(lambda v: f"{int(v)}%" if pd.notna(v) else "")

        fig = px.bar(
            ct_long, x="device_access", y="percent", color="risk",
            color_discrete_map=risk_colors,
            category_orders={"risk": risk_order, "device_access": device_order},
            labels={"device_access": "Device access", "percent": "% of learners", "risk": "Risk"},
            text="label",
        )
        fig.update_traces(textposition="inside", textfont_color="white")
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                          title="Attendance risk by device access")
        st.plotly_chart(fig, use_container_width=True)

        # Helpful note when some device groups are empty in the current view.
        empty_groups = row_sums[row_sums == 0].index.tolist()
        if empty_groups:
            st.caption(f"No learners in the current view for: {', '.join(empty_groups)}.")
    else:
        st.info("No learners match the current filters.")

# ====== CHART ROW 3 — Voice & needs ======
st.subheader("Voice — what are learners themselves asking for?")
row3_col1, row3_col2 = st.columns(2)

# --- Chart 3A: Support needs (the learner's voice column) ---
with row3_col1:
    needs = df["support_need"].replace("", pd.NA).dropna()
    needs = needs[needs != "Unsure"]  # we visualise stated needs; "Unsure" gets called out separately
    need_counts = needs.value_counts()

    if len(need_counts):
        fig = px.bar(
            x=need_counts.values, y=need_counts.index, orientation="h",
            labels={"x": "Number of learners", "y": "Stated support need"},
            text=need_counts.values,
        )
        fig.update_traces(textposition="outside", marker_color="#27AE60")
        fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=30, b=10),
                          title="What learners said they need (their own voice)")
        st.plotly_chart(fig, use_container_width=True)
        unsure = (df["support_need"] == "Unsure").sum()
        st.caption(f"{unsure} learners replied 'Unsure' — they need a conversation, not an automated guess.")
    else:
        st.info("No support-need data matches the current filters.")

# --- Chart 3B: Digital confidence distribution ---
with row3_col2:
    band_order = ["Low", "Medium", "High"]
    band_colors = {"Low": "#C0392B", "Medium": "#E67E22", "High": "#27AE60"}
    band_counts = (
        df["digital_confidence_band"]
        .value_counts()
        .reindex(band_order, fill_value=0)
    )

    fig = px.pie(
        values=band_counts.values, names=band_counts.index, hole=0.45,
        color=band_counts.index, color_discrete_map=band_colors,
    )
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                      title="Digital confidence band distribution", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ====== FOOTER ======
st.divider()
st.caption(
    "Dashboard view — aggregate only. Individual learner views, with paired support "
    "recommendations, live on the Learner Detail page."
)
# Bug Log

## Bug #1 — IntCastingNaNError on small filter selections

**Discovered:** 25 May 2026, during dashboard testing.

**How it manifested:** When the user filtered the dashboard to a small subset
(e.g. Free State province, or Rural area type), the page crashed at the
"Attendance risk by device access" chart with `IntCastingNaNError: Cannot
convert non-finite values (NA or inf) to integer`.

**Root cause:** When a filter produced a subset in which one or more device
access categories had zero learners, the percentage calculation
`ct.div(ct.sum(axis=1))` performed 0÷0, producing NaN. The subsequent
`.astype(int)` call on the chart labels then failed because NaN cannot be
converted to an integer.

**Fix:** Two changes in app.py:
  1. Replaced row sums of 0 with pd.NA before division to prevent 0÷0.
  2. Built the chart labels using `.map(lambda v: f"{int(v)}%" if pd.notna(v) else "")`
     so NaN values produce an empty label instead of crashing the conversion.

**Defensive change:** Also hardened Chart 1A by converting province count
labels to strings explicitly, removing a similar latent risk.

**Verification:** Reproduced the bug with the Free State filter selected, applied
the fix, confirmed the chart now renders with a caption identifying empty
groups.


## Bug #2 — Aggregated DataFrame collapses under heavy filter combinations

**Discovered:** 25 May 2026, during sidebar slicer stress-testing.

**How it manifested:** Applying certain slicer combinations (e.g. Employment =
Part-time; Digital confidence = Medium; Internet = Stable; combinations of
device + risk) crashed Chart 2A with `ValueError: Cannot set a DataFrame
with multiple columns to the single column label`. The error did not appear
on first page load; it surfaced only under sufficiently narrow filters.

**Root cause:** Chart 2A used pandas `.agg(["mean", "count"])` which produces
columns literally named `mean` and `count`. Both are also names of built-in
pandas methods. Under small/empty subsets, the subsequent
`by_prov.apply(...)` returned a multi-column structure instead of a Series,
because of attribute-vs-column ambiguity. Assigning that multi-column
structure to a single column name (`by_prov["label"]`) raised the ValueError.

**Fix:** Two changes:
  1. Renamed the aggregated columns from `mean`/`count` to `avg_score`/`n`
     using `.agg(avg_score="mean", n="count")` — eliminates name collisions
     with pandas method names.
  2. Wrapped the chart in `if len(by_prov) > 0` and added a NaN-safe label
     builder to handle subsets where some provinces have zero learners.
     A clear "No learners match the current filters" message is shown
     instead of a crash when the chart would be empty.

**Also fixed:** A FutureWarning from `.fillna()` on a percentage frame in
Chart 2B was eliminated by casting to `float` explicitly before filling.

**Verification:** Re-applied every slicer combination that previously crashed
(Part-time employment, Digital confidence Medium/High, attendance risk High/Low,
device access combinations, internet Stable/Unstable). All combinations now
render correctly, or display a graceful empty-state message where appropriate.

## Bug #3 — Regression: pd.NA / NAType crash when filters stack on small subsets

**Discovered:** 25 May 2026, during follow-up stress-testing after Bug #2 fix.

**How it manifested:** Certain combined slicer selections (e.g. Age band +
Area type, or Province = KwaZulu-Natal / Limpopo in combination with another
filter) crashed Chart 2B with `TypeError: float() argument must be a string
or a real number, not 'NAType'`. The chart worked when each filter was
applied alone but failed when stacked.

**Root cause:** The Bug #2 fix replaced zero row sums with `pd.NA` to prevent
0÷0 division. `pd.NA` is a pandas extension-type missing marker, not a float.
Under certain filter combinations, the resulting `ct_pct` DataFrame retained
`pd.NA` values in some cells, and the subsequent `.astype("float")` call
could not convert `pd.NA` to a Python float, raising the TypeError.

This is a regression introduced by the Bug #2 fix — fixing the FutureWarning
inadvertently introduced a new crash path on a different subset of filter
combinations.

**Fix:** Replace the zero row sums with `float("nan")` (a standard NumPy NaN)
instead of `pd.NA`. NaN is a native float value, so the column dtype stays as
float throughout, and `.fillna(0.0)` cleanly converts NaN to zero without any
extension-type conversions. The `.astype("float")` step was no longer
necessary a

## Bug #4 — Reset button raised StreamlitAPIException

**Discovered:** 25 May 2026, during sidebar interaction testing.

**How it manifested:** Clicking the "Reset all filters" button raised
`StreamlitAPIException: st.session_state.age_filter cannot be modified
after the widget with key 'age_filter' is instantiated`.

**Root cause:** The reset logic ran inline after the `selectbox` widgets had
already been instantiated. Streamlit prevents external writes to a widget's
session_state key after the widget exists — the widget itself owns that key
for the remainder of the script run. The reset was therefore attempting an
illegal write.

**Fix:** Moved the reset logic into a named callback function and attached it
to the button via `on_click=_reset_all_filters`. Streamlit runs the callback
BEFORE the widgets are re-instantiated on the next script run, so writing to
the session_state keys is permitted at that point. Each key is now set
explicitly to its default "All X" value rather than `None`, so the selectboxes
display their default label after reset.

**Lesson recorded:** When a widget uses a `key`, that key belongs to the
widget after instantiation. Programmatic changes to widget state must happen
in a callback (`on_click=`, `on_change=`) so the change occurs before the
widget is recreated, not in inline code after the widget already exists.

**Verification:** Applied 4 simultaneous filters (Age 22-25, Township,
KZN, Phone only), clicked Reset all filters, and confirmed all eight
selectboxes returned to their "All X" defaults and the dashboard re-rendered
with the full 51-learner dataset.
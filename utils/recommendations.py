"""
recommendations.py
-------------------
Turns a single learner's data into concrete, supportive actions.

Why this file exists: the ethics principle of the whole tool is that a
risk indicator must never appear without a suggested support action
attached. This file is where that rule becomes code. The Learner Detail
page calls this for every learner it displays.

The rules below are deliberately simple and transparent. Anyone — staff,
learner, auditor — can read this file and see exactly why the tool
suggested what it suggested. No black box. That transparency is itself
an ethical requirement.
"""


def recommend_for_learner(learner):
    """Take one learner (a row from the dataframe) and return a list of
    suggested support actions.

    Each suggestion is a dict with:
      - 'action':  what the programme should offer
      - 'reason':  the specific data point that triggered it
      - 'priority': 'high', 'medium', or 'low' — guides ordering, not urgency-shaming

    Returns at least one item. If no specific need is detected, returns a
    neutral "check in" suggestion — never returns an empty list, because
    "no recommendations" reads as "no need," which is its own ethical risk.
    """
    suggestions = []

    # Rule 1 — Resource: device access
    # The most direct support action in the entire tool. Phone-only learners
    # face a real barrier that a device loan directly fixes.
    if learner.get("device_access") == "Phone only":
        suggestions.append({
            "action": "Offer device loan from the programme's device pool",
            "reason": "Learner reports phone-only device access",
            "priority": "high",
        })

    # Rule 2 — Resource: internet access
    # Data bundles are cheap, high-impact support. Trigger on either of the
    # two unstable categories — both signal connectivity is a barrier.
    if learner.get("internet_access") in ("Unstable", "Limited"):
        suggestions.append({
            "action": "Provide monthly data bundle and offline study materials",
            "reason": f"Internet access reported as {learner.get('internet_access')}",
            "priority": "high",
        })

    # Rule 3 — Schedule: employment status
    # Working learners often disengage not from lack of interest but lack of
    # time. Flexible scheduling addresses the structural issue.
    if learner.get("employment_status") == "Full-time":
        suggestions.append({
            "action": "Offer evening sessions and recorded materials for asynchronous learning",
            "reason": "Learner is in full-time employment",
            "priority": "medium",
        })

    # Rule 4 — Skill: low programming confidence
    # We use the BAND, not the raw number. The band column is None if the
    # score is missing or invalid, so we naturally skip rows we can't trust.
    if learner.get("programming_confidence_band") == "Low":
        suggestions.append({
            "action": "Pair learner with a peer mentor for the first 4 weeks",
            "reason": "Programming confidence is in the Low band (self-reported 1–2)",
            "priority": "medium",
        })

    # Rule 5 — The learner's own voice — highest priority of all
    # Anything the learner explicitly said they need takes precedence over
    # anything the system inferred. This is the "surface the learner's voice"
    # design rule from the stakeholder map, made literal.
    declared = learner.get("support_need")
    if declared and declared not in ("None right now", "Unsure", "", None):
        suggestions.insert(0, {  # insert at the front so it appears first
            "action": f"Address the learner's stated need: {declared}",
            "reason": "Learner explicitly requested this in their intake survey",
            "priority": "high",
        })

    # Fallback — never return zero suggestions
    if not suggestions:
        suggestions.append({
            "action": "Schedule a check-in conversation to understand current support needs",
            "reason": "No specific support trigger detected from intake data",
            "priority": "low",
        })

    return suggestions
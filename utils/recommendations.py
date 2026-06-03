"""
recommendations.py
-------------------
Rule-based suggestion engine. Takes learner data, returns concrete support actions.
Every suggestion includes the reason it was triggered.
"""


def recommend_for_learner(learner):
    """Return a list of support actions for one learner.
    
    Each suggestion includes: action (what to offer), reason (why), priority (high/medium/low).
    """
    suggestions = []

    # Rule 1: Phone-only access — offer device loan
    if learner.get("device_access") == "Phone only":
        suggestions.append({
            "action": "Offer device loan from the programme's device pool",
            "reason": "Learner reports phone-only device access",
            "priority": "high",
        })

    # Rule 2: Unstable/limited internet — offer data bundle
    if learner.get("internet_access") in ("Unstable", "Limited"):
        suggestions.append({
            "action": "Provide monthly data bundle and offline study materials",
            "reason": f"Internet access reported as {learner.get('internet_access')}",
            "priority": "high",
        })

    # Rule 3: Full-time employment — offer flexible scheduling
    if learner.get("employment_status") == "Full-time":
        suggestions.append({
            "action": "Offer evening sessions and recorded materials for asynchronous learning",
            "reason": "Learner is in full-time employment",
            "priority": "medium",
        })

    # Rule 4: Low programming confidence — pair with mentor
    if learner.get("programming_confidence_band") == "Low":
        suggestions.append({
            "action": "Pair learner with a peer mentor for the first 4 weeks",
            "reason": "Programming confidence is in the Low band (self-reported 1–2)",
            "priority": "medium",
        })

    # Rule 5: Learner's stated need — always prioritize
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
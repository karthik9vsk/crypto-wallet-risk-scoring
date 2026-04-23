def generate_feature_reasons(feature_map: dict) -> list[str]:
    reasons = []

    if feature_map.get("Sent tnx", 0) > 200:
        reasons.append("high outgoing transaction volume")

    if feature_map.get("Received Tnx", 0) > 200:
        reasons.append("high incoming transaction volume")

    if feature_map.get("Unique Sent To Addresses", 0) > 100:
        reasons.append("unusually high counterparty diversity")

    if feature_map.get("Total ERC20 tnxs", 0) > 300:
        reasons.append("heavy ERC20 transfer activity")

    if feature_map.get("Time Diff between first and last (Mins)", 0) < 60:
        reasons.append("compressed activity window")

    if feature_map.get("avg val sent", 0) > 1000:
        reasons.append("high average sent value")

    return reasons


def build_rule_based_explanation(probability: float, feature_map: dict) -> str:
    reasons = generate_feature_reasons(feature_map)

    risk_level = (
        "high" if probability >= 0.8
        else "medium" if probability >= 0.5
        else "low"
    )

    if reasons:
        joined = ", ".join(reasons)
        return (
            f"This wallet shows {risk_level} fraud risk "
            f"with suspicious indicators such as {joined}."
        )

    return f"This wallet shows {risk_level} fraud risk based on its transaction behavior."
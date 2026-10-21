def generate_recommendations(profile: dict):
    recommendations = []

    missing_percentages = profile.get(
        "missing_percentages",
        {}
    )

    duplicate_rows = profile.get(
        "duplicate_rows",
        0
    )

    outliers = profile.get(
        "outliers",
        {}
    )

    column_issues = profile.get(
        "column_issues",
        {}
    )

    # Missing-value recommendations
    for column, percentage in missing_percentages.items():

        if percentage >= 50:
            recommendations.append({
                "column": column,
                "issue": "missing_values",
                "severity": "high",
                "recommendation": (
                    "Consider removing this column or finding "
                    "a reliable source for the missing values."
                )
            })

        elif percentage >= 20:
            recommendations.append({
                "column": column,
                "issue": "missing_values",
                "severity": "medium",
                "recommendation": (
                    "Consider filling missing values using an "
                    "appropriate imputation method."
                )
            })

        elif percentage > 0:
            recommendations.append({
                "column": column,
                "issue": "missing_values",
                "severity": "low",
                "recommendation": (
                    "Review the missing values and decide whether "
                    "to fill or remove the affected rows."
                )
            })

    # Duplicate-row recommendation
    if duplicate_rows > 0:
        recommendations.append({
            "column": None,
            "issue": "duplicate_rows",
            "severity": "medium",
            "recommendation": (
                f"Review and consider removing the "
                f"{duplicate_rows} duplicate rows."
            )
        })

    # Outlier recommendations
    for column, result in outliers.items():

        percentage = result.get(
            "percentage",
            0
        )

        if percentage >= 20:
            severity = "high"

        elif percentage >= 10:
            severity = "medium"

        else:
            severity = "low"

        recommendations.append({
            "column": column,
            "issue": "numeric_outliers",
            "severity": severity,
            "recommendation": (
                "Review the detected outliers to determine "
                "whether they are valid extreme values or "
                "data-entry errors."
            )
        })

    # Constant-column recommendations
    for column, issues in column_issues.items():

        for issue in issues:

            if issue.get("type") == "constant_column":

                recommendations.append({
                    "column": column,
                    "issue": "constant_column",
                    "severity": "medium",
                    "recommendation": (
                        "Consider removing this column because "
                        "it contains only one unique value."
                    )
                })

    return recommendations
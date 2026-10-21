import pandas as pd


def calculate_quality_score(
    dataframe: pd.DataFrame,
    outliers: dict
):
    issues = []

    rows = dataframe.shape[0]
    columns = dataframe.shape[1]
    total_cells = rows * columns

    # Completeness score
    if total_cells > 0:
        missing_cells = int(
            dataframe.isnull().sum().sum()
        )

        missing_percentage = (
            missing_cells / total_cells
        ) * 100

        completeness_score = (
            100 - missing_percentage
        )
    else:
        missing_cells = 0
        completeness_score = 100

    if missing_cells > 0:
        issues.append(
            f"{missing_cells} missing values detected"
        )

    # Uniqueness score
    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    if rows > 0:
        duplicate_percentage = (
            duplicate_rows / rows
        ) * 100

        uniqueness_score = (
            100 - duplicate_percentage
        )
    else:
        uniqueness_score = 100

    if duplicate_rows > 0:
        issues.append(
            f"{duplicate_rows} duplicate rows detected"
        )

    # Anomaly score
    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    total_numeric_values = int(
        dataframe[numeric_columns]
        .count()
        .sum()
    )

    total_outliers = sum(
        result["count"]
        for result in outliers.values()
    )

    if total_numeric_values > 0:
        outlier_percentage = (
            total_outliers
            / total_numeric_values
        ) * 100

        anomaly_score = (
            100 - outlier_percentage
        )
    else:
        anomaly_score = 100

    if total_outliers > 0:
        issues.append(
            f"{total_outliers} numeric outliers detected"
        )

    # Overall quality score
    overall_score = (
        completeness_score * 0.4
        + uniqueness_score * 0.3
        + anomaly_score * 0.3
    )

    return {
        "overall_score": round(
            overall_score,
            2
        ),
        "completeness_score": round(
            completeness_score,
            2
        ),
        "uniqueness_score": round(
            uniqueness_score,
            2
        ),
        "anomaly_score": round(
            anomaly_score,
            2
        ),
        "issues": issues
    }


def detect_column_issues(dataframe: pd.DataFrame):
    column_issues = {}

    total_rows = dataframe.shape[0]

    for column in dataframe.columns:
        issues = []

        missing_count = int(
            dataframe[column]
            .isnull()
            .sum()
        )

        if total_rows > 0:
            missing_percentage = (
                missing_count
                / total_rows
            ) * 100
        else:
            missing_percentage = 0

        unique_count = int(
            dataframe[column]
            .nunique(dropna=True)
        )

        # Detect missing values
        if missing_count > 0:

            if missing_percentage >= 50:
                severity = "high"

            elif missing_percentage >= 20:
                severity = "medium"

            else:
                severity = "low"

            issues.append({
                "type": "missing_values",
                "message": (
                    f"{round(missing_percentage, 2)}% "
                    "of values are missing"
                ),
                "severity": severity
            })

        # Detect completely empty columns
        if (
            total_rows > 0
            and missing_count == total_rows
        ):
            issues.append({
                "type": "all_missing",
                "message": (
                    "Column contains no usable values"
                ),
                "severity": "high"
            })

        # Detect constant columns
        elif unique_count == 1:
            issues.append({
                "type": "constant_column",
                "message": (
                    "Column contains only one unique value"
                ),
                "severity": "medium"
            })

        if issues:
            column_issues[column] = issues

    return column_issues


def detect_numeric_outliers(
    dataframe: pd.DataFrame
):
    outlier_results = {}

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        series = (
            dataframe[column]
            .dropna()
        )

        # Need enough values for useful quartiles
        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        # If IQR is zero there is not enough spread
        if iqr == 0:
            continue

        lower_bound = (
            q1 - (1.5 * iqr)
        )

        upper_bound = (
            q3 + (1.5 * iqr)
        )

        outliers = series[
            (series < lower_bound)
            | (series > upper_bound)
        ]

        if not outliers.empty:

            outlier_results[column] = {

                "count": int(
                    outliers.count()
                ),

                "percentage": round(
                    (
                        outliers.count()
                        / series.count()
                    ) * 100,
                    2
                ),

                "lower_bound": round(
                    float(lower_bound),
                    3
                ),

                "upper_bound": round(
                    float(upper_bound),
                    3
                ),

                "sample_values": [
                    float(value)
                    for value
                    in outliers.head(5)
                ]
            }

    return outlier_results


def profile_dataframe(
    dataframe: pd.DataFrame
):

    missing_values = (
        dataframe.isnull().sum()
    )

    missing_percentages = (
        dataframe.isnull().mean() * 100
    ).round(2)

    unique_values = (
        dataframe.nunique(
            dropna=True
        )
    )

    numeric_summary = {}

    numeric_columns = (
        dataframe.select_dtypes(
            include="number"
        ).columns
    )

    for column in numeric_columns:

        series = dataframe[column]

        numeric_summary[column] = {

            "count": int(
                series.count()
            ),

            "mean": (
                round(
                    float(series.mean()),
                    3
                )
                if series.count() > 0
                else None
            ),

            "minimum": (
                float(series.min())
                if series.count() > 0
                else None
            ),

            "maximum": (
                float(series.max())
                if series.count() > 0
                else None
            ),

            "standard_deviation": (
                round(
                    float(series.std()),
                    3
                )
                if series.count() > 1
                else None
            )
        }

    column_issues = (
        detect_column_issues(
            dataframe
        )
    )

    outliers = (
        detect_numeric_outliers(
            dataframe
        )
    )

    quality = (
        calculate_quality_score(
            dataframe,
            outliers
        )
    )

    return {

        "rows": dataframe.shape[0],

        "columns": dataframe.shape[1],

        "column_names": (
            dataframe.columns.tolist()
        ),

        "data_types": {
            column: str(dtype)
            for column, dtype
            in dataframe.dtypes.items()
        },

        "missing_values": {
            column: int(value)
            for column, value
            in missing_values.items()
        },

        "missing_percentages": {
            column: float(value)
            for column, value
            in missing_percentages.items()
        },

        "unique_values": {
            column: int(value)
            for column, value
            in unique_values.items()
        },

        "duplicate_rows": int(
            dataframe
            .duplicated()
            .sum()
        ),

        "numeric_summary": (
            numeric_summary
        ),

        "quality": quality,

        "column_issues": (
            column_issues
        ),

        "outliers": outliers
    }
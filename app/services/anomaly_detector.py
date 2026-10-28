import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_ml_anomalies(dataframe: pd.DataFrame):
    numeric_data = dataframe.select_dtypes(
        include="number"
    ).copy()

    if numeric_data.empty:
        return {
            "status": "skipped",
            "reason": "No numeric columns available",
            "count": 0,
            "percentage": 0,
            "anomalies": []
        }

    if len(numeric_data) < 10:
        return {
            "status": "skipped",
            "reason": (
                "At least 10 rows are required for "
                "machine-learning anomaly detection"
            ),
            "count": 0,
            "percentage": 0,
            "anomalies": []
        }

    numeric_data = numeric_data.dropna(
        axis=1,
        how="all"
    )

    if numeric_data.empty:
        return {
            "status": "skipped",
            "reason": (
                "Numeric columns contain no usable values"
            ),
            "count": 0,
            "percentage": 0,
            "anomalies": []
        }

    numeric_data = numeric_data.fillna(
        numeric_data.median()
    )

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    predictions = model.fit_predict(
        numeric_data
    )

    anomaly_scores = model.decision_function(
        numeric_data
    )

    anomaly_rows = []

    for position, prediction in enumerate(predictions):

        if prediction == -1:
            row_index = dataframe.index[position]

            row_values = {}

            for column in dataframe.columns:
                value = dataframe.loc[
                    row_index,
                    column
                ]

                if pd.isna(value):
                    row_values[column] = None

                elif hasattr(value, "item"):
                    row_values[column] = value.item()

                else:
                    row_values[column] = value

            anomaly_rows.append({
                "row_index": int(row_index),
                "anomaly_score": round(
                    float(anomaly_scores[position]),
                    4
                ),
                "values": row_values
            })

    anomaly_count = len(
        anomaly_rows
    )

    anomaly_percentage = (
        anomaly_count / len(dataframe)
    ) * 100

    return {
        "status": "completed",
        "method": "Isolation Forest",
        "numeric_columns_used": (
            numeric_data.columns.tolist()
        ),
        "count": anomaly_count,
        "percentage": round(
            anomaly_percentage,
            2
        ),
        "anomalies": anomaly_rows
    }
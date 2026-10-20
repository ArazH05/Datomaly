import pandas as pd

def profile_dataframe(dataframe: pd.DataFrame):
    missing_values = dataframe.isnull().sum()

    missing_percentages = (
        dataframe.isnull().mean() * 100
    ).round(2)

    unique_values = dataframe.nunique(dropna=True)

    numeric_summary = {}

    numeric_columns = dataframe.select_dtypes(include="number").columns

    for column in numeric_columns:
        series = dataframe[column]

        numeric_summary[column] = {
            "count": int(series.count()),
            "mean": round(float(series.mean()), 3)
            if series.count() > 0 else None,
            "minimum": float(series.min())
            if series.count() > 0 else None,
            "maximum": float(series.max())
            if series.count() > 0 else None,
            "standard_deviation": round(float(series.std()), 3)
            if series.count() > 1 else None
        }

    return {
        "rows": dataframe.shape[0],
        "columns": dataframe.shape[1],

        "column_names": dataframe.columns.tolist(),

        "data_types": {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        },

        "missing_values": {
            column: int(value)
            for column, value in missing_values.items()
        },

        "missing_percentages": {
            column: float(value)
            for column, value in missing_percentages.items()
        },

        "unique_values": {
            column: int(value)
            for column, value in unique_values.items()
        },

        "duplicate_rows": int(
            dataframe.duplicated().sum()
        ),

        "numeric_summary": numeric_summary
    }
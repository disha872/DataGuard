import pandas as pd
import numpy as np
def profile_dataset(df:pd.DataFrame)->dict:
   dataset_summary=get_dataset_summary(df)
   column_profiles=get_column_profiles(df)
   warnings = generate_warnings(dataset_summary,column_profiles)
   return{
       "dataset_summary": dataset_summary,
       "column_profiles": column_profiles,
       "warnings": warnings
   }
def get_dataset_summary(df:pd.DataFrame)->dict:
    summary={
        "number_of_rows":df.shape[0],
        "number_of_columns":df.shape[1],
        "column_names":list(df.columns),
        "data_types":df.dtypes.astype(str).to_dict()
    }
    return summary

def get_column_profiles(df:pd.DataFrame)->list:
    profiles=[]
    for col in df.columns:
        series=df[col]
        missing_count=series.isnull().sum()
        missing_percent = (missing_count / len(series)) * 100 if len(series) > 0 else 0

        profile={
            "column_name":col,
            "data_type":str(series.dtype),
            "missing_count":int(missing_count),
            "missing_percent":round(missing_percent,2),
            "unique_values": series.nunique(dropna=True)
        }
        if pd.api.types.is_numeric_dtype(series):
            profile["numeric_stats"]={
                "mean":float(series.mean()),
                "std":float(series.std()),
                "min":float(series.min()),
                "max":float(series.max())
            }
        profiles.append(profile)
    return profiles

def generate_warnings(dataset_summary:dict,column_profiles:list)->list:
    warnings=[]
    if dataset_summary["number_of_rows"]==0:
        warnings.append("The dataset has no rows.")
    if dataset_summary["number_of_columns"]==0:
        warnings.append("The dataset has no columns.")
    for profile in column_profiles:
        if profile["missing_percent"]>50:
            warnings.append(f"Column '{profile['column_name']}' has more than 50% missing values.")
        if profile["unique_values"] < 2:
            warnings.append(f"Column '{profile['column_name']}' has less than 2 unique values.")
    return warnings
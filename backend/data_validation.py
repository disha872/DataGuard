import pandas as pd
from typing import Dict,List,Optional

def validate_dataset(
    df:pd.DataFrame,
    profile_result:Dict,
    rules:Optional[Dict]=None)->Dict:
    column_issues: List[Dict]=[]
    dataset_issues: List[Dict]=[]

    column_issues.extend(validate_missing_values(df,profile_result))
    column_issues.extend(validate_type_consistency(df,profile_result))
    column_issues.extend(validate_duplicates(df))
    column_issues.extend(validate_outliers(df))

    validation_status=determine_validation_status(
        column_issues=column_issues,
        dataset_issues=dataset_issues
    )
    return{
        "column_issues":column_issues,
        "dataset_issues":dataset_issues,
        "validation_status":validation_status
    }

def validate_missing_values(
    df:pd.DataFrame,
    profile_result:Dict
)->List[Dict]:
    issues=[]
    for col in profile_result["column_profiles"]:
        
        if(col["missing_percent"]>20):
            severity="HIGH"
        elif col["missing_percent"]>5:
            severity="MEDIUM"
        else:
            continue
        issue={
        "column":col["column_name"],
        "issue_type":"MISSING_VALUES",
        "missing_percent":col["missing_percent"],
        "severity":severity,
        "message": f"Column '{col['column_name']}' has {col['missing_percent']}% missing values"
    }
        issues.append(issue)

    return issues

def validate_type_consistency(
    df:pd.DataFrame,
    profile_result:Dict)->List[Dict]:
    issues=[]
    for col in profile_result["column_profiles"]:
        column_name=col["column_name"]
        dtype=col["data_type"]

        if "int" not in dtype and "float" not in dtype:
            continue

        series=df[column_name]

        original_missing=series.isnull().sum()

        converted=pd.to_numeric(series,errors="coerce")

        new_missing=converted.isnull().sum()

        invalid_count=new_missing-original_missing

        if invalid_count<=0:
            continue

        invalid_percent = ((invalid_count)/len(series))*100

        if invalid_percent > 5:
            severity="HIGH"

        else:
            severity="MEDIUM"

        issue = {
            "column":column_name,
            "issue_type":"TYPE_INCONSISTENCY",
            "invalid_count":int(invalid_count),
            "invalid_percent":round(invalid_percent,2),
            "severity":severity,
            "message":(
                f"Column '{column_name}' contains {invalid_count} non-numeric values"
            )
        }
        issues.append(issue)

    return issues

def validate_duplicates(
    df:pd.DataFrame
)-> List[Dict]:
    issues=[]
    total_rows=df.shape[0]
    if total_rows==0:
        return issues
    duplicate_count=df.duplicated().sum()
    if duplicate_count==0:
        return issues
    duplicate_percent=(duplicate_count/total_rows)*100
    if duplicate_percent>2:
        severity="HIGH"
    else:
        severity="MEDIUM"
    issue={
        "issue_type":"DUPLICATE_ROWS",
        "duplicate_count":int(duplicate_count),
        "duplicate_percent":round(duplicate_percent,2),
        "severity":severity,
        "message":(
            f"DataSet contains {duplicate_count} duplicate rows"
            f"({round(duplicate_percent,2)}%)"
        )

    }
    issues.append(issue)
    return issues

def validate_outliers(
    df:pd.DataFrame
)->List[Dict]:
    issues=[]
    total_rows=len(df)
    if total_rows==0:
        return issues
    for col in df.columns:
        series=df[col]

        if not pd.api.types.is_numeric_dtype(series):
            continue
        
        q1=series.quantile(0.25)
        q3=series.quantile(0.75)
        iqr=q3 - q1

        if iqr==0:
            continue

        lower=q1-1.5*iqr
        upper=q3+1.5*iqr

        outliers = (series<lower) | (series>upper)
        outlier_count=outliers.sum()

        if outlier_count==0:
            continue
        
        outlier_percent=(outlier_count/total_rows)*100

        severity="HIGH" if outlier_percent>2 else "MEDIUM"

        issue={
            "column":col,
            "issue_type":"OUTLIERS",
            "outlier_count":int(outlier_count),
            "severity":severity
        }
        issues.append(issue)

    return issues

def determine_validation_status(
    column_issues: List[Dict],
    dataset_issues: List[Dict]
) -> Dict:
    score=100
    all_issues=column_issues+dataset_issues

    for issue in all_issues:
        if issue.get("severity")=="HIGH":
            score-=15
        elif issue.get("severity")=="MEDIUM":
            score-=5
    
    if score<0:
        score=0

    if score>= 80:
        status="PASS"
    elif score>=60:
        status="WARN"
    else:
        status="FAIL"
    return {
        "quality_score":score,
        "validation_status":status
    }
    
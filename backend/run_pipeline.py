import pandas as pd
from data_profiling import profile_dataset
from data_validation import validate_dataset

def run_pipeline(csv_path:str):
    df=pd.read_csv(csv_path)

    profile_result=profile_dataset(df)

    validation_result=validate_dataset(df,profile_result)

    return{
        "profile":profile_result,
        "validation":validation_result
    }

# “To ensure that execution code runs only when the file is executed directly,
#  and not when it is imported as a module
if __name__=="__main__":
    result=run_pipeline("../sample_data/credit_data.csv")
    print(result)
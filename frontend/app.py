import streamlit as st
import pandas as pd
import sys
import os
import json
# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.data_profiling import profile_dataset
from backend.data_validation import validate_dataset

st.set_page_config(
    page_title="DataGuard – Data Quality Checker",
    layout="wide"
)

st.title("🛡️ DataGuard – Data Quality Validation Tool")
st.write(
    "Upload a CSV file to analyze data quality, detect issues, "
    "and receive a trust score."
)

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("File uploaded successfully!")

        # -----------------------------
        # Run Profiling & Validation
        # -----------------------------
        with st.spinner("Analyzing data quality..."):
            import requests

            API_URL = "https://dataguard-backend.onrender.com/analyze"

            response = requests.post(
            API_URL,
            files={"file": uploaded_file.getvalue()})

            result = response.json()
            # st.write("Raw API response:", result)

            profile_result = result["profile"]
            validation_result = result["validation"]

        
        
        full_report = {
            "profile": profile_result,
            "validation": validation_result
        }

        report_json = json.dumps(full_report, indent=4, default=str)

        st.download_button(
            label="📥 Download Data Quality Report (JSON)",
            data=report_json,
            file_name="data_quality_report.json",
            mime="application/json"
        )

        # -----------------------------
        # Dataset Summary
        # -----------------------------
        st.subheader("📊 Dataset Summary")
        summary = profile_result["dataset_summary"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", summary["number_of_rows"])
        col2.metric("Columns", summary["number_of_columns"])
        col3.metric(
            "Quality Score",
            validation_result["validation_status"]["quality_score"]
        )

        # -----------------------------
        # Validation Status Badge
        # -----------------------------
        status = validation_result["validation_status"]["validation_status"]

        if status == "PASS":
            st.success("✅ Dataset Status: PASS")
        elif status == "WARN":
            st.warning("⚠️ Dataset Status: WARN")
        else:
            st.error("❌ Dataset Status: FAIL")

        # -----------------------------
        # Column Issues Table
        # -----------------------------
        st.subheader("🚨 Column-Level Issues")

        column_issues = validation_result["column_issues"]

        if len(column_issues) == 0:
            st.success("No column-level issues detected.")
        else:
            issues_df = pd.DataFrame(column_issues)
            st.dataframe(issues_df, use_container_width=True)
        
        coll1,coll2,coll3=st.columns(3)
        with coll1:
            st.subheader("📉 Missing Values per Column")

            missing_data = []
            missing_data = []

            for col in profile_result["column_profiles"]:
                if col["missing_percent"] > 0:   # only collect columns with missing data
                    missing_data.append({
                        "column": col["column_name"],
                        "missing_percent": col["missing_percent"]
                    })

            if len(missing_data) == 0:
                st.success("No missing values in any column")
            else:
                missing_df = pd.DataFrame(missing_data)
                st.bar_chart(missing_df.set_index("column"))

        with coll2:
            st.subheader("📊 Outliers per Column")

            outlier_data = []
            for issue in validation_result["column_issues"]:
                if issue["issue_type"] == "OUTLIERS":
                    outlier_data.append({
                        "column": issue["column"],
                        "outlier_count": issue["outlier_count"]
                    })

            if len(outlier_data) > 0:
                outlier_df = pd.DataFrame(outlier_data)
                st.bar_chart(outlier_df.set_index("column"))
            else:
                st.write("No outliers detected.")
        with coll3:
            st.subheader("⚠️ Issue Severity Distribution")

            severity_counts = {"HIGH": 0, "MEDIUM": 0}

            for issue in validation_result["column_issues"]:
                severity = issue["severity"]
                severity_counts[severity] += 1

            severity_df = pd.DataFrame(
                list(severity_counts.items()),
                columns=["Severity", "Count"]
            )

            st.pyplot(
                severity_df.set_index("Severity").plot.pie(
                    y="Count",
                    autopct="%1.1f%%",
                    legend=False
                ).get_figure()
            )



        # -----------------------------
        # Profiling Details (Optional)
        # -----------------------------
        with st.expander("🔍 View Column Profiling Details"):
            st.json(profile_result["column_profiles"])

    except Exception as e:
        st.error(f"Error processing file: {e}")

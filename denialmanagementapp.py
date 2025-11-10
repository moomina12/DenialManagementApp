import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Healthcare Denial Management Dashboard",
                   page_icon="💊", layout="wide")

# ---------------- FUNCTIONS ----------------

EXPECTED_COLUMNS = [
    "ICD10_Code", "CPT_Code", "claim_date", "Patient_Age", "Gender", "Region",
    "Provider_Specialty", "Hospital_Type", "Claim_Status", "Claimed_Amount",
    "Approved_Amount", "Denied_amount", "Denial_reason"
]

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"The uploaded file is missing these columns: {', '.join(missing_cols)}")
    if "claim_date" in df.columns:
        df["claim_date"] = pd.to_datetime(df["claim_date"], errors="coerce")
    return df

def download_button(df, filename="filtered_results.csv"):
    """Provide download buttons for CSV and Excel."""
    csv = df.to_csv(index=False).encode("utf-8")

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Results")
    excel_data = buffer.getvalue()

    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )
    st.download_button(
        label="⬇️ Download Excel",
        data=excel_data,
        file_name=filename.replace(".csv", ".xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ---------------- SIDEBAR ----------------
st.sidebar.image("tag3.gif", width=200, caption="Welcome!")

menu = st.sidebar.radio("Go to", ["🏠 Home", "📊 Top Denial Reasons"])

if "data" not in st.session_state:
    st.session_state.data = None

# ---------------- HOME PAGE ----------------
if menu == "🏠 Home":
    

    # ---- WELCOME SECTION ----
    st.markdown(
        """
        <h4 style='text-align:center; color:#2C3E50;'>✨ Welcome to the Denial Management App ✨</h4>
        <p style='text-align:center; color:gray;'>
        Analyze, monitor, and reduce healthcare claim denials with data-driven insights.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    #New line starts here
    import pandas as pd
    import io
    # Create a small sample DataFrame
    sample_data = pd.DataFrame({
    "ICD10_Code": ["A00", "B00"],
    "CPT_Code": ["12345", "67890"],
    "claim_date": ["2025-01-01", "2025-02-15"],
    "Patient_Age": [34, 45],
    "Gender": ["M", "F"],
    "Region": ["North", "South"],
    "Provider_Specialty": ["Cardiology", "Orthopedics"],
    "Hospital_Type": ["Private", "Public"],
    "Claim_Status": ["Approved", "Denied"],
    "Claimed_Amount": [1000, 2000],
    "Approved_Amount": [1000, 0],
    "Denied_amount": [0, 2000],
    "Denial_reason": ["", "Missing info"]
    })
    # Convert to CSV in-memory
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode()
    # Add a download button above the upload
    st.download_button(
    label="📥 Download Sample CSV File",
    data=csv_bytes,
    file_name="sample_claims.csv",
    mime="text/csv"
    )
#new line ends here
    # ---- CSV UPLOAD WITH RIGHT-SIDE SMALL FONT PROMPT ----
    left_col, right_col = st.columns([2, 1])  # left wider than right

    with left_col:
        uploaded_file = st.file_uploader("📂 Upload Your Claims CSV File", type=["csv"])

    with right_col:
        st.markdown(
            """
            <div style="border:1px solid #ddd; padding:10px; border-radius:5px; background-color:#f9f9f9;">
            <strong>Expected Columns:</strong><br>
            <span style="font-size:10px;">
            ICD10_Code, CPT_Code, claim_date, Patient_Age, Gender, Region, 
            Provider_Specialty, Hospital_Type, Claim_Status, Claimed_Amount, 
            Approved_Amount, Denied_amount, Denial_reason
            </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    if uploaded_file is not None:
        try:
            df = load_data(uploaded_file)
            st.session_state.data = df
            st.success(f"✅ File uploaded successfully! {df.shape[0]} records loaded.")
            st.markdown("---")
        except Exception as e:
            st.error(f"⚠️ Error loading file: {e}")
            st.info("Please make sure your CSV has exactly these columns:\n\n" +
                ", ".join(EXPECTED_COLUMNS))
            
            # -------- FILTERS --------
        st.sidebar.header("🔍 Filters")

        regions = df["Region"].dropna().unique().tolist()
        specialties = df["Provider_Specialty"].dropna().unique().tolist()

        selected_region = st.sidebar.multiselect("Select Region(s)", regions, default=regions)
        selected_specialty = st.sidebar.multiselect("Select Specialty(ies)", specialties, default=specialties)

        if "claim_date" in df.columns:
            min_date = df["claim_date"].min()
            max_date = df["claim_date"].max()
            selected_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        else:
            selected_date = None

        filtered_df = df.copy()
        if selected_region:
            filtered_df = filtered_df[filtered_df["Region"].isin(selected_region)]
        if selected_specialty:
            filtered_df = filtered_df[filtered_df["Provider_Specialty"].isin(selected_specialty)]
        if selected_date:
            filtered_df = filtered_df[
                filtered_df["claim_date"].between(pd.to_datetime(selected_date[0]), pd.to_datetime(selected_date[1]))
            ]

        # -------- KPIs --------
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        total_claims = len(filtered_df)
        total_claimed = filtered_df["Claimed_Amount"].sum()
        total_approved = filtered_df["Approved_Amount"].sum()
        total_denied = filtered_df["Denied_amount"].sum()

        col1.metric("Total Claims", total_claims)
        col2.metric("Total Claimed", f"${total_claimed:,.2f}")
        col3.metric("Approved Amount", f"${total_approved:,.2f}")
        col4.metric("Denied Amount", f"${total_denied:,.2f}")

        # -------- CHARTS --------
        st.markdown("### 📈 Claim Status Distribution")
        if "Claim_Status" in filtered_df.columns:
            status_chart = filtered_df["Claim_Status"].value_counts().reset_index()
            status_chart.columns = ["Claim_Status", "Count"]
            fig = px.pie(status_chart, names="Claim_Status", values="Count",
                         title="Claim Status Breakdown", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

        # Denied amount by region
        st.markdown("### 💸 Denied Amount by Region")
        if "Region" in filtered_df.columns:
            denied_by_region = filtered_df.groupby("Region")["Denied_amount"].sum().reset_index()
            fig2 = px.bar(denied_by_region, x="Region", y="Denied_amount",
                          title="Denied Amount by Region", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

        # -------- NEW: Denial Trend Over Time --------
        st.markdown("### 📆 Denial Trend Over Time")
        if "claim_date" in filtered_df.columns:
            trend = (
                filtered_df.groupby(pd.Grouper(key="claim_date", freq="M"))["Denied_amount"]
                .sum()
                .reset_index()
                .sort_values("claim_date")
            )
            fig3 = px.line(trend, x="claim_date", y="Denied_amount",
                           markers=True,
                           title="Monthly Denied Amount Trend")
            st.plotly_chart(fig3, use_container_width=True)

        # -------- DOWNLOAD SECTION --------
        st.markdown("### 💾 Download Filtered Results")
        download_button(filtered_df, filename="filtered_claims.csv")

# ---------------- TOP DENIAL REASONS ----------------
elif menu == "📊 Top Denial Reasons":
    st.title("📊 Top Denial Reasons")

    if st.session_state.data is None:
        st.warning("⚠️ Please upload a CSV file first from the Home page.")
    else:
        df = st.session_state.data

        # -------- FILTERS --------
        st.sidebar.header("🔍 Filters")

        regions = df["Region"].dropna().unique().tolist()
        specialties = df["Provider_Specialty"].dropna().unique().tolist()

        selected_region = st.sidebar.multiselect("Select Region(s)", regions, default=regions)
        selected_specialty = st.sidebar.multiselect("Select Specialty(ies)", specialties, default=specialties)

        if "claim_date" in df.columns:
            min_date = df["claim_date"].min()
            max_date = df["claim_date"].max()
            selected_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        else:
            selected_date = None

        filtered_df = df.copy()
        if selected_region:
            filtered_df = filtered_df[filtered_df["Region"].isin(selected_region)]
        if selected_specialty:
            filtered_df = filtered_df[filtered_df["Provider_Specialty"].isin(selected_specialty)]
        if selected_date:
            filtered_df = filtered_df[
                filtered_df["claim_date"].between(pd.to_datetime(selected_date[0]), pd.to_datetime(selected_date[1]))
            ]

        # -------- TOP DENIAL REASONS --------
        filtered_df["Denial_reason"].fillna("Unknown", inplace=True)
        denial_summary = (
            filtered_df.groupby("Denial_reason")["Denied_amount"]
            .sum()
            .reset_index()
            .sort_values("Denied_amount", ascending=False)
            .head(10)
        )

        fig3 = px.bar(
            denial_summary,
            x="Denied_amount",
            y="Denial_reason",
            orientation="h",
            title="Top Denial Reasons (by Denied Amount)",
            text_auto=".2s",
        )
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 📋 Detailed Denial Data")
        st.dataframe(denial_summary, use_container_width=True)

        # -------- DOWNLOAD SECTION --------
        st.markdown("### 💾 Download Filtered Denial Data")
        download_button(filtered_df, filename="filtered_denials.csv")

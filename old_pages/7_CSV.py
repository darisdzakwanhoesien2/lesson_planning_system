import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="📄 CSV Column Concatenator",
    layout="wide"
)

st.title("📄 CSV Column Concatenator")
st.caption("Upload a CSV and concatenate selected columns (e.g. C, D, E, F)")

# ==================================================
# UPLOAD CSV
# ==================================================
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if not uploaded_file:
    st.info("👆 Upload a CSV file to begin")
    st.stop()

# ==================================================
# LOAD CSV
# ==================================================
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"❌ Failed to read CSV: {e}")
    st.stop()

st.success(f"Loaded {len(df)} rows × {len(df.columns)} columns")

# ==================================================
# COLUMN SELECTION
# ==================================================
st.subheader("🔧 Column Selection")

columns = list(df.columns)

selected_columns = st.multiselect(
    "Select columns to concatenate (order matters)",
    columns,
    default=columns[2:6] if len(columns) >= 6 else columns
)

delimiter = st.text_input(
    "Delimiter",
    value="\n"
)

if not selected_columns:
    st.warning("Select at least one column")
    st.stop()

# ==================================================
# PREVIEW RAW DATA
# ==================================================
st.subheader("📋 Raw Data Preview")
st.dataframe(df[selected_columns])

# ==================================================
# CONCATENATION
# ==================================================
df["concatenated"] = (
    df[selected_columns]
    .astype(str)
    .fillna("")
    .agg(delimiter.join, axis=1)
)

# ==================================================
# OUTPUT
# ==================================================
st.subheader("🔗 Concatenated Output")
st.dataframe(df[["concatenated"]])

# ==================================================
# COPY-FRIENDLY TEXT
# ==================================================
st.subheader("📄 Copy-Friendly Text")
st.text_area(
    "Concatenated rows",
    value="\n\n".join(df["concatenated"].tolist()),
    height=300
)

# ==================================================
# MARKDOWN EXPORT
# ==================================================
st.subheader("⬇️ Download as Markdown")

markdown_content = "\n\n---\n\n".join(
    f"### Entry {i+1}\n\n{row}"
    for i, row in enumerate(df["concatenated"].tolist())
)

st.download_button(
    label="Download Markdown (.md)",
    data=markdown_content,
    file_name="concatenated_output.md",
    mime="text/markdown"
)

# ==================================================
# DOWNLOAD
# ==================================================
csv_out = df.to_csv(index=False)

st.download_button(
    label="⬇️ Download CSV",
    data=csv_out,
    file_name="concatenated_output.csv",
    mime="text/csv"
)

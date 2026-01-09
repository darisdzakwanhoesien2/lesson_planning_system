import streamlit as st
from pathlib import Path
from graphviz import Digraph

from utils.loaders import load_json, load_index

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Global Course Mapping",
    layout="wide"
)

st.title("🌍 Global Course Mapping Overview")
st.caption("All source courses mapped to University of Oulu courses")

# ==================================================
# PATHS
# ==================================================
DATA_DIR = Path("data")

SOURCE_INDEX = DATA_DIR / "registries" / "source_courses_index.json"
MAPPING_INDEX = DATA_DIR / "registries" / "mapping_index.json"
MAPPING_DIR = DATA_DIR / "mappings"

# ==================================================
# LOAD REGISTRIES
# ==================================================
source_courses = load_index(SOURCE_INDEX)
mapping_index = load_index(MAPPING_INDEX)

if not source_courses:
    st.error("❌ No source courses found.")
    st.stop()

if not mapping_index:
    st.warning("⚠️ No mappings defined yet.")
    st.stop()

# ==================================================
# BUILD GLOBAL GRAPH
# ==================================================
dot = Digraph(
    format="png",
    graph_attr={
        "rankdir": "LR",
        "splines": "ortho",
        "nodesep": "0.7",
        "ranksep": "1.1"
    }
)

# --------------------------------------------------
# SOURCE COURSE NODES
# --------------------------------------------------
for src in source_courses:
    src_code = src["course_code"]
    src_name = src["course_name"]

    dot.node(
        src_code,
        f"{src_code}\n{src_name}",
        shape="box",
        style="filled",
        fillcolor="#FFF4CC"
    )

# --------------------------------------------------
# MAPPINGS → TARGET COURSES
# --------------------------------------------------
target_nodes_added = set()

for mapping in mapping_index:
    src_code = mapping["source_course"]
    mapping_file = MAPPING_DIR / mapping["mapping_file"]

    mapping_data = load_json(mapping_file)
    if not mapping_data:
        continue

    for target in mapping_data.get("target_courses", []):
        tgt_code = target.get("course_code", "UNKNOWN")
        tgt_name = target.get("course_name", "Unknown")

        # Avoid duplicate target nodes
        if tgt_code not in target_nodes_added:
            dot.node(
                tgt_code,
                f"{tgt_code}\n{tgt_name}",
                shape="box",
                style="filled",
                fillcolor="#E6F4EA"
            )
            target_nodes_added.add(tgt_code)

        dot.edge(src_code, tgt_code)

# ==================================================
# RENDER
# ==================================================
st.subheader("📊 Global Source → Target Course Graph")
st.graphviz_chart(dot)

# ==================================================
# LEGEND
# ==================================================
with st.expander("ℹ️ Legend"):
    st.markdown("""
- **Yellow nodes**: Source courses (your past / NUS courses)
- **Green nodes**: University of Oulu target courses
- **Arrows**: Credit transfer / equivalency relationships
""")

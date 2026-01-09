import streamlit as st
from pathlib import Path
from graphviz import Digraph
from datetime import datetime
import json

from utils.loaders import load_json, load_index

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Global Course Mapping (Past → NUS → Oulu)",
    layout="wide"
)

st.title("🌍 Global Course Mapping")
st.caption("Past learning → NUS courses → University of Oulu equivalence")

# ==================================================
# PATHS
# ==================================================
DATA_DIR = Path("data")

PAST_DIR = DATA_DIR / "past_courses"
MAPPING_DIR = DATA_DIR / "mappings"

SOURCE_INDEX = DATA_DIR / "registries" / "source_courses_index.json"
MAPPING_INDEX = DATA_DIR / "registries" / "mapping_index.json"

EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# LOAD REGISTRIES
# ==================================================
source_courses = load_index(SOURCE_INDEX)
mapping_index = load_index(MAPPING_INDEX)

if not source_courses:
    st.error("❌ No source courses found in source_courses_index.json")
    st.stop()

if not mapping_index:
    st.warning("⚠️ No mappings defined in mapping_index.json")
    st.stop()

# ==================================================
# INDEX MAPPINGS FOR FAST LOOKUP
# ==================================================
mapping_by_source = {
    m["source_course"]: m["mapping_file"]
    for m in mapping_index
}

# ==================================================
# GRAPHVIZ SETUP
# ==================================================
dot = Digraph(
    format="png",
    graph_attr={
        "rankdir": "LR",
        "splines": "ortho",
        "nodesep": "0.9",
        "ranksep": "1.3"
    }
)

added_nodes = set()

# ==================================================
# JSON EXPORT STRUCTURE
# ==================================================
export_graph = {
    "metadata": {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "description": "Past → NUS → University of Oulu course mappings"
    },
    "nodes": [],
    "edges": []
}

json_nodes_added = set()

def add_json_node(node_id, label, node_type):
    if node_id in json_nodes_added:
        return
    export_graph["nodes"].append({
        "id": node_id,
        "label": label,
        "type": node_type
    })
    json_nodes_added.add(node_id)

def add_json_edge(src, tgt, relation):
    export_graph["edges"].append({
        "from": src,
        "to": tgt,
        "relation": relation
    })

# ==================================================
# BUILD GRAPH
# ==================================================
for src in source_courses:
    src_code = src["course_code"]
    src_name = src["course_name"]

    # -----------------------------
    # SOURCE (NUS) NODE
    # -----------------------------
    if src_code not in added_nodes:
        dot.node(
            src_code,
            f"{src_code}\n{src_name}",
            shape="box",
            style="filled",
            fillcolor="#FFF4CC"
        )
        added_nodes.add(src_code)

    add_json_node(
        src_code,
        f"{src_code}\n{src_name}",
        "source"
    )

    # -----------------------------
    # PAST COURSES (EVIDENCE)
    # -----------------------------
    past_file = PAST_DIR / f"{src_code}.json"
    past_data = load_json(past_file) if past_file.exists() else {}

    for pc in past_data.get("past_courses", []):
        past_id = f"PAST_{src_code}_{pc['course_name']}"

        if past_id not in added_nodes:
            dot.node(
                past_id,
                f"{pc['course_name']}\n({pc['institution']})",
                shape="box",
                style="filled",
                fillcolor="#E8F0FE"
            )
            added_nodes.add(past_id)

        dot.edge(past_id, src_code)

        add_json_node(
            past_id,
            f"{pc['course_name']}\n({pc['institution']})",
            "past"
        )

        add_json_edge(
            past_id,
            src_code,
            "evidence_for"
        )

    # -----------------------------
    # TARGET COURSES (OULU)
    # -----------------------------
    mapping_file = mapping_by_source.get(src_code)
    if not mapping_file:
        continue

    mapping_data = load_json(MAPPING_DIR / mapping_file)
    if not mapping_data:
        continue

    for tgt in mapping_data.get("target_courses", []):
        tgt_code = tgt.get("course_code", "UNKNOWN")
        tgt_name = tgt.get("course_name", "Unknown")

        if tgt_code not in added_nodes:
            dot.node(
                tgt_code,
                f"{tgt_code}\n{tgt_name}",
                shape="box",
                style="filled",
                fillcolor="#E6F4EA"
            )
            added_nodes.add(tgt_code)

        dot.edge(src_code, tgt_code)

        add_json_node(
            tgt_code,
            f"{tgt_code}\n{tgt_name}",
            "target"
        )

        add_json_edge(
            src_code,
            tgt_code,
            "maps_to"
        )

# ==================================================
# SAVE JSON TO DISK
# ==================================================
export_path = EXPORT_DIR / "course_mapping_graph.json"

with export_path.open("w", encoding="utf-8") as f:
    json.dump(export_graph, f, indent=2, ensure_ascii=False)

# ==================================================
# RENDER
# ==================================================
st.subheader("📊 Past → NUS → Oulu Mapping Graph")
st.graphviz_chart(dot)

# ==================================================
# DOWNLOAD
# ==================================================
st.download_button(
    label="⬇️ Download mapping as JSON",
    data=json.dumps(export_graph, indent=2, ensure_ascii=False),
    file_name="course_mapping_graph.json",
    mime="application/json"
)

# ==================================================
# LEGEND
# ==================================================
with st.expander("ℹ️ Legend"):
    st.markdown("""
- **Blue boxes**: Past learning (Coursera / prior evidence)
- **Yellow boxes**: NUS courses
- **Green boxes**: University of Oulu courses
- **Solid arrows**: Curriculum relationships
""")

st.success(f"✅ JSON exported to {export_path}")

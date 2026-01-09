import streamlit as st
from pathlib import Path

from utils.loaders import load_json, load_index

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="University of Oulu Transfer Planning",
    layout="wide"
)

st.title("🎓 University of Oulu – Transfer Planning")
st.caption("Source → Target course equivalency and academic justification")

# ==================================================
# PATHS
# ==================================================
DATA_DIR = Path("data")

SOURCE_INDEX = DATA_DIR / "registries" / "source_courses_index.json"
MAPPING_INDEX = DATA_DIR / "registries" / "mapping_index.json"

SOURCE_DIR = DATA_DIR / "source_courses"
TARGET_DIR = DATA_DIR / "target_courses" / "oulu"
MAPPING_DIR = DATA_DIR / "mappings"

# ==================================================
# LOAD INDICES
# ==================================================
source_courses = load_index(SOURCE_INDEX)
mapping_index = load_index(MAPPING_INDEX)

if not source_courses:
    st.error("No source courses found.")
    st.stop()

# ==================================================
# SOURCE COURSE SELECTION
# ==================================================
st.subheader("1️⃣ Select Source Course")

source_map = {
    f"{c['course_code']} — {c['course_name']}": c["course_code"]
    for c in source_courses
}

selected_label = st.selectbox(
    "Source course",
    options=list(source_map.keys())
)

source_code = source_map[selected_label]

# ==================================================
# LOAD SOURCE COURSE DETAIL
# ==================================================
source_course_path = SOURCE_DIR / f"{source_code}.json"
source_course = load_json(source_course_path)

if not source_course:
    st.warning(f"No detailed data found for {source_code}")

# ==================================================
# FIND MAPPING FILE
# ==================================================
mapping_entry = next(
    (m for m in mapping_index if m["source_course"] == source_code),
    None
)

if not mapping_entry:
    st.warning("No transfer mapping defined for this course.")
    st.stop()

mapping_path = MAPPING_DIR / mapping_entry["mapping_file"]
mapping_data = load_json(mapping_path)

if not mapping_data:
    st.error("Mapping file could not be loaded.")
    st.stop()

# ==================================================
# DISPLAY SOURCE COURSE
# ==================================================
with st.expander("📘 Source Course Details", expanded=True):
    if source_course:
        st.markdown(f"**Course:** {source_course.get('course_name', 'unknown')}")
        st.markdown(f"**Code:** {source_course.get('course_code', 'unknown')}")
        st.markdown(f"**Credits:** {source_course.get('credits', 'unknown')}")
        st.markdown("**Description:**")
        st.write(source_course.get("course_description", "unknown"))
    else:
        st.info("Only basic source metadata available.")

# ==================================================
# TARGET COURSE MAPPINGS
# ==================================================
st.subheader("2️⃣ Recommended University of Oulu Courses")

targets = mapping_data.get("target_courses", [])

if not targets:
    st.info("No target courses mapped.")
    st.stop()

for target in targets:
    with st.container():
        st.markdown("---")
        st.markdown(f"### 🎯 {target['course_name']} ({target['ects']} ECTS)")
        st.markdown(f"**Course code:** {target['course_code']}")
        st.markdown(f"**Mapping type:** `{target['mapping_type']}`")
        st.markdown(f"**Justification:** {target['justification']}")

        if target.get("url"):
            st.link_button("Open course page", target["url"])

        # ----------------------------------------------
        # Load full target course spec (if exists)
        # ----------------------------------------------
        target_file = TARGET_DIR / f"{target['course_code']}_*.json"
        matched_files = list(TARGET_DIR.glob(f"{target['course_code']}*.json"))

        if matched_files:
            target_full = load_json(matched_files[0])
            with st.expander("📄 Full Target Course Details"):
                st.markdown(f"**Faculty:** {target_full['target_course'].get('faculty', 'unknown')}")
                st.markdown(f"**Level:** {target_full['target_course'].get('level', 'unknown')}")
                st.markdown("**Learning Outcomes:**")
                st.write(target_full["target_course"].get("learning_outcomes", []))
        else:
            st.info("Full target course specification not yet available.")

# ==================================================
# OVERALL RECOMMENDATION
# ==================================================
st.subheader("3️⃣ Overall Transfer Recommendation")

st.markdown(f"**Recommendation:** {mapping_data.get('overall_recommendation', 'unknown')}")
st.markdown(f"**Confidence:** {mapping_data.get('confidence', 'unknown')}")

from graphviz import Digraph

st.subheader("2️⃣ Course Mapping Visualization")

from graphviz import Digraph

def render_course_graph(source_course, mapping_data):
    """
    Visualizes:
    Past Courses → NUS Course → Oulu Extra Courses
    """

    # --------------------------------------------------
    # Defensive extraction (NO KeyError possible)
    # --------------------------------------------------
    course_code = source_course.get("course_code", "UNKNOWN")
    course_name = source_course.get("course_name", "Unknown Course")

    # Optional: past courses (may not exist yet)
    past_courses = source_course.get("previous_courses", [])
    if not past_courses:
        past_courses = ["Past Coursework"]

    dot = Digraph(
        format="png",
        graph_attr={
            "rankdir": "LR",
            "splines": "ortho",
            "nodesep": "0.8",
            "ranksep": "1.2"
        }
    )

    # --------------------------------------------------
    # Column 1: Past Courses
    # --------------------------------------------------
    for pc in past_courses:
        dot.node(
            pc,
            pc,
            shape="box",
            style="filled",
            fillcolor="#E8F0FE"
        )

    # --------------------------------------------------
    # Column 2: NUS Course (Source)
    # --------------------------------------------------
    nus_node_id = course_code
    nus_label = f"{course_code}\n{course_name}"

    dot.node(
        nus_node_id,
        nus_label,
        shape="box",
        style="filled",
        fillcolor="#FFF4CC"
    )

    for pc in past_courses:
        dot.edge(pc, nus_node_id)

    # --------------------------------------------------
    # Column 3: Oulu Extra Courses
    # --------------------------------------------------
    for target in mapping_data.get("target_courses", []):
        target_code = target.get("course_code", "UNKNOWN")
        target_name = target.get("course_name", "Unknown")

        oulu_label = f"{target_code}\n{target_name}"

        dot.node(
            target_code,
            oulu_label,
            shape="box",
            style="filled",
            fillcolor="#E6F4EA"
        )

        dot.edge(nus_node_id, target_code)

    return dot



graph = render_course_graph(source_course, mapping_data)
st.graphviz_chart(graph)

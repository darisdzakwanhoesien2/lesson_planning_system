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
st.caption("Past learning → NUS courses → University of Oulu courses")

# ==================================================
# PATHS
# ==================================================
DATA_DIR = Path("data")

SOURCE_INDEX = DATA_DIR / "registries" / "source_courses_index.json"
MAPPING_INDEX = DATA_DIR / "registries" / "mapping_index.json"

SOURCE_DIR = DATA_DIR / "source_courses"
PAST_DIR = DATA_DIR / "past_courses"
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
        "nodesep": "0.9",
        "ranksep": "1.3"
    }
)

added_nodes = set()

# --------------------------------------------------
# LOOP OVER SOURCE COURSES
# --------------------------------------------------
for src in source_courses:
    src_code = src["course_code"]
    src_name = src["course_name"]

    # -----------------------------
    # Load past course provenance
    # -----------------------------
    past_file = PAST_DIR / f"{src_code}.json"
    past_data = load_json(past_file) if past_file.exists() else {}

    past_courses = past_data.get("past_courses", [])
    direct_oulu = past_data.get("direct_oulu_links", [])

    # -----------------------------
    # Past Courses Nodes
    # -----------------------------
    for pc in past_courses:
        pc_id = f"PAST_{pc['course_name']}"
        if pc_id not in added_nodes:
            dot.node(
                pc_id,
                f"{pc['course_name']}\n({pc['institution']})",
                shape="box",
                style="filled",
                fillcolor="#E8F0FE"
            )
            added_nodes.add(pc_id)

        dot.edge(pc_id, src_code)

    # -----------------------------
    # NUS Source Course Node
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

    # -----------------------------
    # Mapping to Oulu Courses
    # -----------------------------
    mapping_entry = next(
        (m for m in mapping_index if m["source_course"] == src_code),
        None
    )

    if not mapping_entry:
        continue

    mapping_data = load_json(MAPPING_DIR / mapping_entry["mapping_file"])
    if not mapping_data:
        continue

    for tgt in mapping_data.get("target_courses", []):
        tgt_code = tgt["course_code"]
        tgt_name = tgt["course_name"]

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

    # -----------------------------
    # Direct Past → Oulu Readiness
    # -----------------------------
    for direct in direct_oulu:
        oulu_id = f"OULU_{direct['course_name']}"

        if oulu_id not in added_nodes:
            dot.node(
                oulu_id,
                f"{direct['course_name']}\n({direct['ects']} ECTS)",
                shape="box",
                style="filled",
                fillcolor="#D0F0E0"
            )
            added_nodes.add(oulu_id)

        for pc in past_courses:
            pc_id = f"PAST_{pc['course_name']}"
            dot.edge(
                pc_id,
                oulu_id,
                style="dashed",
                color="gray"
            )

# ==================================================
# RENDER
# ==================================================
st.subheader("📊 Global Learning & Transfer Graph")
st.graphviz_chart(dot)

# ==================================================
# LEGEND
# ==================================================
with st.expander("ℹ️ Legend"):
    st.markdown("""
- **Blue**: Past learning (Coursera / prior foundation)
- **Yellow**: NUS courses
- **Green**: University of Oulu credit mappings
- **Teal**: Oulu advanced-readiness (non-credit)
- **Solid arrows**: Formal equivalence
- **Dashed arrows**: Preparatory / readiness pathways
""")


# import streamlit as st
# from pathlib import Path

# from utils.loader import load_courses
# from utils.planners import summarize_course, extract_learning_gaps

# # ==================================================
# # PAGE CONFIG
# # ==================================================
# st.set_page_config(
#     page_title="🎓 Course Transfer Planner",
#     layout="wide"
# )

# st.title("🎓 Course Transfer & Learning Planner")
# st.caption("Plan transfer courses, understand equivalencies, and prepare future studies")

# # ==================================================
# # PATHS
# # ==================================================
# BASE_DIR = Path(__file__).parent

# SOURCE_DIR = BASE_DIR / "data" / "source_courses"
# TARGET_DIR = BASE_DIR / "data" / "target_courses"

# # ==================================================
# # LOAD DATA (SCHEMA-AWARE)
# # ==================================================
# try:
#     source_courses = load_courses(SOURCE_DIR, course_type="source")
# except Exception as e:
#     st.error(f"Failed to load source courses: {e}")
#     st.stop()

# try:
#     target_courses = load_courses(TARGET_DIR, course_type="target")
# except Exception as e:
#     st.warning(f"Target courses not fully loaded: {e}")
#     target_courses = {}

# if not source_courses:
#     st.error("❌ No source courses found.")
#     st.stop()

# # ==================================================
# # SIDEBAR — COURSE SELECTION
# # ==================================================
# st.sidebar.header("📚 Select Source Course")

# selected_code = st.sidebar.selectbox(
#     "Source course code",
#     sorted(source_courses.keys())
# )

# course = source_courses[selected_code]
# src = course["source_course"]

# # ==================================================
# # OVERVIEW
# # ==================================================
# st.header(f"{src['code']} — {src['name']}")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("Credits", src["credits"])

# with col2:
#     st.metric("Level", src["level"])

# with col3:
#     st.metric("Orientation", src["academic_orientation"])

# st.divider()

# # ==================================================
# # TABS
# # ==================================================
# tabs = st.tabs([
#     "📘 Course Content",
#     "🎯 Learning Objectives",
#     "🔍 Equivalency & Gaps",
#     "🧭 Learning Paths",
#     "🏫 Transfer Planning (Oulu)"
# ])

# # ==================================================
# # TAB 1 — COURSE CONTENT
# # ==================================================
# with tabs[0]:
#     st.subheader("Key Topics")
#     st.write(", ".join(src["key_topics"]))

#     st.subheader("Pedagogical Style")

#     st.markdown("**Assessment Methods**")
#     st.write(", ".join(src["pedagogical_style"]["assessment"]))

#     st.markdown("**Emphasis**")
#     st.write(", ".join(src["pedagogical_style"]["emphasis"]))

#     st.subheader("Recommended Literature")
#     st.write(src["recommended_literature"])

# # ==================================================
# # TAB 2 — LEARNING OBJECTIVES
# # ==================================================
# with tabs[1]:
#     st.subheader("Intended Learning Outcomes")

#     for obj in src["learning_objectives"]:
#         st.checkbox(obj, value=False)

# # ==================================================
# # TAB 3 — EQUIVALENCY & GAPS
# # ==================================================
# with tabs[2]:
#     st.subheader("Primary Coursera Equivalency")

#     primary = course.get("primary_recommendation")

#     if primary:
#         st.success(f"{primary['course']} — {primary['provider']}")

#         st.markdown("**Justification**")
#         for k, v in primary["justification"].items():
#             label = k.replace("_", " ").title()
#             st.write(f"- **{label}**: {v}")
#     else:
#         st.warning("No primary Coursera recommendation available.")

#     st.divider()
#     st.subheader("Identified Academic Gaps")

#     gaps = extract_learning_gaps(course)

#     if gaps:
#         for g in gaps:
#             st.warning(g)
#     else:
#         st.info("No significant gaps identified.")

# # ==================================================
# # TAB 4 — LEARNING PATHS
# # ==================================================
# with tabs[3]:
#     st.subheader("Recommended Learning Paths")

#     paths = course.get("recommended_learning_paths", {})

#     if not paths:
#         st.info("No learning paths defined for this course.")

#     for _, path in paths.items():
#         with st.expander(path["goal"]):
#             for step in path["path"]:
#                 st.write(f"• {step}")
#             st.caption(path["reasoning"])

# # ==================================================
# # TAB 5 — TRANSFER PLANNING (OULU)
# # ==================================================
# with tabs[4]:
#     st.subheader("University of Oulu Transfer Planning")

#     if not target_courses:
#         st.warning("No Oulu target courses loaded yet.")
#     else:
#         st.success(f"{len(target_courses)} Oulu course(s) loaded.")

#         st.markdown("**Available Target Courses**")
#         for code, tgt in target_courses.items():
#             tgt_course = tgt["target_course"]
#             st.write(
#                 f"- **{tgt_course['code']}** — "
#                 f"{tgt_course['name']} ({tgt_course['credits']} ECTS)"
#             )

#     st.divider()

#     st.markdown("**Planned Transfer Logic (Upcoming)**")
#     st.markdown("""
#     - Topic overlap scoring (EE2023 ↔ Oulu courses)
#     - Credit conversion (Units ↔ ECTS)
#     - Learning outcome alignment
#     - Gap-based prerequisite recommendations
#     - Semester-by-semester study planning
#     """)


# import streamlit as st
# from pathlib import Path

# from utils.loader import load_courses
# from utils.planners import summarize_course, extract_learning_gaps

# # ==================================================
# # PAGE CONFIG
# # ==================================================
# st.set_page_config(
#     page_title="🎓 Course Transfer Planner",
#     layout="wide"
# )

# st.title("🎓 Course Transfer & Learning Planner")
# st.caption("Plan transfer courses, understand equivalencies, and prepare future studies")

# # ==================================================
# # LOAD DATA
# # ==================================================
# SOURCE_DIR = Path("data/source_courses")
# TARGET_DIR = Path("data/target_courses")

# source_courses = load_courses(SOURCE_DIR)
# target_courses = load_courses(TARGET_DIR)  # placeholder for Oulu later

# if not source_courses:
#     st.error("No source courses found.")
#     st.stop()

# # ==================================================
# # SIDEBAR — COURSE SELECTION
# # ==================================================
# st.sidebar.header("📚 Select Source Course")

# selected_code = st.sidebar.selectbox(
#     "Course code",
#     list(source_courses.keys())
# )

# course = source_courses[selected_code]
# src = course["source_course"]

# # ==================================================
# # OVERVIEW
# # ==================================================
# st.header(f"{src['code']} — {src['name']}")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("Credits", src["credits"])
# with col2:
#     st.metric("Level", src["level"])
# with col3:
#     st.metric("Orientation", src["academic_orientation"])

# # ==================================================
# # TABS
# # ==================================================
# tabs = st.tabs([
#     "📘 Course Content",
#     "🎯 Learning Objectives",
#     "🔍 Equivalency & Gaps",
#     "🧭 Learning Paths",
#     "🏫 Transfer Planning (Oulu)"
# ])

# # --------------------------------------------------
# # TAB 1 — CONTENT
# # --------------------------------------------------
# with tabs[0]:
#     st.subheader("Key Topics")
#     st.write(", ".join(src["key_topics"]))

#     st.subheader("Pedagogical Style")
#     st.write("**Assessment:**")
#     st.write(", ".join(src["pedagogical_style"]["assessment"]))

#     st.write("**Emphasis:**")
#     st.write(", ".join(src["pedagogical_style"]["emphasis"]))

#     st.subheader("Recommended Literature")
#     st.write(src["recommended_literature"])

# # --------------------------------------------------
# # TAB 2 — OBJECTIVES
# # --------------------------------------------------
# with tabs[1]:
#     for obj in src["learning_objectives"]:
#         st.checkbox(obj, value=False)

# # --------------------------------------------------
# # TAB 3 — EQUIVALENCY
# # --------------------------------------------------
# with tabs[2]:
#     st.subheader("Primary Coursera Match")

#     primary = course["primary_recommendation"]
#     st.success(f"{primary['course']} — {primary['provider']}")

#     st.write("**Justification:**")
#     for k, v in primary["justification"].items():
#         st.write(f"- **{k.replace('_',' ').title()}**: {v}")

#     st.divider()
#     st.subheader("Identified Gaps")
#     gaps = extract_learning_gaps(course)

#     if gaps:
#         for g in gaps:
#             st.warning(g)
#     else:
#         st.info("No significant gaps identified.")

# # --------------------------------------------------
# # TAB 4 — LEARNING PATHS
# # --------------------------------------------------
# with tabs[3]:
#     paths = course["recommended_learning_paths"]

#     for key, path in paths.items():
#         with st.expander(path["goal"]):
#             for step in path["path"]:
#                 st.write(f"• {step}")
#             st.caption(path["reasoning"])

# # --------------------------------------------------
# # TAB 5 — TRANSFER PLANNING (FUTURE)
# # --------------------------------------------------
# with tabs[4]:
#     st.info("Oulu course database will be integrated here.")

#     st.write("Planned logic:")
#     st.write("""
#     - Match EE2023 topics against Oulu Signals / Systems courses
#     - Credit conversion (ECTS ↔ Units)
#     - Gap-based prerequisite suggestions
#     - Semester-by-semester planning
#     """)

#     if target_courses:
#         st.success("Target courses loaded.")
#     else:
#         st.warning("No target courses loaded yet.")
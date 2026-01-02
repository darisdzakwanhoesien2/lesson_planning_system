import streamlit as st
from pathlib import Path
from graphviz import Digraph

from utils.loaders import load_json, load_index

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Prerequisite & Readiness Graph",
    layout="wide"
)

st.title("🧠 Prerequisite & Readiness Graph")
st.caption("Evidence → Abstract prerequisites → NUS courses → Oulu readiness")

# ==================================================
# PATHS
# ==================================================
DATA_DIR = Path("data")

SOURCE_INDEX = DATA_DIR / "registries" / "source_courses_index.json"
PAST_DIR = DATA_DIR / "past_courses"

# ==================================================
# LOAD SOURCE COURSES
# ==================================================
source_courses = load_index(SOURCE_INDEX)

if not source_courses:
    st.error("❌ No source courses found.")
    st.stop()

# ==================================================
# DEFINE ABSTRACT PREREQUISITES (ONTOLOGY)
# ==================================================
# These are NOT courses — they are capability concepts
PREREQUISITES = {
    "calculus": "Calculus",
    "linear_algebra": "Linear Algebra",
    "differential_equations": "Differential Equations",
    "probability": "Probability & Statistics",
    "numerical_methods": "Numerical Methods",
    "signals_systems": "Signals & Systems",
    "control_theory": "Control Theory",
    "quantum_mechanics": "Quantum Mechanics Foundations"
}

# ==================================================
# HELPER: infer prerequisites from past course text
# ==================================================
def infer_prerequisites(text: str):
    text = text.lower()
    inferred = set()

    if any(k in text for k in ["calculus", "integral", "derivative"]):
        inferred.add("calculus")
    if any(k in text for k in ["linear algebra", "matrix", "vector"]):
        inferred.add("linear_algebra")
    if any(k in text for k in ["differential equation", "ode"]):
        inferred.add("differential_equations")
    if any(k in text for k in ["probability", "statistics"]):
        inferred.add("probability")
    if any(k in text for k in ["numerical", "computation"]):
        inferred.add("numerical_methods")
    if any(k in text for k in ["signal", "system", "laplace", "fourier"]):
        inferred.add("signals_systems")
    if any(k in text for k in ["control", "feedback"]):
        inferred.add("control_theory")
    if any(k in text for k in ["quantum", "schrödinger"]):
        inferred.add("quantum_mechanics")

    return inferred

# ==================================================
# BUILD GRAPH
# ==================================================
dot = Digraph(
    format="png",
    graph_attr={
        "rankdir": "LR",
        "splines": "ortho",
        "nodesep": "1.0",
        "ranksep": "1.5"
    }
)

added_nodes = set()

# --------------------------------------------------
# ABSTRACT PREREQUISITE NODES
# --------------------------------------------------
for key, label in PREREQUISITES.items():
    dot.node(
        f"PREREQ_{key}",
        label,
        shape="ellipse",
        style="filled",
        fillcolor="#F0F0F0"
    )

# --------------------------------------------------
# LOOP OVER NUS COURSES
# --------------------------------------------------
for src in source_courses:
    src_code = src["course_code"]
    src_name = src["course_name"]

    # -----------------------------
    # NUS COURSE NODE
    # -----------------------------
    dot.node(
        src_code,
        f"{src_code}\n{src_name}",
        shape="box",
        style="filled",
        fillcolor="#FFF4CC"
    )

    # -----------------------------
    # LOAD PAST COURSE DATA
    # -----------------------------
    past_file = PAST_DIR / f"{src_code}.json"
    if not past_file.exists():
        continue

    past_data = load_json(past_file)
    if not past_data:
        continue

    past_courses = past_data.get("past_courses", [])
    direct_oulu = past_data.get("direct_oulu_links", [])

    # -----------------------------
    # EVIDENCE NODES (Coursera etc.)
    # -----------------------------
    for pc in past_courses:
        evidence_id = f"EVIDENCE_{src_code}_{pc['course_name']}"

        dot.node(
            evidence_id,
            f"{pc['course_name']}\n({pc['institution']})",
            shape="box",
            style="filled",
            fillcolor="#E8F0FE"
        )

        # Evidence → NUS
        dot.edge(evidence_id, src_code)

        # Evidence → Abstract prerequisites
        text_blob = (
            pc.get("course_name", "") + " " +
            pc.get("justification", "")
        )

        inferred = infer_prerequisites(text_blob)

        for prereq in inferred:
            dot.edge(
                evidence_id,
                f"PREREQ_{prereq}",
                style="dashed",
                color="gray"
            )

            # Abstract prerequisite → NUS
            dot.edge(
                f"PREREQ_{prereq}",
                src_code
            )

    # -----------------------------
    # OULU READINESS (NON-CREDIT)
    # -----------------------------
    for direct in direct_oulu:
        oulu_id = f"READY_{direct['course_name']}"

        dot.node(
            oulu_id,
            f"{direct['course_name']}\n({direct['ects']} ECTS)",
            shape="box",
            style="filled",
            fillcolor="#D0F0E0"
        )

        # NUS → Oulu readiness
        dot.edge(
            src_code,
            oulu_id,
            style="dashed",
            color="black"
        )

# ==================================================
# RENDER
# ==================================================
st.subheader("📊 Prerequisite & Readiness Graph")
st.graphviz_chart(dot)

# ==================================================
# LEGEND
# ==================================================
with st.expander("ℹ️ Legend"):
    st.markdown("""
- **Blue boxes**: Evidence (Coursera / prior learning)
- **Gray ovals**: Abstract prerequisites (capabilities)
- **Yellow boxes**: NUS courses
- **Teal boxes**: Oulu readiness (future / non-credit)
- **Solid arrows**: Capability dependency
- **Dashed arrows**: Evidence or readiness relationships
""")

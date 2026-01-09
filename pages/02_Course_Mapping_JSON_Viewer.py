import streamlit as st
from pathlib import Path
import json
from graphviz import Digraph

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Course Mapping Graph Viewer (JSON)",
    layout="wide"
)

st.title("📊 Course Mapping Graph Viewer")
st.caption("Visualization and tables loaded from exported JSON graph")

# ==================================================
# PATH
# ==================================================
GRAPH_JSON_PATH = Path("data/exports/course_mapping_graph.json")
# GRAPH_JSON_PATH = Path("data/exports/course_mapping_graph.json") _v2

if not GRAPH_JSON_PATH.exists():
    st.error("❌ course_mapping_graph.json not found in data/exports/")
    st.stop()

# ==================================================
# LOAD JSON
# ==================================================
with GRAPH_JSON_PATH.open("r", encoding="utf-8") as f:
    graph_data = json.load(f)

nodes = graph_data.get("nodes", [])
edges = graph_data.get("edges", [])
metadata = graph_data.get("metadata", {})

# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.header("🔎 Filters")

node_types = sorted(set(n["type"] for n in nodes))
visible_types = st.sidebar.multiselect(
    "Show node types",
    node_types,
    default=node_types
)

# ==================================================
# BUILD TABLE DATA
# ==================================================
past_rows = []
source_rows = []
target_rows = []

for node in nodes:
    row = {
        "ID": node["id"],
        "Label": node["label"]
    }

    if node["type"] == "past":
        past_rows.append(row)
    elif node["type"] == "source":
        source_rows.append(row)
    elif node["type"] == "target":
        target_rows.append(row)

# ==================================================
# TABLE VIEW
# ==================================================
st.subheader("📋 Course Tables")

tab_past, tab_source, tab_target = st.tabs(
    ["🟦 Past Courses", "🟨 NUS Courses", "🟩 Oulu Courses"]
)

with tab_past:
    if past_rows:
        st.dataframe(past_rows, use_container_width=True)
    else:
        st.info("No past courses available.")

with tab_source:
    if source_rows:
        st.dataframe(source_rows, use_container_width=True)
    else:
        st.info("No NUS courses available.")

with tab_target:
    if target_rows:
        st.dataframe(target_rows, use_container_width=True)
    else:
        st.info("No Oulu courses available.")

# ==================================================
# GRAPH SETUP
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

# ==================================================
# COLOR MAP
# ==================================================
COLOR_BY_TYPE = {
    "past": "#E8F0FE",     # Blue
    "source": "#FFF4CC",   # Yellow
    "target": "#E6F4EA"    # Green
}

# ==================================================
# ADD NODES
# ==================================================
visible_node_ids = set()

for node in nodes:
    if node["type"] not in visible_types:
        continue

    dot.node(
        node["id"],
        node["label"],
        shape="box",
        style="filled",
        fillcolor=COLOR_BY_TYPE.get(node["type"], "#FFFFFF")
    )
    visible_node_ids.add(node["id"])

# ==================================================
# ADD EDGES
# ==================================================
for edge in edges:
    if edge["from"] in visible_node_ids and edge["to"] in visible_node_ids:
        dot.edge(
            edge["from"],
            edge["to"],
            label=edge.get("relation", "")
        )

# ==================================================
# GRAPH RENDER
# ==================================================
st.subheader("🧭 Course Mapping Graph")
st.graphviz_chart(dot)

# ==================================================
# METADATA & STATS
# ==================================================
with st.expander("📌 Graph Metadata"):
    st.json(metadata)

with st.expander("📈 Graph Statistics"):
    st.write({
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "node_types": {
            t: sum(1 for n in nodes if n["type"] == t)
            for t in node_types
        }
    })

# ==================================================
# RAW JSON VIEW
# ==================================================
with st.expander("🗂 Raw JSON"):
    st.json(graph_data)


# import streamlit as st
# from pathlib import Path
# import json
# from graphviz import Digraph

# # ==================================================
# # PAGE CONFIG
# # ==================================================
# st.set_page_config(
#     page_title="Course Mapping Graph Viewer (JSON)",
#     layout="wide"
# )

# st.title("📊 Course Mapping Graph Viewer")
# st.caption("Visualization loaded from exported JSON graph")

# # ==================================================
# # PATH
# # ==================================================
# GRAPH_JSON_PATH = Path("data/exports/course_mapping_graph.json")

# if not GRAPH_JSON_PATH.exists():
#     st.error("❌ course_mapping_graph.json not found in data/exports/")
#     st.stop()

# # ==================================================
# # LOAD JSON
# # ==================================================
# with GRAPH_JSON_PATH.open("r", encoding="utf-8") as f:
#     graph_data = json.load(f)

# nodes = graph_data.get("nodes", [])
# edges = graph_data.get("edges", [])
# metadata = graph_data.get("metadata", {})

# # ==================================================
# # SIDEBAR FILTERS
# # ==================================================
# st.sidebar.header("🔎 Filters")

# node_types = sorted(set(n["type"] for n in nodes))
# visible_types = st.sidebar.multiselect(
#     "Show node types",
#     node_types,
#     default=node_types
# )

# # ==================================================
# # GRAPH SETUP
# # ==================================================
# dot = Digraph(
#     format="png",
#     graph_attr={
#         "rankdir": "LR",
#         "splines": "ortho",
#         "nodesep": "0.9",
#         "ranksep": "1.3"
#     }
# )

# # ==================================================
# # COLOR MAP
# # ==================================================
# COLOR_BY_TYPE = {
#     "past": "#E8F0FE",     # Blue
#     "source": "#FFF4CC",   # Yellow
#     "target": "#E6F4EA"    # Green
# }

# # ==================================================
# # ADD NODES
# # ==================================================
# visible_node_ids = set()

# for node in nodes:
#     if node["type"] not in visible_types:
#         continue

#     dot.node(
#         node["id"],
#         node["label"],
#         shape="box",
#         style="filled",
#         fillcolor=COLOR_BY_TYPE.get(node["type"], "#FFFFFF")
#     )
#     visible_node_ids.add(node["id"])

# # ==================================================
# # ADD EDGES
# # ==================================================
# for edge in edges:
#     if edge["from"] in visible_node_ids and edge["to"] in visible_node_ids:
#         dot.edge(
#             edge["from"],
#             edge["to"],
#             label=edge.get("relation", "")
#         )

# # ==================================================
# # RENDER
# # ==================================================
# st.subheader("🧭 Course Mapping Graph")
# st.graphviz_chart(dot)

# # ==================================================
# # METADATA & STATS
# # ==================================================
# with st.expander("📌 Graph Metadata"):
#     st.json(metadata)

# with st.expander("📈 Graph Statistics"):
#     st.write({
#         "total_nodes": len(nodes),
#         "total_edges": len(edges),
#         "node_types": {
#             t: sum(1 for n in nodes if n["type"] == t)
#             for t in node_types
#         }
#     })

# # ==================================================
# # RAW JSON VIEW
# # ==================================================
# with st.expander("🗂 Raw JSON"):
#     st.json(graph_data)

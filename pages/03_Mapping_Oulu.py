import streamlit as st
from pathlib import Path
import json
from graphviz import Digraph
from collections import defaultdict
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="Past → Oulu Mapping with Notes", layout="wide")

st.title("🎓 Past → Oulu Course Mapping (with Notes)")
st.caption("Edit notes, descriptions, and URLs — saved permanently. Physics: https://opas.peppi.oulu.fi/en/programme/45124?period=2025-2026. Information Science: https://opas.peppi.oulu.fi/en/offering/SA2025TOL/44975?period=2025-2026")

# ==================================================
# PATHS
# ==================================================
GRAPH_JSON_PATH = Path("data/exports/course_mapping_graph.json")
NOTES_PATH = Path("data/exports/course_notes.json")
NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)

if not GRAPH_JSON_PATH.exists():
    st.error("❌ course_mapping_graph.json not found in data/exports/")
    st.stop()

# ==================================================
# LOAD GRAPH
# ==================================================
with GRAPH_JSON_PATH.open("r", encoding="utf-8") as f:
    graph_data = json.load(f)

nodes = graph_data["nodes"]
edges = graph_data["edges"]

node_by_id = {n["id"]: n for n in nodes}
node_type = {n["id"]: n["type"] for n in nodes}

past_nodes = {n["id"]: n for n in nodes if n["type"] == "past"}
target_nodes = {n["id"]: n for n in nodes if n["type"] == "target"}

# ==================================================
# LOAD NOTES (PERSISTENT)
# ==================================================
if NOTES_PATH.exists():
    with NOTES_PATH.open("r", encoding="utf-8") as f:
        notes_db = json.load(f)
else:
    notes_db = {}

# ==================================================
# BUILD PATHS
# ==================================================
past_to_nus = defaultdict(set)
nus_to_oulu = defaultdict(set)

for e in edges:
    src, tgt = e.get("from"), e.get("to")
    if not src or not tgt:
        continue

    if node_type.get(src) == "past" and node_type.get(tgt) == "source":
        past_to_nus[src].add(tgt)
    if node_type.get(src) == "source" and node_type.get(tgt) == "target":
        nus_to_oulu[src].add(tgt)

collapsed = defaultdict(set)
for p, nus_set in past_to_nus.items():
    for n in nus_set:
        for o in nus_to_oulu.get(n, []):
            collapsed[p].add(o)

# ==================================================
# SIDEBAR FILTER
# ==================================================
st.sidebar.header("🎯 Filter")

past_label_to_id = {v["label"]: k for k, v in past_nodes.items()}

selected_labels = st.sidebar.multiselect(
    "Select Past Courses",
    options=sorted(past_label_to_id.keys())
)

if selected_labels:
    selected_past_ids = {past_label_to_id[l] for l in selected_labels}
else:
    selected_past_ids = set(past_nodes.keys())

# ==================================================
# BUILD EDITABLE TABLE
# ==================================================
rows = []

for pid in selected_past_ids:
    for tid in collapsed.get(pid, []):
        key = f"{pid}__{tid}"

        record = notes_db.get(key, {})

        rows.append({
            "past_id": pid,
            "past_course": past_nodes[pid]["label"],
            "oulu_id": tid,
            "oulu_course": target_nodes[tid]["label"],
            "description": record.get("description", ""),
            "notes": record.get("notes", ""),
            "url": record.get("url", "")
        })

df = pd.DataFrame(rows)

# ==================================================
# EDITOR
# ==================================================
st.subheader("📝 Editable Mapping Notes (Saved Permanently)")

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "past_id": st.column_config.TextColumn("Past ID", disabled=True),
        "oulu_id": st.column_config.TextColumn("Oulu ID", disabled=True),
        "past_course": st.column_config.TextColumn("Past Course", disabled=True),
        "oulu_course": st.column_config.TextColumn("Oulu Course", disabled=True),
        "url": st.column_config.LinkColumn("URL")
    }
)

# ==================================================
# SAVE BUTTON
# ==================================================
if st.button("💾 Save Notes Permanently"):
    for _, r in edited_df.iterrows():
        key = f"{r.past_id}__{r.oulu_id}"
        notes_db[key] = {
            "description": r.description,
            "notes": r.notes,
            "url": r.url
        }

    with NOTES_PATH.open("w", encoding="utf-8") as f:
        json.dump(notes_db, f, indent=2, ensure_ascii=False)

    st.success("Saved to data/exports/course_notes.json")

# ==================================================
# GRAPH
# ==================================================
dot = Digraph(format="png", graph_attr={"rankdir": "LR", "nodesep": "1", "ranksep": "1.3"})

for pid in selected_past_ids:
    dot.node(pid, past_nodes[pid]["label"], shape="box", style="filled", fillcolor="#E8F0FE")

mapped_targets = set()
for pid in selected_past_ids:
    mapped_targets |= collapsed.get(pid, set())

for tid in mapped_targets:
    dot.node(tid, target_nodes[tid]["label"], shape="box", style="filled", fillcolor="#E6F4EA")

for pid in selected_past_ids:
    for tid in collapsed.get(pid, []):
        dot.edge(pid, tid)

st.subheader("🧭 Transfer Graph (Past → Oulu)")
st.graphviz_chart(dot)

# ==================================================
# DEBUG
# ==================================================
with st.expander("🛠 Raw Notes DB"):
    st.json(notes_db)


# import streamlit as st
# from pathlib import Path
# import json
# from graphviz import Digraph
# from collections import defaultdict

# # ==================================================
# # PAGE CONFIG
# # ==================================================
# st.set_page_config(
#     page_title="Past → Oulu Course Mapping (Collapsed)",
#     layout="wide"
# )

# st.title("🎓 Past → Oulu Course Mapping")
# st.caption("Direct equivalency paths collapsed from Past → NUS → Oulu")

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

# # ==================================================
# # NODE LOOKUPS
# # ==================================================
# node_by_id = {n["id"]: n for n in nodes}
# node_type = {n["id"]: n["type"] for n in nodes}

# past_nodes = {n["id"]: n for n in nodes if n["type"] == "past"}
# target_nodes = {n["id"]: n for n in nodes if n["type"] == "target"}

# # ==================================================
# # BUILD PATH INDEX
# # ==================================================
# past_to_nus = defaultdict(set)
# nus_to_oulu = defaultdict(set)

# for e in edges:
#     src = e.get("from")
#     tgt = e.get("to")

#     if not src or not tgt:
#         continue

#     if node_type.get(src) == "past" and node_type.get(tgt) == "source":
#         past_to_nus[src].add(tgt)

#     if node_type.get(src) == "source" and node_type.get(tgt) == "target":
#         nus_to_oulu[src].add(tgt)

# # ==================================================
# # COLLAPSE: PAST → OULU
# # ==================================================
# collapsed_edges = defaultdict(set)

# for past_id, nus_set in past_to_nus.items():
#     for nus_id in nus_set:
#         for oulu_id in nus_to_oulu.get(nus_id, []):
#             collapsed_edges[past_id].add(oulu_id)

# # ==================================================
# # SIDEBAR FILTER
# # ==================================================
# st.sidebar.header("🎯 Filter")

# past_labels = {v["label"]: k for k, v in past_nodes.items()}

# selected_past_labels = st.sidebar.multiselect(
#     "Select Past Courses (optional)",
#     options=sorted(past_labels.keys())
# )

# if selected_past_labels:
#     selected_past_ids = {past_labels[l] for l in selected_past_labels}
# else:
#     selected_past_ids = set(past_nodes.keys())

# # ==================================================
# # TABLE DATA
# # ==================================================
# past_rows = []
# oulu_rows = []

# for pid in selected_past_ids:
#     past_rows.append({
#         "ID": pid,
#         "Course": past_nodes[pid]["label"],
#         "Mapped Oulu Courses": len(collapsed_edges.get(pid, []))
#     })

# mapped_oulu_ids = set()
# for pid in selected_past_ids:
#     mapped_oulu_ids |= collapsed_edges.get(pid, set())

# for tid in mapped_oulu_ids:
#     oulu_rows.append({
#         "ID": tid,
#         "Course": target_nodes[tid]["label"]
#     })

# # ==================================================
# # TABLE VIEW
# # ==================================================
# st.subheader("📋 Course Tables")

# tab_past, tab_oulu = st.tabs(["🟦 Past Courses", "🟩 Oulu Courses"])

# with tab_past:
#     st.dataframe(past_rows, use_container_width=True)

# with tab_oulu:
#     st.dataframe(oulu_rows, use_container_width=True)

# # ==================================================
# # GRAPH
# # ==================================================
# dot = Digraph(
#     format="png",
#     graph_attr={
#         "rankdir": "LR",
#         "splines": "ortho",
#         "nodesep": "1.0",
#         "ranksep": "1.5"
#     }
# )

# # Colors
# PAST_COLOR = "#E8F0FE"
# OULU_COLOR = "#E6F4EA"

# # Add nodes
# for pid in selected_past_ids:
#     dot.node(pid, past_nodes[pid]["label"], shape="box", style="filled", fillcolor=PAST_COLOR)

# for tid in mapped_oulu_ids:
#     dot.node(tid, target_nodes[tid]["label"], shape="box", style="filled", fillcolor=OULU_COLOR)

# # Add collapsed edges
# for pid in selected_past_ids:
#     for tid in collapsed_edges.get(pid, []):
#         dot.edge(pid, tid, label="equivalent")

# # ==================================================
# # RENDER
# # ==================================================
# st.subheader("🧭 Collapsed Transfer Graph (Past → Oulu)")
# st.graphviz_chart(dot)

# # ==================================================
# # STATS
# # ==================================================
# with st.expander("📈 Mapping Statistics"):
#     st.write({
#         "past_courses_displayed": len(selected_past_ids),
#         "oulu_courses_mapped": len(mapped_oulu_ids),
#         "total_mappings": sum(len(v) for v in collapsed_edges.values())
#     })

# # ==================================================
# # DEBUG (OPTIONAL)
# # ==================================================
# with st.expander("🛠 Path Debug (Past → NUS → Oulu)"):
#     debug = []
#     for p, nus_set in past_to_nus.items():
#         for n in nus_set:
#             for o in nus_to_oulu.get(n, []):
#                 debug.append({
#                     "Past": node_by_id[p]["label"],
#                     "Via NUS": node_by_id[n]["label"],
#                     "Oulu": node_by_id[o]["label"]
#                 })
#     st.dataframe(debug, use_container_width=True)


# import streamlit as st
# from pathlib import Path
# import json
# from graphviz import Digraph

# # ==================================================
# # PAGE CONFIG
# # ==================================================
# st.set_page_config(
#     page_title="Past → Oulu Course Mapping Viewer",
#     layout="wide"
# )

# st.title("🎓 Past → Oulu Course Mapping")
# st.caption("Visualization of direct and indirect transfer paths from Past Courses to Oulu Courses")

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
# # NODE TYPE LOOKUP
# # ==================================================
# node_by_id = {n["id"]: n for n in nodes}
# node_type = {n["id"]: n["type"] for n in nodes}

# # ==================================================
# # FILTER: KEEP ONLY PAST + TARGET (OULU)
# # ==================================================
# visible_nodes = [
#     n for n in nodes
#     if n["type"] in {"past", "target"}
# ]

# visible_node_ids = {n["id"] for n in visible_nodes}

# # ==================================================
# # FILTER EDGES:
# #   Allow:
# #     past -> target
# #     past -> past (if chaining exists)
# #     target -> target (rare but safe)
# #   Block anything touching "source"
# # ==================================================
# visible_edges = []

# for e in edges:
#     src, tgt = e["from"], e["to"]

#     if src not in visible_node_ids or tgt not in visible_node_ids:
#         continue

#     visible_edges.append(e)

# # ==================================================
# # BUILD TABLE DATA
# # ==================================================
# past_rows = []
# target_rows = []

# for node in visible_nodes:
#     row = {
#         "ID": node["id"],
#         "Label": node["label"]
#     }

#     if node["type"] == "past":
#         past_rows.append(row)
#     elif node["type"] == "target":
#         target_rows.append(row)

# # ==================================================
# # TABLE VIEW
# # ==================================================
# st.subheader("📋 Course Tables")

# tab_past, tab_target = st.tabs(["🟦 Past Courses", "🟩 Oulu Courses"])

# with tab_past:
#     if past_rows:
#         st.dataframe(past_rows, use_container_width=True)
#     else:
#         st.info("No past courses available.")

# with tab_target:
#     if target_rows:
#         st.dataframe(target_rows, use_container_width=True)
#     else:
#         st.info("No Oulu courses available.")

# # ==================================================
# # GRAPH SETUP
# # ==================================================
# dot = Digraph(
#     format="png",
#     graph_attr={
#         "rankdir": "LR",
#         "splines": "ortho",
#         "nodesep": "1.0",
#         "ranksep": "1.5"
#     }
# )

# # ==================================================
# # COLOR MAP
# # ==================================================
# COLOR_BY_TYPE = {
#     "past": "#E8F0FE",     # Blue
#     "target": "#E6F4EA"   # Green
# }

# # ==================================================
# # ADD NODES
# # ==================================================
# for node in visible_nodes:
#     dot.node(
#         node["id"],
#         node["label"],
#         shape="box",
#         style="filled",
#         fillcolor=COLOR_BY_TYPE.get(node["type"], "#FFFFFF")
#     )

# # ==================================================
# # ADD EDGES
# # ==================================================
# for edge in visible_edges:
#     dot.edge(
#         edge["from"],
#         edge["to"],
#         label=edge.get("relation", "")
#     )

# # ==================================================
# # GRAPH RENDER
# # ==================================================
# st.subheader("🧭 Past → Oulu Course Mapping Graph")
# st.graphviz_chart(dot)

# # ==================================================
# # METADATA & STATS
# # ==================================================
# with st.expander("📌 Graph Metadata"):
#     st.json(metadata)

# with st.expander("📈 Graph Statistics"):
#     st.write({
#         "visible_nodes": len(visible_nodes),
#         "visible_edges": len(visible_edges),
#         "past_courses": len(past_rows),
#         "oulu_courses": len(target_rows),
#     })

# # ==================================================
# # RAW JSON (OPTIONAL)
# # ==================================================
# with st.expander("🗂 Raw JSON"):
#     st.json(graph_data)

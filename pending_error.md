Great, this is the **right diagnostic question** 👍
I’ll answer it in a **very concrete, actionable way**, tied **directly** to your current `Global_Course_Mapping.py`.

---

## TL;DR (Executive answer)

You **do NOT need to fix your Python code yet**.

You need to fix **how meaning is encoded in JSON**, specifically:

👉 **You must fix `data/past_courses/*.json`**
👉 **You must NOT touch `data/mappings/*.json` for this issue**
👉 **You must NOT encode abstract concepts (like `PAST_Calculus`) as real courses**

Your current confusion comes from **JSON semantics**, not visualization logic.

---

# 1️⃣ What your current Global_Course_Mapping.py actually does

Let’s be explicit about what your code **is designed to visualize**:

### Your current graph shows **ONLY this layer**:

```
NUS source courses  →  Oulu target courses
```

Specifically:

* Nodes come from:

  * `source_courses_index.json`
  * `mapping_index.json`
  * `data/mappings/*.json`
* It **does not read**:

  * `data/past_courses/`
  * `direct_oulu_links`
  * Coursera courses
  * abstract prerequisites

✅ So your code is **correct for what it’s intended to do**.

---

# 2️⃣ Where the confusion is REALLY coming from

The confusion comes from **incorrect modeling inside `past_courses/*.json`**, not from this page.

You currently have **three different ideas mixed together**:

| Thing                             | What it SHOULD be     | Where it SHOULD live                |
| --------------------------------- | --------------------- | ----------------------------------- |
| PAST_Calculus                     | abstract prerequisite | **NOT a course JSON**               |
| Calculus: Single Variable (UPenn) | evidence              | `past_courses/*.json`               |
| Quantum Mechanics I               | target course         | `target_courses/oulu/` or readiness |

But right now, they are being **implicitly treated as the same kind of node**.

---

# 3️⃣ Which JSON files you MUST fix (precisely)

## ✅ Files you SHOULD fix

### 🔧 1. `data/past_courses/*.json`  ← **MAIN FIX**

These files must be corrected so that:

* They **ONLY contain evidence**
* They **DO NOT imply equivalence**
* They **DO NOT act like prerequisites nodes**

### Example: ❌ what to REMOVE / avoid

```json
{
  "course_code": "PAST_Calculus",
  "course_name": "Calculus"
}
```

🚫 This should **never exist** as a course.

---

### Example: ✅ correct structure for `past_courses`

```json
{
  "nus_course_code": "ESP2107",
  "nus_course_name": "Numerical Methods and Statistics",

  "past_courses": [
    {
      "provider": "Coursera",
      "course_name": "Calculus: Single Variable",
      "institution": "University of Pennsylvania",
      "evidence_for": ["calculus"]
    }
  ]
}
```

📌 Notice:

* No `PAST_Calculus` node
* Calculus is **evidence**, not a graph destination
* No Oulu course mentioned here

---

### 🔧 2. `direct_oulu_links.json` (or move into `past_courses/`)

You currently have:

```
direct_oulu_links.json
```

This file **should not exist as a global standalone file**.

✅ It should be **moved into the relevant `past_courses/*.json`**, for example:

```
data/past_courses/PC3235B.json
```

Because **Quantum Mechanics readiness is justified by physics exposure**, not globally.

---

## ❌ Files you should NOT change for this issue

### 🚫 Do NOT modify these (they are correct)

| File                         | Reason                                          |
| ---------------------------- | ----------------------------------------------- |
| `data/mappings/*.json`       | These are **credit equivalence**, not readiness |
| `mapping_index.json`         | Registry is correct                             |
| `source_courses_index.json`  | Correct abstraction                             |
| `target_courses/oulu/*.json` | These are authoritative Oulu courses            |
| `Global_Course_Mapping.py`   | Logic matches data model                        |

---

# 4️⃣ Why Quantum Mechanics felt “wrong” in your graph

Because **Quantum Mechanics should NEVER appear in this graph yet**.

Your current page is:

> **Global Source → Target Course Graph**

Quantum Mechanics I–III are:

* ❌ NOT mapped from NUS courses
* ❌ NOT transfer-equivalent
* ✅ Only *future readiness targets*

So they should:

* NOT appear in `mappings/*.json`
* NOT appear in `Global_Course_Mapping.py`

They belong in a **different graph**:

> *Readiness / Prerequisite Graph*

---

# 5️⃣ Final authoritative rule set (memorize this)

### 🔵 `past_courses/*.json`

* Coursera
* Prior learning
* Evidence only
* NEVER point to Oulu directly

### 🟡 `mappings/*.json`

* Formal credit equivalence only
* NUS → Oulu
* Reviewed by committees

### 🟢 `target_courses/oulu/*.json`

* Canonical Oulu curriculum
* No provenance logic

### 🔴 Abstract concepts (`PAST_Calculus`)

* **Do not serialize as JSON**
* Generate dynamically if needed
* Use only in a **separate prerequisite graph**

---

# 6️⃣ What to do next (concrete steps)

### Step 1 (mandatory)

Fix **all files in**:

```
data/past_courses/
```

Remove:

* abstract prerequisite nodes
* implied equivalence
* Oulu course mentions unless clearly marked as *readiness*

### Step 2 (recommended)

Remove:

```
direct_oulu_links.json
```

and move its content into:

```
data/past_courses/PC3235B.json
```

### Step 3 (later, optional)

Create a **new page**:

```
6_Prerequisite_and_Readiness_Graph.py
```

This is where:

* PAST_Calculus
* Quantum readiness
* Evidence chains belong

---

## If you want, I can next:

1. Rewrite **one past_courses JSON correctly** with you
2. Design the **separate readiness graph**
3. Add code guards to prevent invalid edges
4. Create a **semantic validator** for your JSONs

Just tell me which one you want to do first.

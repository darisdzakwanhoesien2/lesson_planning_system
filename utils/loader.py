import json
from pathlib import Path

def load_courses(folder: Path, course_type: str):
    """
    course_type: 'source' or 'target'
    """
    courses = {}

    if not folder.exists():
        return courses

    key_map = {
        "source": "source_course",
        "target": "target_course"
    }

    root_key = key_map[course_type]

    for file in folder.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            if root_key not in data:
                raise ValueError(
                    f"{file.name} does not follow {course_type}_course schema"
                )

            code = data[root_key]["code"]
            courses[code] = data

    return courses


# import json
# from pathlib import Path

# def load_courses(folder: Path):
#     courses = {}
#     if not folder.exists():
#         return courses

#     for file in folder.glob("*.json"):
#         with open(file, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             code = data["source_course"]["code"]
#             courses[code] = data
#     return courses
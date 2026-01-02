def summarize_course(course):
    src = course["source_course"]
    return {
        "code": src["code"],
        "name": src["name"],
        "credits": src["credits"],
        "level": src["level"],
        "orientation": src["academic_orientation"],
    }

def extract_learning_gaps(course):
    gaps = []
    for match in course["coursera_equivalents"]["closest_overall_matches"]:
        gaps.extend(match["reasoning"].get("gap_analysis", []))
    return list(set(gaps))
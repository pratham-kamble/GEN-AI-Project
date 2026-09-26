from typing import List, Dict


def build_skill_gap_report(matching_skills: List[str], missing_skills: List[str]) -> Dict[str, List[str]]:
    """
    Structures the skill-gap analysis for a candidate — matching vs missing
    skills relative to the job's required + preferred skill sets.
    """
    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "gap_count": len(missing_skills),
    }
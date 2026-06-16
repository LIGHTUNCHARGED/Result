import json
import os
import re

# Workspace directory
workspace_dir = os.path.dirname(os.path.abspath(__file__))

sem1_txt_path = os.path.join(workspace_dir, "Gazette Report B Tech Sem 1 2025-26.txt")
sem2_txt_path = os.path.join(workspace_dir, "Gazette Report B Tech Sem 2 2025-26.txt")

sem1_json_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Results.json")
sem1_js_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Results.js")

sem2_json_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Sem2_Results.json")
sem2_js_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Sem2_Results.js")

profiles_js_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Profiles.js")

# Comprehensive course name mapping
COURSE_NAMES = {
    # Semester 1 Foundation Courses
    "FCCH0103": "Environmental Science and Green Chemistry",
    "FCCH008": "Environmental Science and Green Chemistry",
    "FCCS0102": "Computer Programming",
    "FCCS002": "Computer Programming",
    "FCEC0116": "Electronics Engineering",
    "FCEC0106": "Electronics Engineering",
    "FCEC003": "Electronics Engineering",
    "FCEE0106": "Basic Electrical Engineering",
    "FCHS0105": "English / Communication Skills",
    "FCHS005": "English / Communication Skills",
    "FCME0116": "Basics of Mechanical Engineering",
    "FCME0106": "Basics of Mechanical Engineering",
    "FCME006": "Basics of Mechanical Engineering",
    "FCMT0101": "Mathematics-I",
    "FCMT001": "Mathematics-I",
    "FCMT007": "Mathematics-I",
    "FCMT0201": "Applied Mathematics-II",
    "FCPH0104": "Introduction to Electromagnetic Theory",
    "FCPH0114": "Quantum Physics",
    "FCPH0124": "Introduction to Electromagnetic Theory",
    "FCPH004": "Introduction to Electromagnetic Theory",
    "FCCW0106": "Python Programming",
    "FEPD001": "Physical Education / Value Education",
    "FEPD015": "Physical Education / Value Education",
    "VAPD0101": "Yoga and Meditation",
    "VAPD0115": "Yoga and Meditation",
    
    # Semester 2 Core Courses
    # BioTech
    "BTBTC203": "Introduction to Biotechnology",
    "BTCHC202": "Advance Chemistry",
    "BTPHC201": "Physics of Materials",
    # CSAI
    "CACSC201": "Discrete Structures",
    "CACSC202": "Data Structures",
    "CAECC203": "Digital Logic Design",
    # CSE
    "COCSC201": "Discrete Structures",
    "COCSC202": "Data Structures",
    "COECC203": "Digital Logic Design",
    # CS-DS
    "CDCSC201": "Discrete Structures",
    "CDCSC202": "Data Structures",
    "CDECC203": "Digital Logic Design",
    # CS-BDA
    "CBCPC201": "Discrete Structures",
    "CBCPC202": "Data Structures",
    "CBEPC203": "Digital Logic Design",
    # CS-IoT
    "CICPC201": "Discrete Structures",
    "CICPC202": "Data Structures",
    "CIEPC203": "Digital Logic Design",
    # MAC
    "CMCSC203": "Discrete Structures",
    "CMCSC204": "Data Structures",
    "CMPHC201": "Physics of Materials",
    # IT
    "ITITC201": "Data Structures",
    "ITITC202": "Discrete Structures",
    "ITECC203": "Digital Logic Design",
    # IT-NIS
    "INITC201": "Data Structures",
    "INITC202": "Discrete Structures",
    "INECC203": "Digital Logic Design",
    # ECE / VLSI / ECE-AIML / Voc
    "ECECC201": "Network Analysis and Synthesis",
    "ECECC202": "Electronic Devices and Circuits",
    "ECITC203": "Data Structures and Algorithms",
    "EACPC203": "Data Structures and Algorithms",
    "EAEPC201": "Network Analysis and Synthesis",
    "EAEPC202": "Electronic Devices and Circuits",
    "EIECC201": "Electronic Devices and Circuits",
    "EIECC202": "Network Analysis and Synthesis",
    "VTECC201": "Network Analysis and Synthesis",
    "VTECC202": "Electronic Devices and Circuits",
    "VTITC203": "Data Structures and Algorithms",
    # EE
    "EEEEC201": "Network Analysis & Synthesis",
    "EEEEC202": "Electrical Measurements",
    "EEECC203": "Analog and Digital Electronics",
    # ICE
    "ICICC201": "Electrical Circuits Analysis",
    "ICECC202": "Electronic Devices and Circuits",
    "ICICC203": "Electrical Measurements",
    # ME
    "MEMEC201": "Engineering Mechanics",
    "MEMEC202": "Engineering Materials & Metallurgy",
    "MEMEC203": "Engineering & Machine Drawing",
    # ME-EV
    "MVMWC201": "Engineering Mechanics",
    "MVMWC202": "Thermal Engineering - I",
    "MVMWC203": "Mechanical & Electrical Drawing",
    # Civil
    "CECWC201": "Strength of Materials",
    "CECWC202": "Surveying",
    "CECWC203": "Basic Fluid Mechanics",
    # Geoinformatics
    "CGCWC201": "Principles of Photogrammetry and Photo Interpretation",
    "CGCWC202": "Fundamentals of Remote Sensing",
    "CGCWC203": "Surveying"
}

def is_roll_no(s):
    return bool(re.match(r"^\d{4}U[A-Z]+\d+$", s))

def clean_name(s):
    s = re.sub(r"[^A-Z\s\.\-]", "", s)
    return s.strip()

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_course_name(code):
    return COURSE_NAMES.get(code, f"{code} Course")

def parse_gazette(txt_path):
    print(f"Parsing gazette from: {os.path.basename(txt_path)}")
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"PageNo:\d+", content)
    if pages and not pages[0].strip():
        pages = pages[1:]

    students_list = []

    for page_idx, page_text in enumerate(pages):
        page_num = page_idx + 1
        
        # Extract Branch
        branch_match = re.search(r"Semester:\s*\d+\s*-\s*(.*?)\s+examination held in", page_text)
        branch = branch_match.group(1).strip() if branch_match else None
        if not branch:
            branch_match = re.search(r"B\.Tech\.\s*-\s*Semester:\s*\d+\s*-\s*(.*?)\s+examination", page_text)
            branch = branch_match.group(1).strip() if branch_match else "UNKNOWN BRANCH"
            
        raw_lines = [line.strip() for line in page_text.split("\n")]
        lines = [line for line in raw_lines if line]
        
        # Locate header end
        header_end_idx = -1
        for idx, line in enumerate(lines):
            if line == "CS":
                header_end_idx = idx
                break
                
        if header_end_idx == -1:
            continue
            
        body_lines = lines[header_end_idx + 1:]
        
        # Locate footer
        footer_idx = -1
        for idx, line in enumerate(body_lines):
            if line == "Sl" and idx + 1 < len(body_lines) and body_lines[idx+1] == "Roll No":
                footer_idx = idx
                break
                
        footer_lines = []
        if footer_idx != -1:
            footer_lines = body_lines[footer_idx:]
            body_lines = body_lines[:footer_idx]
            
        # Get footer roll number for the first student on the page
        footer_roll = None
        for line in footer_lines:
            if is_roll_no(line):
                footer_roll = line
                break
                
        # Split body into student blocks by roll numbers
        roll_indices = [idx for idx, line in enumerate(body_lines) if is_roll_no(line)]
        
        candidate_blocks = []
        if roll_indices:
            candidate_blocks.append(body_lines[:roll_indices[0]])
            for i in range(len(roll_indices)):
                start_idx = roll_indices[i]
                end_idx = roll_indices[i+1] if i + 1 < len(roll_indices) else len(body_lines)
                candidate_blocks.append(body_lines[start_idx:end_idx])
        else:
            candidate_blocks.append(body_lines)
            
        # Parse blocks
        for block_idx, block in enumerate(candidate_blocks):
            # Clean leading serial numbers
            while block and block[0].isdigit() and len(block[0]) < 4:
                block = block[1:]
                
            if not block:
                continue
                
            roll = None
            if is_roll_no(block[0]):
                roll = block[0]
                block = block[1:]
            elif block_idx == 0:
                roll = footer_roll
                
            if roll is None:
                continue
                
            if not roll.startswith("2025U"):
                continue
                
            clean_block_lines = [l.strip() for l in block if l.strip()]
            if len(clean_block_lines) < 6:
                continue
                
            name = clean_name(clean_block_lines[0])
            father = clean_name(clean_block_lines[1]) if len(clean_block_lines) > 1 else "UNKNOWN"
            
            # Locate summary stats using backward search
            stats_idx = -1
            for i in range(len(clean_block_lines) - 4, 1, -1):
                tot_cr_val = clean_block_lines[i]
                tot_crp_val = clean_block_lines[i+1]
                sgpa_val = clean_block_lines[i+2]
                cs_val = clean_block_lines[i+3]
                
                if tot_cr_val.isdigit() and 1 <= int(tot_cr_val) <= 35:
                    if (tot_crp_val.isdigit() or tot_crp_val == "RL") and \
                       (is_float(sgpa_val) or sgpa_val == "RL") and \
                       (cs_val.isdigit() or cs_val == "RL"):
                        if sgpa_val == "RL" or "." in sgpa_val:
                            stats_idx = i
                            break
                            
            if stats_idx == -1:
                continue
                
            tot_cr = int(clean_block_lines[stats_idx])
            tot_crp = clean_block_lines[stats_idx+1]
            sgpa_str = clean_block_lines[stats_idx+2]
            cs = clean_block_lines[stats_idx+3]
            
            sgpa = 0.0 if sgpa_str == "RL" else float(sgpa_str)
            
            # Extract courses
            course_lines = clean_block_lines[2:stats_idx]
            courses = []
            c_idx = 0
            while c_idx < len(course_lines):
                # Search for course code pattern
                if re.match(r'^[A-Z]{2,5}\d{3,4}$', course_lines[c_idx]):
                    code = course_lines[c_idx]
                    credits = int(course_lines[c_idx+1]) if c_idx+1 < len(course_lines) and course_lines[c_idx+1].isdigit() else 0
                    grade = course_lines[c_idx+2] if c_idx+2 < len(course_lines) else "RL"
                    gp_val = course_lines[c_idx+3] if c_idx+3 < len(course_lines) else "0"
                    gp = float(gp_val) if is_float(gp_val) else 0.0
                    crp = course_lines[c_idx+4] if c_idx+4 < len(course_lines) else "0"
                    
                    courses.append({
                        "code": code,
                        "name": get_course_name(code),
                        "credits": credits,
                        "grade": grade,
                        "gp": gp,
                        "crp": crp
                    })
                    c_idx += 5
                else:
                    c_idx += 1
            
            students_list.append({
                "rollNo": roll,
                "name": name,
                "father": father,
                "branch": branch,
                "sgpa": sgpa,
                "sgpa_str": sgpa_str,
                "tot_cr": tot_cr,
                "tot_crp": tot_crp,
                "cs": int(cs) if cs.isdigit() else 0,
                "courses": courses
            })
            
    print(f"Successfully parsed {len(students_list)} student records.")
    return students_list

def calculate_ranks_and_percentiles(students, key_func, rank_field, pct_field):
    # Sort students by score descending, handling tie-breakers
    # Filter out RL/0.0 values for ranking order, but keep them at the bottom
    ranked_students = [s for s in students if key_func(s) > 0]
    unranked_students = [s for s in students if key_func(s) <= 0]
    
    ranked_students.sort(key=key_func, reverse=True)
    
    # Calculate global ranks
    current_rank = 1
    for idx, student in enumerate(ranked_students):
        if idx > 0 and key_func(student) == key_func(ranked_students[idx - 1]):
            student[rank_field] = ranked_students[idx - 1][rank_field]
        else:
            student[rank_field] = idx + 1
            
    for student in unranked_students:
        student[rank_field] = len(ranked_students) + 1
        
    # Calculate global percentiles
    total_valid = len(ranked_students)
    if total_valid > 0:
        for student in students:
            score = key_func(student)
            if score <= 0:
                student[pct_field] = 0.0
            else:
                count_lower_equal = sum(1 for s in ranked_students if key_func(s) <= score)
                student[pct_field] = round((count_lower_equal / total_valid) * 100, 2)
    else:
        for student in students:
            student[pct_field] = 0.0
            
    # Calculate branch ranks and branch percentiles
    branches = {}
    for student in students:
        br = student["branch"]
        if br not in branches:
            branches[br] = []
        branches[br].append(student)
        
    for br_name, br_students in branches.items():
        br_ranked = [s for s in br_students if key_func(s) > 0]
        br_unranked = [s for s in br_students if key_func(s) <= 0]
        
        br_ranked.sort(key=key_func, reverse=True)
        
        # Branch ranks
        for idx, student in enumerate(br_ranked):
            if idx > 0 and key_func(student) == key_func(br_ranked[idx - 1]):
                student[f"{rank_field}Branch"] = br_ranked[idx - 1][f"{rank_field}Branch"]
            else:
                student[f"{rank_field}Branch"] = idx + 1
                
        for student in br_unranked:
            student[f"{rank_field}Branch"] = len(br_ranked) + 1
            
        # Branch percentiles
        br_total_valid = len(br_ranked)
        if br_total_valid > 0:
            for student in br_students:
                score = key_func(student)
                if score <= 0:
                    student[f"{pct_field}Branch"] = 0.0
                else:
                    count_lower_equal = sum(1 for s in br_ranked if key_func(s) <= score)
                    student[f"{pct_field}Branch"] = round((count_lower_equal / br_total_valid) * 100, 2)
        else:
            for student in br_students:
                student[f"{pct_field}Branch"] = 0.0

def main():
    # 1. Parse both gazettes
    sem1_students = parse_gazette(sem1_txt_path)
    sem2_students = parse_gazette(sem2_txt_path)
    
    # 2. Calculate SGPA ranks and percentiles
    calculate_ranks_and_percentiles(sem1_students, lambda s: s["sgpa"], "rank", "pct")
    calculate_ranks_and_percentiles(sem2_students, lambda s: s["sgpa"], "rank", "pct")
    
    # Write Sem 1 JSON & JS files
    sem1_results_output = []
    for idx, student in enumerate(sorted(sem1_students, key=lambda s: s["sgpa"], reverse=True)):
        sem1_results_output.append({
            "SNo": idx + 1,
            "Global Rank": student["rank"],
            "Branch Rank": student["rankBranch"],
            "Name": student["name"],
            "Roll No": student["rollNo"],
            "SGPA": student["sgpa"],
            "Branch": student["branch"]
        })
    
    with open(sem1_json_path, "w", encoding="utf-8") as f:
        json.dump(sem1_results_output, f, indent=4)
    with open(sem1_js_path, "w", encoding="utf-8") as f:
        f.write("const sem1Data = " + json.dumps(sem1_results_output) + ";\n")
        
    # Write Sem 2 JSON & JS files
    sem2_results_output = []
    for idx, student in enumerate(sorted(sem2_students, key=lambda s: s["sgpa"], reverse=True)):
        sem2_results_output.append({
            "SNo": idx + 1,
            "Global Rank": student["rank"],
            "Branch Rank": student["rankBranch"],
            "Name": student["name"],
            "Roll No": student["rollNo"],
            "SGPA": student["sgpa"],
            "Branch": student["branch"]
        })
        
    with open(sem2_json_path, "w", encoding="utf-8") as f:
        json.dump(sem2_results_output, f, indent=4)
    with open(sem2_js_path, "w", encoding="utf-8") as f:
        f.write("const sem2Data = " + json.dumps(sem2_results_output) + ";\n")

    # 3. Create Merged Student Profiles
    sem1_map = {s["rollNo"]: s for s in sem1_students}
    sem2_map = {s["rollNo"]: s for s in sem2_students}
    
    all_rolls = set(sem1_map.keys()).union(sem2_map.keys())
    
    profiles = {}
    
    for roll in all_rolls:
        s1 = sem1_map.get(roll)
        s2 = sem2_map.get(roll)
        
        name = (s1["name"] if s1 else (s2["name"] if s2 else "UNKNOWN")).upper()
        father = (s1["father"] if s1 else (s2["father"] if s2 else "UNKNOWN")).upper()
        branch = s1["branch"] if s1 else (s2["branch"] if s2 else "UNKNOWN")
        
        sgpa1 = s1["sgpa"] if s1 else 0.0
        sgpa2 = s2["sgpa"] if s2 else 0.0
        
        # Weighted CGPA Formula
        cgpa = 0.0
        if sgpa1 > 0 and sgpa2 > 0:
            cgpa = ((20 * sgpa1) + (24 * sgpa2)) / 44
        elif sgpa1 > 0:
            cgpa = sgpa1
        elif sgpa2 > 0:
            cgpa = sgpa2
            
        cgpa = round(cgpa, 3)
        
        profiles[roll] = {
            "rollNo": roll,
            "name": name,
            "father": father,
            "branch": branch,
            "cgpa": cgpa,
            "sem1": {
                "present": s1 is not None,
                "sgpa": sgpa1,
                "sgpa_str": s1["sgpa_str"] if s1 else "RL",
                "tot_cr": s1["tot_cr"] if s1 else 0,
                "tot_crp": s1["tot_crp"] if s1 else "0",
                "cs": s1["cs"] if s1 else 0,
                "rank": s1["rank"] if s1 else 9999,
                "rankBranch": s1["rankBranch"] if s1 else 9999,
                "pct": s1["pct"] if s1 else 0.0,
                "pctBranch": s1["pctBranch"] if s1 else 0.0,
                "courses": s1["courses"] if s1 else []
            },
            "sem2": {
                "present": s2 is not None,
                "sgpa": sgpa2,
                "sgpa_str": s2["sgpa_str"] if s2 else "RL",
                "tot_cr": s2["tot_cr"] if s2 else 0,
                "tot_crp": s2["tot_crp"] if s2 else "0",
                "cs": s2["cs"] if s2 else 0,
                "rank": s2["rank"] if s2 else 9999,
                "rankBranch": s2["rankBranch"] if s2 else 9999,
                "pct": s2["pct"] if s2 else 0.0,
                "pctBranch": s2["pctBranch"] if s2 else 0.0,
                "courses": s2["courses"] if s2 else []
            }
        }
        
    # Calculate Overall CGPA Ranks and Percentiles on the profiles list
    profiles_list = list(profiles.values())
    calculate_ranks_and_percentiles(profiles_list, lambda s: s["cgpa"], "cgpaRank", "cgpaPct")
    
    # Re-map the lists with ranks/percentiles back to profiles dictionary
    for s in profiles_list:
        profiles[s["rollNo"]]["cgpaRank"] = s["cgpaRank"]
        profiles[s["rollNo"]]["cgpaRankBranch"] = s["cgpaRankBranch"]
        profiles[s["rollNo"]]["cgpaPct"] = s["cgpaPct"]
        profiles[s["rollNo"]]["cgpaPctBranch"] = s["cgpaPctBranch"]
        
    # Write Profiles JS file
    with open(profiles_js_path, "w", encoding="utf-8") as f:
        f.write("const studentProfiles = " + json.dumps(profiles) + ";\n")
        
    print(f"Generated {profiles_js_path} with {len(profiles)} detailed student profiles.")

if __name__ == "__main__":
    main()

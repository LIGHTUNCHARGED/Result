import json
import os
import re

# Use the directory where this script is located as the workspace directory
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sem2_txt_path = os.path.join(workspace_dir, "Gazette Report B Tech Sem 2 2025-26.txt")
sem2_json_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Sem2_Results.json")
sem2_js_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Sem2_Results.js")

sem1_json_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Results.json")
sem1_js_path = os.path.join(workspace_dir, "NSUT_Batch_2025_Results.js")

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

def extract_stats(block):
    for i in range(len(block) - 4, 1, -1):
        tot_cr_val = block[i]
        tot_crp_val = block[i+1]
        sgpa_val = block[i+2]
        cs_val = block[i+3]
        
        if tot_cr_val.isdigit() and 1 <= int(tot_cr_val) <= 35:
            if (tot_crp_val.isdigit() or tot_crp_val == "RL") and \
               (is_float(sgpa_val) or sgpa_val == "RL") and \
               (cs_val.isdigit() or cs_val == "RL"):
                if sgpa_val == "RL" or "." in sgpa_val:
                    return {
                        "TOT_CR": int(tot_cr_val),
                        "TOT_CRP": tot_crp_val,
                        "SGPA": sgpa_val,
                        "CS": cs_val
                    }
    return None

def parse_gazette_and_rank():
    with open(sem2_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"PageNo:\d+", content)
    if pages and not pages[0].strip():
        pages = pages[1:]

    raw_students = []

    for page_idx, page_text in enumerate(pages):
        page_num = page_idx + 1
        
        # Branch
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
            
        # Get footer roll numbers
        footer_roll = None
        for line in footer_lines:
            if is_roll_no(line):
                footer_roll = line
                break
                
        # Split body into candidate blocks by roll numbers
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
                
            if not block:
                continue
                
            name = clean_name(block[0])
            father = clean_name(block[1]) if len(block) > 1 else "UNKNOWN"
            
            stats = extract_stats(block)
            if not stats:
                print(f"Warning: Could not parse stats for {name} on Page {page_num}")
                continue
                
            sgpa_val = stats["SGPA"]
            tot_cr = stats["TOT_CR"]
            
            sgpa = 0.0 if sgpa_val == "RL" else float(sgpa_val)
            
            raw_students.append({
                "Roll No": roll,
                "Name": name,
                "Father's Name": father,
                "Branch": branch,
                "SGPA": sgpa,
                "Credits": tot_cr
            })

    print(f"Parsed {len(raw_students)} students from B.Tech 2025 batch.")

    raw_students.sort(key=lambda x: x["SGPA"], reverse=True)

    # 1. Calculate Global Ranks
    global_rank = 1
    for idx, student in enumerate(raw_students):
        if idx > 0 and student["SGPA"] == raw_students[idx - 1]["SGPA"]:
            student["Global Rank"] = raw_students[idx - 1]["Global Rank"]
        else:
            student["Global Rank"] = idx + 1

    # 2. Calculate Branch Ranks
    branches = {}
    for student in raw_students:
        branch = student["Branch"]
        if branch not in branches:
            branches[branch] = []
        branches[branch].append(student)

    for branch_name, branch_students in branches.items():
        branch_students.sort(key=lambda x: x["SGPA"], reverse=True)
        for idx, student in enumerate(branch_students):
            if idx > 0 and student["SGPA"] == branch_students[idx - 1]["SGPA"]:
                student["Branch Rank"] = branch_students[idx - 1]["Branch Rank"]
            else:
                student["Branch Rank"] = idx + 1

    # Format JSON output
    output_students = []
    for idx, student in enumerate(raw_students):
        output_students.append({
            "SNo": idx + 1,
            "Global Rank": student["Global Rank"],
            "Branch Rank": student["Branch Rank"],
            "Name": student["Name"],
            "Roll No": student["Roll No"],
            "SGPA": student["SGPA"],
            "Branch": student["Branch"]
        })

    # Write Sem 2 JSON
    with open(sem2_json_path, "w", encoding="utf-8") as f:
        json.dump(output_students, f, indent=4)
    print(f"Successfully generated {sem2_json_path} with {len(output_students)} records.")

    # Write Sem 2 JS
    with open(sem2_js_path, "w", encoding="utf-8") as f:
        f.write("const sem2Data = " + json.dumps(output_students) + ";\n")
    print(f"Successfully generated {sem2_js_path} for static loading.")

    # Convert Sem 1 JSON to Sem 1 JS
    if os.path.exists(sem1_json_path):
        with open(sem1_json_path, "r", encoding="utf-8") as f:
            sem1_data = json.load(f)
        with open(sem1_js_path, "w", encoding="utf-8") as f:
            f.write("const sem1Data = " + json.dumps(sem1_data) + ";\n")
        print(f"Successfully converted Sem 1 JSON to static {sem1_js_path}")
    else:
        print(f"Warning: Sem 1 JSON not found at {sem1_json_path}")

if __name__ == "__main__":
    parse_gazette_and_rank()

import os
from datetime import datetime
import re


# Base Directory*************************************
ROOT_PATH = r"D:\Transfers"

# company names**************************************
COMPANIES = [
    "AHH_AMO",
    "ANTHEM_ABC_MUSGROW",
    "TELADOC",
    "SAVRX"
]

# Default folders (used for ANTHEM)
FOLDERS = [
    "152", "480", "521", "HWL", "IWU", "J84", "L82",
    "L480", "LAF", "LBU", "OCU", "OEW",
    "P42", "S98", "TRI", "TRI_MED"
]

# ==============================
# DATE PARSE LOGIC
# ==============================

def safe_parse_date(date_str):
    """
    Safely converts string date into datetime object.

    Supports:
    - MM-DD-YYYY (primary)
    - DD-MM-YYYY (fallback)

    Returns datetime object OR None
    """
    try:
        # normal expected format
        return datetime.strptime(date_str, "%m-%d-%Y")
    except ValueError:
        try:
            # fallback: DD-MM-YYYY
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            return None


# DATE EXTRACTION LOGIC*****************************************************


# Company 1: AHH_AMO********************************************************

def extract_date_ahh_amo(filename):
    """
    Example:
    AHH_ABC_Elig_Full_250901123941.TXT

    Extracts:
    250901 -> 09-01-2025
    """

    name = filename.replace(".834", "").replace(".TXT", "")

    match = re.search(r"(\d{6})\d{6}$", name)
    if not match:
        return None

    date = match.group(1)
    yy, mm, dd = date[0:2], date[2:4], date[4:6]
    return f"{mm}-{dd}-20{yy}"



# # Company 2: ANTHEM_ABC_MUSGROW***************************************************************

# IMPORTANT: depends on FOLDERS defined in Module 1
FOLDER_LENGTH_MAP = {folder: len(folder) for folder in FOLDERS}


# def extract_date(filename, folder):
#     """
#     Standard extraction for ANTHEM folders.

#     Handles:
#     - Direct prefix match
#     - Special TRI_MED scanning logic
#     """

#     name = filename.replace(".834", "")

#     folder_len = FOLDER_LENGTH_MAP.get(folder)
#     if folder_len is None:
#         return None

#     # exact folder match at start
#     if name[:folder_len] != folder:
#         return None

#     date = name[folder_len:folder_len + 6]

#     if date.isdigit():
#         yy, mm, dd = date[0:2], date[2:4], date[4:6]
        
#         # Fix: Handle YYDDMM format where MM > 12
#         if int(mm) > 12 and int(dd) <= 12:
#             mm, dd = dd, mm
        
#         # Validate date
#         if int(mm) < 1 or int(mm) > 12 or int(dd) < 1 or int(dd) > 31:
#             return None

#         return f"{mm}-{dd}-20{yy}"
    
    

#     # ---- SPECIAL TRI_MED LOGIC (unchanged) ----
#     try:
#         if folder == "TRI_MED":
#             rest = name[folder_len:]
#             parts = rest.split("_")

#             for part in parts:
#                 for i in range(len(part) - 5):
#                     chunk = part[i:i+6]
#                     if chunk.isdigit():
#                         yy, mm, dd = chunk[0:2], chunk[2:4], chunk[4:6]
                        
#                         # Fix: Handle YYDDMM
#                         if int(mm) > 12 and int(dd) <= 12:
#                             mm, dd = dd, mm
                        
#                         # Validate
#                         if int(mm) < 1 or int(mm) > 12 or int(dd) < 1 or int(dd) > 31:
#                             pass # check next chunk
#                         else:
#                             return f"{mm}-{dd}-20{yy}"



    
#     except Exception:
#         pass

#     return None


# new logic for extraction 16-02-2026*************************************

def extract_date(filename, folder):
    """
    Standard extraction for ANTHEM folders.

    Handles:
    - YYMMDDHHMMSS
    - YYYYMMDDHHMMSS   <-- NEW FIX
    - Special TRI_MED scanning logic
    """

    name = filename.replace(".834", "")

    folder_len = FOLDER_LENGTH_MAP.get(folder)
    if folder_len is None:
        return None

    # exact folder match at start
    if name[:folder_len] != folder:
        return None

    # NEW FIX: HANDLE YYYYMMDDHHMMSS (14 digits)********************************************
    # Example: OCU20220106152506
  
    date_14 = name[folder_len:folder_len + 14]

    if len(date_14) == 14 and date_14.isdigit():

        yyyy = date_14[0:4]
        mm   = date_14[4:6]
        dd   = date_14[6:8]

        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
            return f"{mm}-{dd}-{yyyy}"


    # ORIGINAL 6 DIGIT LOGIC (YYMMDD)***************************************************

    date = name[folder_len:folder_len + 6]

    if date.isdigit():

        yy, mm, dd = date[0:2], date[2:4], date[4:6]

        # Handle YYDDMM format
        if int(mm) > 12 and int(dd) <= 12:
            mm, dd = dd, mm

        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
            return f"{mm}-{dd}-20{yy}"

 
    # SPECIAL TRI_MED LOGIC (unchanged)*************************************************

    try:
        if folder == "TRI_MED":

            rest = name[folder_len:]
            parts = rest.split("_")

            for part in parts:
                for i in range(len(part) - 5):
                    chunk = part[i:i+6]
                    if chunk.isdigit():

                        yy, mm, dd = chunk[0:2], chunk[2:4], chunk[4:6]

                        if int(mm) > 12 and int(dd) <= 12:
                            mm, dd = dd, mm

                        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
                            return f"{mm}-{dd}-20{yy}"

    except Exception:
        pass

    return None



# Company 3 : TELADOC********************************************
#****************************************************************

def extract_date_teladoc(filename):
    """
    Examples:
    MEITD_20240115.834
    TEST_MEITD_20240115.834

    Extracts YYYYMMDD -> MM-DD-YYYY
    """

    match = re.search(r"(\d{8})", filename)
    if not match:
        return None

    yyyymmdd = match.group(1)
    yyyy = yyyymmdd[0:4]
    mm   = yyyymmdd[4:6]
    dd   = yyyymmdd[6:8]

    return f"{mm}-{dd}-{yyyy}"



# Company 4 : SAVRX****************************************************
# *********************************************************************

# ---- helper (kept as-is) ----
def _fmt_date(mm, dd, yyyy):
    return f"{mm}-{dd}-{yyyy}"



# SAVRX Folder 1 : 480***************************************************


def extract_date_savrx_480(filename):
    name = filename.upper()
    name = name.split(".")[0]

    # CASE 1 : YYYYMMDD*********************
    m = re.search(r"IBEW480_(\d{8})$", name)
    if m:
        d = m.group(1)
        yyyy = d[0:4]
        mm   = d[4:6]
        dd   = d[6:8]
        return f"{mm}-{dd}-{yyyy}"

    # CASE 2 : YYMMDDHHMMSS******************
    m = re.search(r"IBEW480_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None



# SAVRX Folder 2 : 521*****************************************

def extract_date_savrx_521(filename):
    name = filename.upper()
    name = name.split(".")[0]

    # CASE 1 : YYYYMMDD***************************
    m = re.search(r"PP521_(\d{8})$", name)
    if m:
        d = m.group(1)
        yyyy = d[0:4]
        mm   = d[4:6]
        dd   = d[6:8]
        return f"{mm}-{dd}-{yyyy}"

    # CASE 2 : YYMMDDHHMMSS*************************
    m = re.search(r"PP521_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# SAVRX Folder 3 : J84*******************************************

def extract_date_savrx_j84(filename):
    name = filename.upper()
    name = name.split(".")[0]

    # CASE 1 : MMDDYY**********************
    m = re.search(r"J84_EDI(\d{6})$", name)
    if m:
        d = m.group(1)
        mm = d[0:2]
        dd = d[2:4]
        yy = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    # CASE 2 : YYMMDDHHMMSS*****************
    m = re.search(r"J84_EDI(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    # CASE 3 & 4 : _MMDDYY
    m = re.search(r"_(\d{6})$", name)
    if m:
        d = m.group(1)
        mm = d[0:2]
        dd = d[2:4]
        yy = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# SAVRX Folder 4 : L82****************************************************************

def extract_date_savrx_l82(filename):
    name = filename.upper()
    name = name.split(".")[0]

    # CASE 1 : YYYYMMDD
    m = re.search(r"L82EDI_(\d{8})$", name)
    if m:
        d = m.group(1)
        yyyy = d[0:4]
        mm = d[4:6]
        dd = d[6:8]
        return f"{mm}-{dd}-{yyyy}"

    # CASE 2 : YYMMDDHHMMSS
    m = re.search(r"L82EDI_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# SAVRX Folder 5 : MEI*******************************************************************

def extract_date_savrx_mei(filename):
    name = filename.upper()
    name = name.split(".")[0]

    # CASE 1 : MMDDYY
    m = re.search(r"_(\d{6})$", name)
    if m:
        d = m.group(1)
        mm = d[0:2]
        dd = d[2:4]
        yy = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    # CASE 2 : YYMMDDHHMMSS
    m = re.search(r"_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# SAVRX Folder 6 : OEW****************************************************************

def extract_date_savrx_oew(filename):
    name = filename.upper()
    name = name.split(".")[0]

    m = re.search(r"_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    m = re.search(r"_(\d{8})", name)
    if m:
        d = m.group(1)
        yyyy = d[0:4]
        mm = d[4:6]
        dd = d[6:8]
        return f"{mm}-{dd}-{yyyy}"

    return None


# SAVRX Folder 7 : TRI***************************************************************

def extract_date_savrx_tri(filename):
    name = filename.upper()
    name = name.split(".")[0]

    m = re.search(r"_(\d{6})$", name)
    if m:
        d = m.group(1)
        mm = d[0:2]
        dd = d[2:4]
        yy = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    m = re.search(r"_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# SAVRX Folder 8 : TRI_NONMEDICARE*****************************************************

def extract_date_savrx_tri_nonmedicare(filename):
    name = filename.upper()
    name = name.split(".")[0]

    m = re.search(r"_(\d{6})$", name)
    if m:
        d = m.group(1)
        mm = d[0:2]
        dd = d[2:4]
        yy = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    m = re.search(r"_(\d{6})\d{6}$", name)
    if m:
        d = m.group(1)
        yy = d[0:2]
        mm = d[2:4]
        dd = d[4:6]
        return f"{mm}-{dd}-20{yy}"

    return None


# MASTER SAVRX ROUTER************************************************

def extract_date_savrx(folder, filename):
    match folder:
        case "480":
            return extract_date_savrx_480(filename)
        case "521":
            return extract_date_savrx_521(filename)
        case "J84":
            return extract_date_savrx_j84(filename)
        case "L82":
            return extract_date_savrx_l82(filename)
        case "MEI":
            return extract_date_savrx_mei(filename)
        case "OEW":
            return extract_date_savrx_oew(filename)
        case "TRI":
            return extract_date_savrx_tri(filename)
        case "TRI_NONMEDICARE":
            return extract_date_savrx_tri_nonmedicare(filename)
        case _:
            return None


# 13-02-2026**********************************************************************
def is_date_in_range(file_date, start_date, end_date):
    """
    Strict Date Comparison
    file_date  -> always MM-DD-YYYY (from filename)
    start_date -> DD-MM-YYYY (from UI)
    end_date   -> DD-MM-YYYY (from UI)
    """

    try:
        file_dt = datetime.strptime(file_date, "%m-%d-%Y")
        start_dt = datetime.strptime(start_date.strip(), "%d-%m-%Y")
        end_dt = datetime.strptime(end_date.strip(), "%d-%m-%Y")

        return start_dt <= file_dt <= end_dt

    except Exception:
        return False


# NEW LOGIC 14-02-2026*********************************************************
def find_member_id_all_dates(base_path, folders, target_member_id, debug=False):
    present_records = []
    absent_records = []

    for folder in folders:
        if debug:
            print("Searching Folder :", folder)

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            date = extract_date(file, folder)
            if not date:
                continue

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

           
            if (
                f"REF*OF*{target_member_id}~" in content
                or f"REF*ABB*{target_member_id}~" in content
            ):
                present_records.append({
                    "date": date,
                    "filename": file
                })
            else:
                absent_records.append({
                    "date": date,
                    "filename": file
                })

            if debug:
                print("---------------------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        )
    )


# new logic 14-02-2026******************************************************
def find_member_id_all_dates_ahh_amo(base_path, target_member_id, debug=False):
    present_records = []
    absent_records = []

    backup_path = os.path.join(base_path, "backups")

    if debug:
        print("Backup Path :", backup_path)

    if not os.path.exists(backup_path):
        return [], []

    member_id_pattern = re.compile(
        rf"REF\*(0F|ABB)\*{re.escape(target_member_id)}(\*|~|\b)",
        re.IGNORECASE
    )

    for file in os.listdir(backup_path):

        if debug:
            print("Checking file for Member ID:", file)

        if not file.lower().endswith((".txt", ".834")):
            continue

        # SAME DATE EXTRACTION *********************************
        date = extract_date_ahh_amo(file)

        file_path = os.path.join(backup_path, file)

        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        found = False

        if member_id_pattern.search(content):
            if debug:
                print("Member ID match found:", target_member_id)
                print("File:", file)
                print("Extracted date:", date)

            found = True

        record = {
            "date": date,  # can be None
            "filename": file
        }

        if found:
            present_records.append(record)
        else:
            absent_records.append(record)

        if debug:
            print("-------------------------------------")

    # Safe date sorting (no skip if date is None)
    def safe_sort(records):
        return sorted(
            records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )

    return (
        safe_sort(present_records),
        safe_sort(absent_records)
    )


# new logic 14-02-2026******************************************************
# **************************************************************************

def find_member_id_all_dates_teladoc(
    base_path,
    folders,
    target_member_id,
    debug=False
):
    present_records = []
    absent_records = []

    # Exact same regex (unchanged)
    member_id_pattern = re.compile(
        rf"REF\*(0F|OF|ABB)\*{re.escape(target_member_id)}~",
        re.IGNORECASE
    )

    for folder in folders:

        if debug:
            print(f"Searching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Searching in File : {file}")
                print("-" * 95)

            if not file.endswith(".834"):
                continue

            # ---- DATE EXTRACTION **************************
            date = extract_date_teladoc(file)

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            # ---- COUNT MATCHES (unchanged behaviour) ----
            matches = member_id_pattern.findall(content)
            match_count = len(matches)

            record = {
                "date": date,
                "filename": file
            }

            if match_count > 0:
                present_records.append(record)
            else:
                absent_records.append(record)

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


# new logic : 14-02-2026********************************************************

def find_member_id_all_dates_savrx(
    base_path,
    folders,
    target_member_id,
    debug=False
):
    present_records = []
    absent_records = []

    # Exact flexible REF logic (unchanged)
    member_id_pattern = re.compile(
        rf"REF\*(0F|OF|ABB)\*{re.escape(target_member_id)}(\*|~|\b)",
        re.IGNORECASE
    )

    for folder in folders:

        if debug:
            print(f"\nSearching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")

        if debug:
            print(backup_path)

        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Searching in file : {file}")
                print("-" * 72)

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            # ---- DATE EXTRACTION (unchanged) ----
            date = extract_date_savrx(folder, file)

            # ---- MEMBER ID MATCH COUNT (unchanged behaviour) ----
            matches = member_id_pattern.findall(content)
            match_count = len(matches)

            record = {
                "date": date,
                "filename": file
            }

            if match_count > 0:

                if debug:
                    print(
                        f"Member ID {target_member_id} found "
                        f"{match_count} times in file : {file}"
                    )

                present_records.append(record)
            else:
                absent_records.append(record)

            if debug:
                print("------------------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


# MEMBER NAME SEARCH LOGIC**************************************************

MEMBER_NAME_PATTERN = re.compile(r"NM1\*IL\*1\*(.+?)\*{3,}")


# MEMBER NAME LOGIC : 14-02-2026**********************************************
def find_member_name_all_dates(
    base_path,
    folders,
    target_member_name,
    debug=False
):
    present_records = []
    absent_records = []

    target_name = target_member_name.upper().strip()

    for folder in folders:

        if debug:
            print(f"Searching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            date = extract_date(file, folder)
            if not date:
                continue

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = MEMBER_NAME_PATTERN.findall(content)

            found = False

            # Original matching behaviour preserved
            for name in matches:
                clean_name = name.replace("*", " ").strip()

                if clean_name.upper() == target_name:
                    found = True
                    break

            if found:
                present_records.append({
                    "date": date,
                    "filename": file
                })
            else:
                absent_records.append({
                    "date": date,
                    "filename": file
                })

            if debug:
                print("---------------------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        )
    )


# new logic 14-02-2026******************************************************

def find_member_name_all_dates_ahh_amo(
    base_path,
    target_member_name,
    debug=False
):
    present_records = []
    absent_records = []

    target_name = target_member_name.upper().strip()

    backup_path = os.path.join(base_path, "backups")

    if debug:
        print("Backup Path :", backup_path)

    if not os.path.exists(backup_path):
        return [], []

    for file in os.listdir(backup_path):

        if debug:
            print("Checking file for Member Name:", file)

        if not file.lower().endswith((".txt", ".834")):
            continue

        date = extract_date_ahh_amo(file)

        file_path = os.path.join(backup_path, file)

        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        matches = MEMBER_NAME_PATTERN.findall(content)

        found = False

        for raw_name in matches:
            clean_name = raw_name.replace("*", " ").strip()

            if clean_name.upper() == target_name:
                found = True
                break

        if found:
            present_records.append({
                "date": date,
                "filename": file
            })
        else:
            absent_records.append({
                "date": date,
                "filename": file
            })

        if debug:
            print("-------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )



# new logic 14-02-2026******************************************************

def find_member_name_all_dates_teladoc(
    base_path,
    folders,
    target_member_name,
    debug=False
):
    present_records = []
    absent_records = []

    target_name = target_member_name.upper().strip()

    for folder in folders:

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            date = extract_date_teladoc(file)

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = MEMBER_NAME_PATTERN.findall(content)

            found = False

            for raw_name in matches:
                clean_name = raw_name.replace("*", " ").strip()

                if clean_name.upper() == target_name:
                    found = True
                    break

            record = {
                "date": date,
                "filename": file
            }

            if found:
                present_records.append(record)
            else:
                absent_records.append(record)

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )



# new logic : 14-02-2026********************************************************
def find_member_name_all_dates_savrx(
    base_path,
    folders,
    target_member_name,
    debug=False
):
    present_records = []
    absent_records = []

    # normalize input (unchanged behaviour)
    target_name = target_member_name.upper().strip()

    for folder in folders:

        if debug:
            print(f"\nSearching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")

        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Searching in file : {file}")
                print("-" * 72)

            file_path = os.path.join(backup_path, file)

            # read ALL file types (unchanged behaviour)
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            # ---- DATE EXTRACTION (unchanged) ----
            date = extract_date_savrx(folder, file)

            # ---- MEMBER NAME MATCH COUNT (unchanged) ----
            matches = MEMBER_NAME_PATTERN.findall(content)
            match_count = 0

            for raw_name in matches:
                clean_name = raw_name.replace("*", " ").strip()

                if clean_name.upper() == target_name:
                    match_count += 1

            record = {
                "date": date,
                "filename": file
            }

            if match_count > 0:

                if debug:
                    print(
                        f"Member Name '{target_member_name}' found "
                        f"{match_count} times in file : {file}"
                    )

                present_records.append(record)
            else:
                absent_records.append(record)

            if debug:
                print("------------------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


# SSN SEARCH LOGIC*****************************************************
# *********************************************************************


# Exact same SSN pattern*********************
SSN_PATTERN = re.compile(
    r"NM1\*IL\*1\*.*?\*+34\*(\d{9})~"
)


# new logic 14-02-2026***********************************************************************
# *******************************************************************************************

def find_ssn_all_dates(
    base_path,
    folders,
    target_ssn,
    debug=False
):
    present_records = []
    absent_records = []

    for folder in folders:

        if debug:
            print("Searching in folder:", folder)

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            date = extract_date(file, folder)
            if not date:
                continue

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            # If SSN present
            if target_ssn in matches:
                present_records.append({
                    "date": date,
                    "filename": file
                })
            else:
                absent_records.append({
                    "date": date,
                    "filename": file
                })

            if debug:
                print("---------------------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
        )
    )


# new logic 14-02-2026******************************************************
def find_ssn_all_dates_ahh_amo(
    base_path,
    target_ssn,
    debug=False
):
    present_records = []
    absent_records = []

    backup_path = os.path.join(base_path, "backups")

    if not os.path.exists(backup_path):
        return [], []

    for file in os.listdir(backup_path):

        if debug:
            print("Checking file for SSN:", file)

        # Same behaviour: no extension restriction

        date = extract_date_ahh_amo(file)

        file_path = os.path.join(backup_path, file)

        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        matches = SSN_PATTERN.findall(content)

        found = False

        if target_ssn in matches:

            if debug:
                print("SSN match found:", target_ssn)
                print("File:", file)
                print("Extracted date:", date)

            found = True

        record = {
            "date": date,
            "filename": file
        }

        if found:
            present_records.append(record)
        else:
            absent_records.append(record)

        if debug:
            print("-------------------------------------")

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


#  new logic 14-02-2026******************************************************
def find_ssn_all_dates_teladoc(
    base_path,
    folders,
    target_ssn,
    debug=False
):
    present_records = []
    absent_records = []

    for folder in folders:

        if debug:
            print(f"Searching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Checking file : {file}")

            if not file.endswith(".834"):
                continue

            date = extract_date_teladoc(file)

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            record = {
                "date": date,
                "filename": file
            }

            if target_ssn in matches:
                present_records.append(record)
            else:
                absent_records.append(record)

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


# new logic : 14-02-2026************************************************

def find_ssn_all_dates_savrx(
    base_path,
    folders,
    target_ssn,
    debug=False
):
    present_records = []
    absent_records = []

    for folder in folders:

        if debug:
            print(f"\nSearching in Folder : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")

        if debug:
            print(backup_path)

        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Searching in file : {file}")
                print("-" * 72)

            # ---- DATE EXTRACTION (unchanged) ----
            date = extract_date_savrx(folder, file)

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            file_match_count = 0
            date_added = False

            for ssn in matches:
                if ssn == target_ssn:
                    file_match_count += 1

                    if not date_added:
                        date_added = True

            record = {
                "date": date,
                "filename": file
            }

            if file_match_count > 0:
                if debug:
                    print(
                        f"SSN {target_ssn} found "
                        f"{file_match_count} times in file : {file}"
                    )
                present_records.append(record)
            else:
                absent_records.append(record)

    return (
        sorted(
            present_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        ),
        sorted(
            absent_records,
            key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y") if x["date"] else datetime.min
        )
    )


# DATE RANGE SSN FETCH LOGIC*******************************************************
# *********************************************************************************


# ---------------------------------
# Company 1: ANTHEM_ABC_MUSGROW
# ---------------------------------

def find_all_ssns_in_date_range(
    base_path,
    folders,
    start_date,
    end_date,
    debug=False
):
    ssns_found = []

    for folder in folders:

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            file_date = extract_date(file, folder)
            if not file_date:
                continue

            if not is_date_in_range(file_date, start_date, end_date):
                continue

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            for ssn in matches:
                ssns_found.append(ssn)

    return sorted(ssns_found)


# ---------------------------------
# Company 2: AHH_AMO
# ---------------------------------

def find_all_ssns_in_date_range_ahh_amo(
    base_path,
    start_date,
    end_date,
    debug=False
):
    ssns_found = []

    backup_path = os.path.join(base_path, "backups")
    if not os.path.exists(backup_path):
        return []

    for file in os.listdir(backup_path):

        if not file.lower().endswith((".txt", ".834")):
            continue

        file_date = extract_date_ahh_amo(file)
        if not file_date:
            continue

        if not is_date_in_range(file_date, start_date, end_date):
            continue

        file_path = os.path.join(backup_path, file)

        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

            if debug:
                print("Checking file for date range SSN search:", file)

        matches = SSN_PATTERN.findall(content)

        for ssn in matches:
            ssns_found.append(ssn)

    return sorted(ssns_found)


# ---------------------------------
# Company 3: TELADOC
# ---------------------------------

def find_all_ssns_in_date_range_teladoc(
    base_path,
    folders,
    start_date,
    end_date,
    debug=False
):
    ssns_found = []

    for folder in folders:

        backup_path = os.path.join(base_path, folder, "backups")
        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if not file.endswith(".834"):
                continue

            file_date = extract_date_teladoc(file)
            if not file_date:
                continue

            if not is_date_in_range(file_date, start_date, end_date):
                continue

            file_path = os.path.join(backup_path, file)

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            for ssn in matches:
                ssns_found.append(ssn)

    return sorted(ssns_found)


# ---------------------------------
# Company 4: SAVRX
# ---------------------------------

def find_all_ssns_in_date_range_savrx(
    base_path,
    folders,
    start_date,
    end_date,
    debug=False
):
    ssns_found = []

    for folder in folders:

        if debug:
            print(f"\nSearching in Folder (Date Range) : {folder}")

        backup_path = os.path.join(base_path, folder, "backups")

        if debug:
            print(backup_path)

        if not os.path.exists(backup_path):
            continue

        for file in os.listdir(backup_path):

            if debug:
                print(f"Checking file : {file}")

            file_path = os.path.join(backup_path, file)

            # Folder-wise date extraction
            file_date = extract_date_savrx(folder, file)
            if not file_date:
                continue

            if not is_date_in_range(file_date, start_date, end_date):
                continue

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()

            matches = SSN_PATTERN.findall(content)

            for ssn in matches:
                ssns_found.append(ssn)

            if debug:
                print(
                    f"File Date {file_date} in range → "
                    f"SSNs found: {len(matches)}"
                )

    return sorted(ssns_found)


# new logic 14-02-2026 for the subfolders dropdown*****************************************************
# *****************************************************************************************************


def get_company_config(selected_company: str, selected_subfolder: str | None = None):

    if selected_company not in COMPANIES:
        raise ValueError(
            "Invalid company selection. "
            "Available companies: " + ", ".join(COMPANIES)
        )

    # 1️.ANTHEM
    if selected_company == "ANTHEM_ABC_MUSGROW":
        base_path = os.path.join(ROOT_PATH, "ANTHEM_ABC_MUSGROW", "834s")

        all_folders = FOLDERS.copy()
        active_folders = all_folders

        if selected_subfolder and selected_subfolder in all_folders:
            active_folders = [selected_subfolder]

    # 2️.AHH_AMO  FIXED
    elif selected_company == "AHH_AMO":
        base_path = os.path.join(ROOT_PATH, "AHH_AMO")

        # DEFINE SUBFOLDERS MANUALLY HERE
        all_folders = [" "]   # <-- yahi show hoga dropdown me isme folders hi nhi hai

        active_folders = all_folders
        if selected_subfolder and selected_subfolder in all_folders:
            active_folders = [selected_subfolder]

    # 3️.TELADOC  
    elif selected_company == "TELADOC":
        base_path = os.path.join(ROOT_PATH, "TELADOC")

        # Already predefined
        all_folders = ["MEI"]

        active_folders = all_folders
        if selected_subfolder and selected_subfolder in all_folders:
            active_folders = [selected_subfolder]

    # 4️.SAVRX
    elif selected_company == "SAVRX":
        base_path = os.path.join(ROOT_PATH, "SAVRX")

        all_folders = [
            "480", "521", "J84", "L82",
            "MEI", "OEW", "TRI", "TRI_NONMEDICARE"
        ]

        active_folders = all_folders

        if selected_subfolder and selected_subfolder in all_folders:
            active_folders = [selected_subfolder]

    else:
        raise ValueError("Invalid company.")

    # FLAGS (IMPORTANT)
    is_ahh_amo = selected_company == "AHH_AMO"
    is_teladoc = selected_company == "TELADOC"
    is_savrx = selected_company == "SAVRX"

    return {
        "selected_company": selected_company,
        "base_path": base_path,
        "active_folders": active_folders,
        "is_ahh_amo": is_ahh_amo,
        "is_teladoc": is_teladoc,
        "is_savrx": is_savrx
    }


# new logic for conclusion 14-02-2026*********************************************
#********************************************************************************* 

def generate_ssn_timeline_summary(present_records, absent_records):
    if not present_records and not absent_records:
        return "No records found."

    # Collect all dates with state*************************
    all_dates = {}

    for r in present_records:
        if r["date"]:
            all_dates[r["date"]] = "present"

    for r in absent_records:
        if r["date"] and r["date"] not in all_dates:
            all_dates[r["date"]] = "absent"

    if not all_dates:
        return "No valid dated records found."

    # Sort all dates chronologically
    try:
        sorted_dates = sorted(
            all_dates.keys(),
            key=lambda d: datetime.strptime(d, "%m-%d-%Y")
        )
    except Exception:
        # Fallback if sorting fails (though extract_date should prevent this)
        sorted_dates = sorted(all_dates.keys())

    summary_parts = []
    
    current_state = None
    missing_block = []

    # Helper to add event
    def add_event(text, type="info"):
        summary_parts.append(f"<li class='summary-{type}'>{text}</li>")

    for idx, date in enumerate(sorted_dates):
        state = all_dates[date]

        # FIRST ENTRY
        if idx == 0:
            if state == "present":
                add_event(f"Started on <b>{date}</b>", "success")
            else:
                missing_block = [date]
            current_state = state
            continue

        # SAME STATE CONTINUE
        if state == current_state:
            if state == "absent":
                missing_block.append(date)
            continue

        # STATE CHANGE: PRESENT → ABSENT
        if current_state == "present" and state == "absent":
            missing_block = [date]
            current_state = "absent"
            continue

        # STATE CHANGE: ABSENT → PRESENT
        if current_state == "absent" and state == "present":
            # Flush missing block
            if missing_block:
                count = len(missing_block)
                dates_str = ", ".join(missing_block) if count < 5 else f"{missing_block[0]} ... {missing_block[-1]}."
                add_event(f"Missing: {dates_str}", "warning")
            
            add_event(f"Restarted on <b>{date}</b>", "success")

            missing_block = []
            current_state = "present"
            continue

    # If ended in absent
    if current_state == "absent" and missing_block:
        count = len(missing_block)
        dates_str = ", ".join(missing_block) if count < 5 else f"{missing_block[0]} ... {missing_block[-1]}."
        add_event(f"Last File But SSN Absent : {dates_str}", "danger")

    # Show last present regardless of current state
    # if present_records:
    #     try:
    #         last_present = max(
    #             present_records,
    #             key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
    #         )["date"]
    #         add_event(f"Last Present Date: <b>{last_present}</b>", "info")
    #     except:
    #         pass

    # return f"<ul class='timeline-list'>{''.join(summary_parts)}</ul>"

    # new logic 16-02-2026******************************

    if present_records:
        try:
            # Filter only valid dates (ignore '-' or invalid)
            valid_present_records = [
                r for r in present_records
                if r["date"] and r["date"] != "-"
            ]

            if valid_present_records:
                last_present = max(
                    valid_present_records,
                    key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
                )["date"]

                add_event(f"Last Present Date: <b>{last_present}</b>", "info")

        except Exception:
            pass
    return f"<ul class='timeline-list'>{''.join(summary_parts)}</ul>"


# new logic for member id**********14-02-2026*******************************************
# **************************************************************************************

def generate_member_id_timeline_summary(present_records, absent_records):
    # Reuse the same logic, just label tweaks if needed, but the structure is generic enough
    # For now, I'll copy the logic to ensure distinct behavior if requested later.
    
    if not present_records and not absent_records:
        return "No records found."

    all_dates = {}
    for r in present_records:
        if r["date"]: all_dates[r["date"]] = "present"
    for r in absent_records:
        if r["date"] and r["date"] not in all_dates: all_dates[r["date"]] = "absent"

    if not all_dates:
        return "No valid dated records found."

    try:
        sorted_dates = sorted(
            all_dates.keys(),
            key=lambda d: datetime.strptime(d, "%m-%d-%Y")
        )
    except Exception:
        sorted_dates = sorted(all_dates.keys())

    summary_parts = []
    current_state = None
    missing_block = []

    def add_event(text, type="info"):
        summary_parts.append(f"<li class='summary-{type}'>{text}</li>")

    for idx, date in enumerate(sorted_dates):
        state = all_dates[date]

        if idx == 0:
            if state == "present":
                add_event(f"Member ID Started on <b>{date}</b>", "success")
            else:
                missing_block = [date]
            current_state = state
            continue

        if state == current_state:
            if state == "absent": missing_block.append(date)
            continue

        if current_state == "present" and state == "absent":
            missing_block = [date]
            current_state = "absent"
            continue

        if current_state == "absent" and state == "present":
            if missing_block:
                count = len(missing_block)
                dates_str = ", ".join(missing_block) if count < 5 else f"{missing_block[0]} ... {missing_block[-1]}."
                add_event(f"Missing: {dates_str}", "warning")
            
            add_event(f"Restarted on <b>{date}</b>", "success")
            missing_block = []
            current_state = "present"
            continue

    if current_state == "absent" and missing_block:
        count = len(missing_block)
        dates_str = ", ".join(missing_block) if count < 5 else f"{missing_block[0]} ... {missing_block[-1]}."
        add_event(f"Last File But SSN Absent : {dates_str}", "danger")

    # if present_records:
    #     try:
    #         last_present = max(
    #             present_records,
    #             key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
    #         )["date"]
    #         add_event(f"Last Present Date: <b>{last_present}</b>", "info")
    #     except:
    #         pass

    # new logic 16-02-2026******************
    if present_records:
        try:
            # Filter only valid dates (ignore '-' or invalid)
            valid_present_records = [
                r for r in present_records
                if r["date"] and r["date"] != "-"
            ]

            if valid_present_records:
                last_present = max(
                    valid_present_records,
                    key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y")
                )["date"]

                add_event(f"Last Present Date: <b>{last_present}</b>", "info")

        except Exception:
            pass


    return f"<ul class='timeline-list'>{''.join(summary_parts)}</ul>"


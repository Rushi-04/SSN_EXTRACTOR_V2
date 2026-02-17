from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from logic import *

app = FastAPI(title="834 Eligibility Search System")

# Serve static files (index.html)
app.mount("/static", StaticFiles(directory="."), name="static")


# ----------------------------
# Request Models
# ----------------------------

class CompanyRequest(BaseModel):
    company_name: str


class SubfolderRequest(BaseModel):
    subfolder_name: str | None = None


class SSNRequest(BaseModel):
    ssn: str


class MemberIdRequest(BaseModel):
    member_id: str


class MemberNameRequest(BaseModel):
    member_name: str


class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str


# ----------------------------
# GLOBAL STATE (same as your API class)
# ----------------------------
api_state = {
    "company": None,
    "subfolder": None,
    "config": None
}


# ----------------------------
# Serve Frontend
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------
# API: Select Company
# ----------------------------
@app.post("/select_company")
def select_company(req: CompanyRequest):
    try:
        api_state["company"] = req.company_name
        api_state["subfolder"] = None
        api_state["config"] = get_company_config(req.company_name)

        return {
            "success": True,
            "subfolders": api_state["config"]["active_folders"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ----------------------------
# API: Select Subfolder
# ----------------------------
@app.post("/select_subfolder")
def select_subfolder(req: SubfolderRequest):

    if not api_state["company"]:
        return {"success": False, "error": "Select company first."}

    try:
        api_state["subfolder"] = req.subfolder_name if req.subfolder_name else None
        api_state["config"] = get_company_config(api_state["company"], api_state["subfolder"])

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ----------------------------
# API: Search SSN
# ----------------------------
@app.post("/search_by_ssn")
def search_by_ssn(req: SSNRequest):

    if not api_state["config"]:
        return {"success": False, "error": "Please select company first."}

    ssn = req.ssn.strip().rstrip("~")

    BASE_PATH = api_state["config"]["base_path"]
    ACTIVE_FOLDERS = api_state["config"]["active_folders"]
    IS_AHH_AMO = api_state["config"]["is_ahh_amo"]
    IS_TELADOC = api_state["config"]["is_teladoc"]
    IS_SAVRX = api_state["config"]["is_savrx"]

    if IS_AHH_AMO:
        present, absent = find_ssn_all_dates_ahh_amo(BASE_PATH, ssn)
    elif IS_TELADOC:
        present, absent = find_ssn_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, ssn)
    elif IS_SAVRX:
        present, absent = find_ssn_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, ssn)
    else:
        present, absent = find_ssn_all_dates(BASE_PATH, ACTIVE_FOLDERS, ssn)

    if not present:
        return {"success": False, "error": "SSN not found."}

    summary = generate_ssn_timeline_summary(present, absent)

    return {
        "success": True,
        "ssn": ssn,
        "present_records": present,
        "absent_records": absent,
        "from": present[0]["date"],
        "to": present[-1]["date"],
        "summary": summary
    }


# ----------------------------
# API: Search Member ID
# ----------------------------
@app.post("/search_by_member_id")
def search_by_member_id(req: MemberIdRequest):

    if not api_state["config"]:
        return {"success": False, "error": "Please select company first."}

    member_id = req.member_id.strip().rstrip("~")

    BASE_PATH = api_state["config"]["base_path"]
    ACTIVE_FOLDERS = api_state["config"]["active_folders"]
    IS_AHH_AMO = api_state["config"]["is_ahh_amo"]
    IS_TELADOC = api_state["config"]["is_teladoc"]
    IS_SAVRX = api_state["config"]["is_savrx"]

    if IS_AHH_AMO:
        present, absent = find_member_id_all_dates_ahh_amo(BASE_PATH, member_id)
    elif IS_TELADOC:
        present, absent = find_member_id_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, member_id)
    elif IS_SAVRX:
        present, absent = find_member_id_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, member_id)
    else:
        present, absent = find_member_id_all_dates(BASE_PATH, ACTIVE_FOLDERS, member_id)

    if not present:
        return {"success": False, "error": "Member ID not found."}

    summary = generate_member_id_timeline_summary(present, absent)

    return {
        "success": True,
        "member_id": member_id,
        "present_records": present,
        "absent_records": absent,
        "from": present[0]["date"],
        "to": present[-1]["date"],
        "summary": summary
    }


# ----------------------------
# API: Search Member Name
# ----------------------------
@app.post("/search_by_member_name")
def search_by_member_name(req: MemberNameRequest):

    if not api_state["config"]:
        return {"success": False, "error": "Please select company first."}

    member_name = req.member_name.strip()

    BASE_PATH = api_state["config"]["base_path"]
    ACTIVE_FOLDERS = api_state["config"]["active_folders"]
    IS_AHH_AMO = api_state["config"]["is_ahh_amo"]
    IS_TELADOC = api_state["config"]["is_teladoc"]
    IS_SAVRX = api_state["config"]["is_savrx"]

    if IS_AHH_AMO:
        present, absent = find_member_name_all_dates_ahh_amo(BASE_PATH, member_name)
    elif IS_TELADOC:
        present, absent = find_member_name_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, member_name)
    elif IS_SAVRX:
        present, absent = find_member_name_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, member_name)
    else:
        present, absent = find_member_name_all_dates(BASE_PATH, ACTIVE_FOLDERS, member_name)

    if not present:
        return {"success": False, "error": "Member Name not found."}

    return {
        "success": True,
        "member_name": member_name,
        "present_records": present,
        "absent_records": absent,
        "from": present[0]["date"],
        "to": present[-1]["date"]
    }


# ----------------------------
# API: Date Range Search
# ----------------------------
@app.post("/search_ssns_by_date_range")
def search_ssns_by_date_range(req: DateRangeRequest):

    if not api_state["config"]:
        return {"success": False, "error": "Please select company first."}

    BASE_PATH = api_state["config"]["base_path"]
    ACTIVE_FOLDERS = api_state["config"]["active_folders"]
    IS_AHH_AMO = api_state["config"]["is_ahh_amo"]
    IS_TELADOC = api_state["config"]["is_teladoc"]
    IS_SAVRX = api_state["config"]["is_savrx"]

    try:
        if IS_AHH_AMO:
            ssns = find_all_ssns_in_date_range_ahh_amo(BASE_PATH, req.start_date, req.end_date)
        elif IS_TELADOC:
            ssns = find_all_ssns_in_date_range_teladoc(BASE_PATH, ACTIVE_FOLDERS, req.start_date, req.end_date)
        elif IS_SAVRX:
            ssns = find_all_ssns_in_date_range_savrx(BASE_PATH, ACTIVE_FOLDERS, req.start_date, req.end_date)
        else:
            ssns = find_all_ssns_in_date_range(BASE_PATH, ACTIVE_FOLDERS, req.start_date, req.end_date)

        return {
            "success": True,
            "total_ssns": len(set(ssns)),
            "ssns": sorted(set(ssns))
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

import webview
from logic import *


class API:

    def __init__(self):
        self.company = None
        self.subfolder = None   # ✅ NEW
        self.config = None


    # ================================
    # SELECT COMPANY
    # ================================
    def select_company(self, company_name):

        try:
            self.company = company_name
            self.subfolder = None  # reset subfolder when company changes

            self.config = get_company_config(company_name)

            return {
                "success": True,
                "subfolders": self.config["active_folders"]  # send folders to UI
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


    # ================================
    # SELECT SUBFOLDER (NEW LOGIC)
    # ================================
    def select_subfolder(self, subfolder_name):

        if not self.company:
            return {"success": False, "error": "Select company first."}

        try:
            self.subfolder = subfolder_name if subfolder_name else None

            # 🔥 Rebuild config with optional subfolder
            self.config = get_company_config(self.company, self.subfolder)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}


    # ================================
    # SSN SEARCH
    # ================================
    def search_by_ssn(self, ssn):

        if not self.config:
            return {"success": False, "error": "Please select company first."}

        ssn = ssn.strip().rstrip("~")

        BASE_PATH = self.config["base_path"]
        ACTIVE_FOLDERS = self.config["active_folders"]
        IS_AHH_AMO = self.config["is_ahh_amo"]
        IS_TELADOC = self.config["is_teladoc"]
        IS_SAVRX = self.config["is_savrx"]

        if IS_AHH_AMO:
            present_dates, all_dates = find_ssn_all_dates_ahh_amo(BASE_PATH, ssn)
        elif IS_TELADOC:
            present_dates, all_dates = find_ssn_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, ssn)
        elif IS_SAVRX:
            present_dates, all_dates = find_ssn_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, ssn)
        else:
            present_dates, all_dates = find_ssn_all_dates(BASE_PATH, ACTIVE_FOLDERS, ssn)

        present_dates = sorted(present_dates, key=lambda d: safe_parse_date(d))
        all_dates = sorted(all_dates, key=lambda d: safe_parse_date(d))

        if not present_dates:
            return {"success": False, "error": "SSN not found."}

        absent_dates = sorted(set(all_dates) - set(present_dates))

        return {
            "success": True,
            "ssn": ssn,
            "present_dates": present_dates,
            "absent_dates": absent_dates,
            "from": present_dates[0],
            "to": present_dates[-1]
        }


    # ================================
    # MEMBER ID SEARCH
    # ================================
    def search_by_member_id(self, member_id):

        if not self.config:
            return {"success": False, "error": "Please select company first."}

        member_id = member_id.strip().rstrip("~")

        BASE_PATH = self.config["base_path"]
        ACTIVE_FOLDERS = self.config["active_folders"]
        IS_AHH_AMO = self.config["is_ahh_amo"]
        IS_TELADOC = self.config["is_teladoc"]
        IS_SAVRX = self.config["is_savrx"]

        if IS_AHH_AMO:
            dates, _ = find_member_id_all_dates_ahh_amo(BASE_PATH, member_id)
        elif IS_TELADOC:
            dates, _ = find_member_id_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, member_id)
        elif IS_SAVRX:
            dates, _ = find_member_id_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, member_id)
        else:
            dates = find_member_id_all_dates(BASE_PATH, ACTIVE_FOLDERS, member_id)

        dates = sorted(dates, key=lambda d: safe_parse_date(d))

        if not dates:
            return {"success": False, "error": "Member ID not found."}

        return {
            "success": True,
            "member_id": member_id,
            "dates": dates,
            "from": dates[0],
            "to": dates[-1]
        }


    # ================================
    # MEMBER NAME SEARCH
    # ================================
    def search_by_member_name(self, member_name):

        if not self.config:
            return {"success": False, "error": "Please select company first."}

        member_name = member_name.strip()

        BASE_PATH = self.config["base_path"]
        ACTIVE_FOLDERS = self.config["active_folders"]
        IS_AHH_AMO = self.config["is_ahh_amo"]
        IS_TELADOC = self.config["is_teladoc"]
        IS_SAVRX = self.config["is_savrx"]

        if IS_AHH_AMO:
            dates, _ = find_member_name_all_dates_ahh_amo(BASE_PATH, member_name)
        elif IS_TELADOC:
            dates, _ = find_member_name_all_dates_teladoc(BASE_PATH, ACTIVE_FOLDERS, member_name)
        elif IS_SAVRX:
            dates, _ = find_member_name_all_dates_savrx(BASE_PATH, ACTIVE_FOLDERS, member_name)
        else:
            dates = find_member_name_all_dates(BASE_PATH, ACTIVE_FOLDERS, member_name)

        dates = sorted(dates, key=lambda d: safe_parse_date(d))

        if not dates:
            return {"success": False, "error": "Member Name not found."}

        return {
            "success": True,
            "member_name": member_name,
            "dates": dates,
            "from": dates[0],
            "to": dates[-1]
        }


    # ================================
    # DATE RANGE SSN SEARCH
    # ================================
    def search_ssns_by_date_range(self, start_date, end_date):

        if not self.config:
            return {"success": False, "error": "Please select company first."}

        BASE_PATH = self.config["base_path"]
        ACTIVE_FOLDERS = self.config["active_folders"]
        IS_AHH_AMO = self.config["is_ahh_amo"]
        IS_TELADOC = self.config["is_teladoc"]
        IS_SAVRX = self.config["is_savrx"]

        try:
            if IS_AHH_AMO:
                ssns = find_all_ssns_in_date_range_ahh_amo(BASE_PATH, start_date, end_date)
            elif IS_TELADOC:
                ssns = find_all_ssns_in_date_range_teladoc(BASE_PATH, ACTIVE_FOLDERS, start_date, end_date)
            elif IS_SAVRX:
                ssns = find_all_ssns_in_date_range_savrx(BASE_PATH, ACTIVE_FOLDERS, start_date, end_date)
            else:
                ssns = find_all_ssns_in_date_range(BASE_PATH, ACTIVE_FOLDERS, start_date, end_date)

            return {
                "success": True,
                "total_ssns": len(set(ssns)),
                "ssns": sorted(set(ssns))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    api = API()
    webview.create_window(
        "834 Eligibility Search System",
        "index.html",
        js_api=api,
        width=1400,
        height=900
    )
    webview.start()

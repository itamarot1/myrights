# session_manager.py

from gpt_response import get_basic_rights_response, get_detailed_rights_report
import re

class UserSession:
    def __init__(self):
        self.profile = {
            "age": None,
            "employment_status": None,
            "disability": None,
            "military_service": None,
            "marital_status": None
        }

    def is_profile_complete(self):
        return all(v is not None for v in self.profile.values())

    def update_profile(self, key, value):
        self.profile[key] = value

    def ask_for_clarifications(self):
        return get_basic_rights_response(self.profile)

    def generate_final_report(self, clarifications: list):
        result = get_detailed_rights_report(self.profile, clarifications)
        return result or ""  # תמיד נחזיר טקסט ולא None


# פונקציה לזיהוי שווי ההטבות שלא מומשו
def extract_unclaimed_value(gpt_text: str) -> int:
    total = 0
    rows = [line for line in gpt_text.split("\n") if "|" in line and "₪" in line]

    for row in rows:
        match = re.search(r"(\d{1,3}(?:,\d{3})*)(?:–|-)?(\d{1,3}(?:,\d{3})*)?\s*₪", row)
        if match and "לא" in row:  # רק אם לא ממומש
            low = int(match.group(1).replace(",", ""))
            high = match.group(2)
            value = int(high.replace(",", "")) if high else low
            total += value

    return total

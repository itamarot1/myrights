import json
import uuid

def create_proper_right(id_str, name, description, category, eligibility, amount, priority="medium"):
    """Create a right in the proper format matching existing structure"""
    return {
        "id": id_str,
        "name": name,
        "description": description,
        "category": category,
        "subcategory": "",
        "eligibility_criteria": {
            "age_min": eligibility.get("age_min"),
            "age_max": eligibility.get("age_max"),
            "gender": ["כל"],
            "marital_status": ["כל"],
            "employment_status": eligibility.get("employment_status", ["כל"]),
            "has_children": None,
            "children_under_18": None,
            "recognized_disability": None,
            "health_issue": None,
            "is_new_immigrant": None,
            "sector": ["כללי"],
            "income_max": eligibility.get("income_max"),
            "housing_status": ["כל"],
            "education": eligibility.get("education"),
            "city": None,
            "num_children": None,
            "children_ages": None,
            "child_special_needs": None,
            "disability_percentage": None,
            "need_daily_assistance": None,
            "filed_disability_claim": None,
            "receiving_benefit": False,
            "service_length_years": eligibility.get("service_length_years"),
            "recognized_combat_or_disabled": None,
            "injured_in_service": None,
            "avg_monthly_income": None,
            "income_drop": None,
            "paid_income_tax": None,
            "business_type": None,
            "business_decline": None,
            "receives_old_age_pension": None,
            "has_income_supplement": None,
            "military_service": eligibility.get("military_service", ["כל"])
        },
        "exclusion_criteria": {
            "income_min": None,
            "already_receiving": []
        },
        "priority": priority,
        "amount_estimation": amount,
        "application_method": "פנייה למוסד הרלוונטי",
        "required_documents": [],
        "processing_time": None,
        "contact_info": "",
        "website_url": "",
        "keywords": [],
        "related_rights": [],
        "last_updated": "2024-12-16"
    }

# Create worker rights in proper format
worker_rights = [
    create_proper_right(
        "worker_sick_pay_001",
        "דמי מחלה",
        "תשלום דמי מחלה לעובדים - 18 ימים בשנה, החל מהיום השני 50% ומהיום הרביעי 100%",
        "עבודה ותעסוקה",
        {"age_min": 18, "age_max": 67, "employment_status": ["שכיר"]},
        "עד 18 ימי שכר בשנה",
        "high"
    ),
    create_proper_right(
        "worker_vacation_002",
        "חופשה שנתית",
        "זכות לחופשה שנתית בתשלום לפי ותק - 7-28 ימים בשנה",
        "עבודה ותעסוקה",
        {"age_min": 18, "age_max": 67, "employment_status": ["שכיר"]},
        "7-28 ימי שכר בשנה",
        "high"
    ),
    create_proper_right(
        "worker_severance_003",
        "פיצויי פיטורים",
        "פיצויים בעת סיום עבודה - חודש שכר לכל שנת עבודה",
        "עבודה ותעסוקה",
        {"age_min": 18, "age_max": 67, "employment_status": ["שכיר"]},
        "חודש שכר לכל שנת עבודה",
        "high"
    )
]

# Create soldier rights in proper format  
soldier_rights = [
    create_proper_right(
        "soldier_scholarship_001",
        "מלגת ממדים ללימודים",
        "מימון מלא של שכר לימוד לתואר ראשון ללוחמים משוחררים - עד 11,653 ש״ח לשנה",
        "לימודים והשכלה",
        {"age_min": 18, "age_max": 30, "military_service": ["שירות צבאי (צה\"ל)"], "education": ["בגרות", "תואר ראשון"]},
        "11,653 ש״ח לשנה למשך 3-4 שנים",
        "high"
    ),
    create_proper_right(
        "soldier_grant_002", 
        "מענק שחרור",
        "מענק חד פעמי לחיילים משוחררים לפי משך ותכניות השירות",
        "זכויות ייחודיות לאוכלוסיות ספציפיות",
        {"age_min": 18, "age_max": 30, "military_service": ["שירות צבאי (צה\"ל)"], "service_length_years": 2},
        "משתנה לפי תקופת השירות",
        "medium"
    )
]

# Load existing rights
with open('rights_data_backup.json', 'r', encoding='utf-8') as f:
    existing_rights = json.load(f)

# Add new rights
all_rights = existing_rights + worker_rights + soldier_rights

print(f"הוספתי {len(worker_rights)} זכויות עובדים ו-{len(soldier_rights)} זכויות חיילים")
print(f"סה״כ זכויות: {len(all_rights)}")

# Save updated file
with open('rights_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_rights, f, ensure_ascii=False, indent=2)

print("הקובץ עודכן בהצלחה!")
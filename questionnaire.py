def has_children_under_18(profile):
    """Check if user has children under 18"""
    children_ages = profile.get('children_ages', '')
    if not children_ages:
        return True  # If ages not specified yet, ask questions
    
    # Parse ages from string like "5, 8, 19"
    try:
        ages = [int(age.strip()) for age in children_ages.split(',')]
        return any(age < 18 for age in ages)
    except:
        return True  # If can't parse, ask questions

def served_long_enough_for_pension(profile):
    """Check if user served 15+ years for military pension eligibility"""
    service_info = profile.get('service_length_role', '')
    if not service_info:
        return True  # If not specified yet, continue asking
    
    # Look for numbers in service length
    import re
    numbers = re.findall(r'\d+', service_info)
    if numbers:
        years = int(numbers[0])
        return years >= 15
    return False  # If can't determine, assume not eligible

BASIC_QUESTIONS = [
    {
        "key": "age",
        "question": "מהו גילך (במספר)?",
        "type": "number",
        "validation": lambda x: x.isdigit() and 0 <= int(x) <= 120
    },
    {
        "key": "gender", 
        "question": "מהו מינך?",
        "type": "choice",
        "options": ["זכר", "נקבה"]
    },
    {
        "key": "marital_status",
        "question": "מהו מצבך האישי?", 
        "type": "choice",
        "options": ["רווק", "נשוי", "גרוש", "אלמן"]
    },
    {
        "key": "city",
        "question": "באיזה יישוב/עיר אתה גר?",
        "type": "text"
    },
    {
        "key": "housing_status",
        "question": "האם אתה גר בשכירות, בבעלות, בדיור ציבורי או אחר?",
        "type": "choice", 
        "options": ["שכירות", "בבעלות", "דיור ציבורי", "אחר"]
    },
    {
        "key": "employment_status",
        "question": "מהו הסטטוס התעסוקתי שלך?",
        "type": "choice",
        "options": ["שכיר", "עצמאי", "מובטל", "סטודנט", "פנסיונר", "אחר"]
    },
    {
        "key": "recognized_disability",
        "question": "האם יש לך נכות מוכרת בביטוח לאומי?",
        "type": "choice",
        "options": ["כן", "לא"]
    },
    {
        "key": "health_issue", 
        "question": "האם יש לך בעיה רפואית או נפשית שמגבילה את תפקודך?",
        "type": "choice",
        "options": ["כן", "לא"]
    },
    {
        "key": "military_or_national_service",
        "question": "האם שירתת בצה""ל או בשירות לאומי/אזרחי?",
        "type": "choice", 
        "options": ["שירות צבאי (צה\"ל)", "שירות לאומי/אזרחי", "לא שירתתי"]
    },
    {
        "key": "education",
        "question": "האם יש לך תעודת בגרות, תעודת הנדסאי או תואר אקדמי?",
        "type": "choice",
        "options": ["אין", "בגרות", "הנדסאי", "תואר ראשון", "תואר שני ומעלה"]
    },
    {
        "key": "has_children",
        "question": "האם יש לך ילדים מתחת לגיל 18 או בעלי צרכים מיוחדים?",
        "type": "choice",
        "options": ["כן", "לא"]
    },
    {
        "key": "is_new_immigrant", 
        "question": "האם אתה עולה חדש?",
        "type": "choice",
        "options": ["כן", "לא"] 
    },
    {
        "key": "sector",
        "question": "האם אתה משתייך למגזר החרדי, הערבי, הבדואי או אחר?",
        "type": "choice",
        "options": ["כללי", "חרדי", "ערבי", "בדואי", "אחר"]
    },
    {
        "key": "avg_monthly_income",
        "question": "מה ההכנסה החודשית הממוצעת שלך ובן/בת זוגך יחד (בשקלים)?",
        "type": "number",
        "validation": lambda x: x.isdigit() and int(x) >= 0
    },
    {
        "key": "paid_income_tax_6_years",
        "question": "האם שילמת מס הכנסה ב-6 השנים האחרונות?",
        "type": "choice",
        "options": ["כן", "לא", "לא זכור"]
    },
    {
        "key": "had_work_accident",
        "question": "האם חווית תאונת עבודה אי פעם?",
        "type": "choice",
        "options": ["כן", "לא"]
    },
    {
        "key": "had_car_accident",
        "question": "האם היית מעורב בתאונת דרכים?",
        "type": "choice",
        "options": ["כן", "לא"]
    },
    {
        "key": "miluim_days_yearly",
        "question": "כמה ימי מילואים אתה משרת בשנה?",
        "type": "choice",
        "options": ["לא משרת", "עד 10 ימים", "10-20 ימים", "מעל 20 ימים", "מילואימניק פעיל"]
    }
]

CONDITIONAL_QUESTIONS = [
    {
        "condition": lambda p: str(p.get("has_children", "")).strip().lower() in ["כן", "yes", "true"],
        "questions": [
            {
                "key": "num_children",
                "question": "כמה ילדים?",
                "type": "number"
            },
            {
                "key": "children_ages",
                "question": "מה גילי הילדים? (לדוגמה: 5, 8, 12)",
                "type": "text"
            }
        ]
    },
    {
        "condition": lambda p: (str(p.get("has_children", "")).strip().lower() in ["כן", "yes", "true"] and 
                                has_children_under_18(p)),
        "questions": [
            {
                "key": "children_school_type",
                "question": "באיזה סוג מוסד לימוד הילדים לומדים?",
                "type": "choice",
                "options": ["חינוך רגיל", "חינוך מיוחד", "חינוך פרטי", "מעורב"]
            },
            {
                "key": "paying_afterschool",
                "question": "האם אתה משלם על צהרונים או חוגים לילדים?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "children_transportation",
                "question": "האם ילדיך זכאים להסעות מיוחדות?",
                "type": "choice", 
                "options": ["כן", "לא", "לא בדקתי"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("has_children", "")).strip().lower() in ["כן", "yes", "true"],
        "questions": [
            {
                "key": "child_special_needs",
                "question": "האם יש ילד במשפחה עם צרכים מיוחדים או מוגבלות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("recognized_disability", "")).strip().lower() == "כן",
        "questions": [
            {
                "key": "disability_percentage",
                "question": "מה אחוז הנכות המוכרת שלך?",
                "type": "number",
                "validation": lambda x: x.isdigit() and 0 <= int(x) <= 100
            },
            {
                "key": "need_daily_assistance",
                "question": "האם אתה נזקק לעזרה בתפקוד יומיומי?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "filed_disability_claim",
                "question": "האם הגשת בעבר תביעה לקצבת נכות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("recognized_disability", "")).strip().lower() == "כן" or str(p.get("health_issue", "")).strip().lower() == "כן",
        "questions": [
            {
                "key": "receiving_benefit",
                "question": "האם אתה מקבל קצבה כלשהי מביטוח לאומי או גורם אחר?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("military_or_national_service", "")).strip() == "שירות צבאי (צה\"ל)",
        "questions": [
            {
                "key": "service_length_years",
                "question": "כמה שנים שירתת בסך הכל?",
                "type": "number"
            },
            {
                "key": "service_role",
                "question": "באיזה תפקיד שירתת?",
                "type": "choice",
                "options": ["קרבי", "תומך", "מקצועי", "אחר"]
            },
            {
                "key": "injured_in_service",
                "question": "האם נפצעת במהלך השירות או מוכר כנכה צה\"ל?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("employment_status", "")) in ["שכיר", "עצמאי"],
        "questions": [
            {
                "key": "avg_monthly_income",
                "question": "מהו ממוצע ההכנסה החודשית ברוטו? (במספרים)",
                "type": "number"
            },
            {
                "key": "income_drop",
                "question": "האם הייתה ירידה בהכנסות לאחרונה?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "paid_income_tax",
                "question": "האם שילמת מס הכנסה בשנתיים האחרונות?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "paid_courses",
                "question": "האם שילמת על קורסים מקצועיים בשנתיים האחרונות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("employment_status", "")) == "עצמאי",
        "questions": [
            {
                "key": "business_type",
                "question": "איזה סוג עסק?",
                "type": "choice",
                "options": ["עוסק פטור", "עוסק מורשה", "חברה בע\"מ", "אחר"]
            },
            {
                "key": "business_decline",
                "question": "האם העסק חווה ירידה או נסגר?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "receiving_business_grants",
                "question": "האם אתה מקבל מענקים לעסקים?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("employment_status", "")) == "פנסיונר",
        "questions": [
            {
                "key": "receives_old_age_pension",
                "question": "האם אתה מקבל קצבת זקנה?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "has_income_supplement",
                "question": "האם יש לך השלמת הכנסה?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    }
]

SECONDARY_QUESTIONS = [
    {
        "condition": lambda p: str(p.get("recognized_disability", "")).strip().lower() == "כן",
        "questions": [
            {
                "key": "disability_type",
                "question": "מה סוג הנכות העיקרי?",
                "type": "choice",
                "options": ["פיזית", "נפשית", "שכלית", "חושית", "מעורב"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("paid_income_tax", "")) == "כן",
        "questions": [
            {
                "key": "medical_expense_receipts",
                "question": "האם יש לך קבלות על הוצאות רפואיות או חינוך מיוחד?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("employment_status", "")) in ["שכיר", "עצמאי"],
        "questions": [
            {
                "key": "work_experience_years",
                "question": "כמה שנות ניסיון יש לך בעבודה?",
                "type": "number",
                "validation": lambda x: x.isdigit() and 0 <= int(x) <= 60
            },
            {
                "key": "work_injury",
                "question": "האם נפגעת אי פעם בתאונת עבודה או מחלה מקצועית?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("has_children", "")) == "כן",
        "questions": [
            {
                "key": "single_parent",
                "question": "האם אתה הורה יחיד/ה?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("paid_income_tax_6_years", "")) == "כן",
        "questions": [
            {
                "key": "has_medical_receipts",
                "question": "האם יש לך קבלות על הוצאות רפואיות?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "has_pension_fund",
                "question": "האם יש לך קרן השתלמות או קופת גמל?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "paid_professional_courses",
                "question": "האם שילמת על קורסים מקצועיים?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "donated_to_organizations",
                "question": "האם תרמת לעמותות מוכרות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("had_work_accident", "")) == "כן" or str(p.get("had_car_accident", "")) == "כן",
        "questions": [
            {
                "key": "accident_compensation_received",
                "question": "האם קיבלת פיצוי על התאונה?",
                "type": "choice",
                "options": ["כן", "לא", "בתהליך"]
            },
            {
                "key": "accident_medical_treatment",
                "question": "האם אתה מקבל טיפול רפואי בעקבות התאונה?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    {
        "condition": lambda p: str(p.get("miluim_days_yearly", "")) in ["מעל 20 ימים", "מילואימניק פעיל"],
        "questions": [
            {
                "key": "miluim_role",
                "question": "מה תפקידך במילואים?",
                "type": "choice",
                "options": ["קרבי", "תומך", "מקצועי", "פיקוד"]
            },
            {
                "key": "miluim_compensation_issues",
                "question": "האם חווית בעיות עם פיצויי מילואים?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    }
]
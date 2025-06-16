#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptive questionnaire system - replaces the old static questionnaire
מערכת שאלון אדפטיבית - מחליפה את השאלון הסטטי הישן
"""

def has_children_under_18(profile):
    """Check if user has children under 18"""
    children_ages = profile.get('children_ages', '')
    if children_ages:
        try:
            ages = [int(age.strip()) for age in children_ages.split(',')]
            return any(age < 18 for age in ages)
        except:
            pass
    
    # Fallback to number of children (assume under 18 if no ages specified)
    num_children = profile.get('num_children', '0')
    try:
        return int(num_children) > 0
    except:
        return False

# Minimal core questions that capture maximum rights potential
MINIMAL_CORE_QUESTIONS = [
    {
        "key": "age",
        "question": "מהו גילך?",
        "type": "number",
        "validation": lambda x: x.isdigit() and 0 <= int(x) <= 120,
        "priority": 1
    },
    {
        "key": "num_children",
        "question": "כמה ילדים יש לך?",
        "type": "number",
        "validation": lambda x: x.isdigit() and int(x) >= 0,
        "priority": 2
    },
    {
        "key": "employment_status",
        "question": "מה מצבך התעסוקתי?",
        "type": "choice",
        "options": ["שכיר", "עצמאי", "מובטל", "סטודנט", "פנסיונר", "לא עובד"],
        "priority": 3
    },
    {
        "key": "recognized_disability",
        "question": "האם יש לך נכות מוכרת בביטוח לאומי?",
        "type": "choice",
        "options": ["כן", "לא"],
        "priority": 4
    },
    {
        "key": "military_or_national_service",
        "question": "האם שירתת בצה\"ל או בשירות לאומי?",
        "type": "choice",
        "options": ["שירות צבאי (צה\"ל)", "שירות לאומי/אזרחי", "לא שירתתי"],
        "priority": 5
    }
]

# Smart follow-up questions based on answers
ADAPTIVE_FOLLOW_UPS = [
    # Children details
    {
        "condition": lambda p: p.get("num_children") and int(p.get("num_children", "0")) > 0,
        "questions": [
            {
                "key": "marital_status",
                "question": "מהו מצבך המשפחתי?",
                "type": "choice",
                "options": ["נשוי", "גרוש", "רווק", "אלמן"]
            }
        ]
    },
    
    # Employment details - only for workers
    {
        "condition": lambda p: p.get("employment_status") in ["שכיר", "עצמאי"],
        "questions": [
            {
                "key": "avg_monthly_income",
                "question": "מה ההכנסה החודשית שלך (בקירוב)?",
                "type": "choice",
                "options": ["עד 4,000", "4,000-8,000", "8,000-15,000", "מעל 15,000"]
            },
            {
                "key": "paid_income_tax_6_years",
                "question": "האם שילמת מס הכנסה ב-6 השנים האחרונות?",
                "type": "choice",
                "options": ["כן", "לא", "לא זכור"]
            }
        ]
    },
    
    # Disability details
    {
        "condition": lambda p: p.get("recognized_disability") == "כן",
        "questions": [
            {
                "key": "disability_percentage",
                "question": "מה אחוז הנכות המוכרת שלך?",
                "type": "choice",
                "options": ["עד 25%", "25-50%", "50-75%", "מעל 75%"]
            },
            {
                "key": "need_daily_assistance",
                "question": "האם אתה זקוק לעזרה יומיומית?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    
    # Military service details - only for veterans
    {
        "condition": lambda p: p.get("military_or_national_service") == "שירות צבאי (צה\"ל)",
        "questions": [
            {
                "key": "service_length_years",
                "question": "כמה שנים שירתת בסך הכל?",
                "type": "choice",
                "options": ["עד 3 שנים", "3-10 שנים", "10-20 שנים", "מעל 20 שנים"]
            },
            {
                "key": "injured_in_service",
                "question": "האם נפצעת במהלך השירות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    
    # Low income specific questions
    {
        "condition": lambda p: p.get("avg_monthly_income") in ["עד 4,000", "4,000-8,000"],
        "questions": [
            {
                "key": "housing_status",
                "question": "איך אתה גר?",
                "type": "choice",
                "options": ["שכירות", "בבעלות", "דיור ציבורי", "אחר"]
            },
            {
                "key": "receiving_benefits",
                "question": "האם אתה מקבל קצבה כלשהי?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    
    # High disability specific questions
    {
        "condition": lambda p: p.get("disability_percentage") in ["50-75%", "מעל 75%"],
        "questions": [
            {
                "key": "disability_type",
                "question": "מה סוג הנכות העיקרי?",
                "type": "choice",
                "options": ["פיזית", "נפשית", "שכלית", "חושית", "מעורב"]
            }
        ]
    },
    
    # Accident and compensation questions - for tax payers
    {
        "condition": lambda p: p.get("paid_income_tax_6_years") == "כן",
        "questions": [
            {
                "key": "had_work_accident",
                "question": "האם חווית תאונת עבודה אי פעם?",
                "type": "choice",
                "options": ["כן", "לא"]
            },
            {
                "key": "has_medical_receipts",
                "question": "האם יש לך קבלות על הוצאות רפואיות?",
                "type": "choice",
                "options": ["כן", "לא"]
            }
        ]
    },
    
    # Large family benefits
    {
        "condition": lambda p: p.get("num_children") and int(p.get("num_children", "0")) >= 3,
        "questions": [
            {
                "key": "children_ages",
                "question": "מה גילי הילדים? (לדוגמה: 5, 8, 12)",
                "type": "text"
            }
        ]
    },
    
    # Long military service benefits  
    {
        "condition": lambda p: p.get("service_length_years") in ["10-20 שנים", "מעל 20 שנים"],
        "questions": [
            {
                "key": "miluim_days_yearly",
                "question": "כמה ימי מילואים אתה משרת בשנה?",
                "type": "choice",
                "options": ["לא משרת", "עד 20 ימים", "מעל 20 ימים", "מילואימניק פעיל"]
            }
        ]
    }
]

def get_relevant_questions(current_profile):
    """Get next most relevant questions based on current profile"""
    
    # First, check if we need any core questions
    missing_core = []
    for q in MINIMAL_CORE_QUESTIONS:
        if q["key"] not in current_profile:
            # Apply age-based filtering
            age = current_profile.get('age')
            if age:
                age_int = int(age) if age.isdigit() else 25
                
                # Don't ask military to children or very elderly
                if q["key"] == "military_or_national_service" and (age_int < 17 or age_int > 70):
                    continue
                    
                # Don't ask employment to children or very elderly initially
                if q["key"] == "employment_status" and (age_int < 16 or age_int > 75):
                    continue
            
            missing_core.append(q)
    
    if missing_core:
        # Return highest priority core question
        return [min(missing_core, key=lambda x: x["priority"])]
    
    # Then check for relevant follow-ups
    relevant_followups = []
    for followup_block in ADAPTIVE_FOLLOW_UPS:
        try:
            if followup_block["condition"](current_profile):
                for question in followup_block["questions"]:
                    if question["key"] not in current_profile:
                        relevant_followups.append(question)
        except:
            continue  # Skip if condition evaluation fails
    
    # Return up to 2 most relevant follow-up questions
    return relevant_followups[:2]

def estimate_completion_percentage(current_profile):
    """Estimate how complete the profile is"""
    
    # Core questions weight more
    core_completion = sum(1 for q in MINIMAL_CORE_QUESTIONS if q["key"] in current_profile)
    core_total = len(MINIMAL_CORE_QUESTIONS)
    
    # Count relevant follow-ups that could be asked
    total_relevant_followups = 0
    answered_followups = 0
    
    for followup_block in ADAPTIVE_FOLLOW_UPS:
        try:
            if followup_block["condition"](current_profile):
                for question in followup_block["questions"]:
                    total_relevant_followups += 1
                    if question["key"] in current_profile:
                        answered_followups += 1
        except:
            continue
    
    if total_relevant_followups == 0:
        return (core_completion / core_total) * 100
    
    # Weighted completion: 70% core, 30% follow-ups
    core_percentage = (core_completion / core_total) * 0.7
    followup_percentage = (answered_followups / total_relevant_followups) * 0.3
    
    return (core_percentage + followup_percentage) * 100

def convert_to_old_format(adaptive_profile):
    """Convert adaptive profile to old questionnaire format for compatibility"""
    converted = adaptive_profile.copy()
    
    # Convert num_children to has_children for backwards compatibility
    if "num_children" in converted and "has_children" not in converted:
        num_children = int(converted.get("num_children", "0"))
        converted["has_children"] = "כן" if num_children > 0 else "לא"
    
    # Add default values for missing old fields
    defaults = {
        "gender": "לא צוין",
        "city": "לא צוין", 
        "sector": "כללי",
        "education": "לא צוין",
        "is_new_immigrant": "לא",
        "health_issue": "לא" if converted.get("recognized_disability") == "לא" else "כן"
    }
    
    for key, default_value in defaults.items():
        if key not in converted:
            converted[key] = default_value
    
    return converted

# For backwards compatibility - expose the adaptive system as the main questionnaire
BASIC_QUESTIONS = MINIMAL_CORE_QUESTIONS
CONDITIONAL_QUESTIONS = ADAPTIVE_FOLLOW_UPS
SECONDARY_QUESTIONS = []  # Not needed in adaptive system

if __name__ == "__main__":
    # Test the adaptive questionnaire
    print("🎯 בדיקת השאלון האדפטיבי")
    print("="*50)
    
    # Simulate different user types
    test_cases = [
        {"name": "הורה יחיד עם הכנסה נמוכה", "answers": {
            "age": "35", "has_children": "כן", "employment_status": "שכיר",
            "recognized_disability": "לא", "military_or_national_service": "שירות צבאי (צה\"ל)",
            "num_children": "2", "marital_status": "גרוש", "avg_monthly_income": "עד 4,000"
        }},
        {"name": "גמלאי עם נכות", "answers": {
            "age": "68", "has_children": "לא", "employment_status": "פנסיונר",
            "recognized_disability": "כן", "disability_percentage": "מעל 75%"
        }},
        {"name": "חייל משוחרר צעיר", "answers": {
            "age": "22", "has_children": "לא", "employment_status": "סטודנט",
            "recognized_disability": "לא", "military_or_national_service": "שירות צבאי (צה\"ל)",
            "service_length_years": "עד 3 שנים"
        }}
    ]
    
    for test_case in test_cases:
        print(f"\n📋 {test_case['name']}:")
        profile = test_case['answers']
        
        questions_that_would_be_asked = 0
        temp_profile = {}
        
        # Simulate step-by-step questionnaire
        while questions_that_would_be_asked < 15:  # Limit for demo
            next_questions = get_relevant_questions(temp_profile)
            if not next_questions:
                break
                
            next_q = next_questions[0]
            questions_that_would_be_asked += 1
            
            # Simulate answer
            if next_q["key"] in profile:
                temp_profile[next_q["key"]] = profile[next_q["key"]]
                print(f"  {questions_that_would_be_asked}. {next_q['question']} → {profile[next_q['key']]}")
            else:
                break
        
        completion = estimate_completion_percentage(temp_profile)
        print(f"  📊 שלמות: {completion:.0f}% | שאלות: {questions_that_would_be_asked}")
    
    print(f"\n✅ השאלון האדפטיבי מתאים את עצמו לכל סוג משתמש!")
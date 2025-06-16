import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from adaptive_questionnaire import get_relevant_questions, estimate_completion_percentage, convert_to_old_format
from rights_validator import RightsValidator, create_validation_report

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_rights_catalog():
    """Load the rights catalog from JSON file"""
    try:
        with open('rights_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Rights catalog file not found")
        return []

def filter_matching_rights(profile: dict, min_value_threshold=500):
    """Filter rights that match the user profile and have significant value"""
    rights_catalog = load_rights_catalog()
    matching_rights = []
    
    for right in rights_catalog:
        eligibility = right.get('eligibility_criteria', {})
        
        # Skip rights with empty or overly broad criteria
        if not has_specific_criteria(eligibility):
            continue
        
        # Check basic criteria matching
        if not check_eligibility_match(profile, eligibility, right):
            continue
            
        # Check if right has significant monetary value
        amount = right.get('amount_estimation', '')
        if not has_significant_value(amount, min_value_threshold):
            continue
            
        matching_rights.append(right)
    
    # Remove duplicates and sort by value
    unique_rights = remove_duplicate_rights(matching_rights)
    
    # Sort by estimated value (highest first)
    rights_sorted = sorted(unique_rights, key=lambda x: extract_max_amount(x.get('amount_estimation', '0')), reverse=True)
    
    return rights_sorted[:5]  # Max 5 high-quality rights

def has_specific_criteria(criteria: dict) -> bool:
    """Check if the right has specific, meaningful criteria"""
    meaningful_criteria = 0
    
    # Count specific criteria
    for key, value in criteria.items():
        if value is not None and value != [] and value != ['כל']:
            if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                meaningful_criteria += 1
    
    # Accept rights with at least 1 meaningful criterion OR rights that are completely general (for universal benefits)
    return True  # For now, let the eligibility matching do all the filtering

def remove_duplicate_rights(rights: list) -> list:
    """Remove duplicate rights based on name similarity"""
    unique_rights = []
    seen_names = set()
    
    for right in rights:
        name = right.get('name', '').strip()
        # Check for duplicate or very similar names
        is_duplicate = False
        for seen_name in seen_names:
            if name in seen_name or seen_name in name or calculate_similarity(name, seen_name) > 0.8:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_rights.append(right)
            seen_names.add(name)
    
    return unique_rights

def calculate_similarity(str1: str, str2: str) -> float:
    """Simple similarity calculation"""
    words1 = set(str1.split())
    words2 = set(str2.split())
    if not words1 or not words2:
        return 0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

def check_eligibility_match(profile: dict, criteria: dict, right: dict = None):
    """Check if profile matches eligibility criteria - strict matching"""
    
    # Age check
    age = profile.get('age')
    if age and age.isdigit():
        age = int(age)
        age_min = criteria.get('age_min')
        age_max = criteria.get('age_max')
        if age_min and age < age_min:
            return False
        if age_max and age > age_max:
            return False
    
    # Income check - strict
    income_max = criteria.get('income_max')
    user_income = profile.get('avg_monthly_income')
    if income_max and user_income:
        try:
            # Extract numbers from income string (handle "10,000 שח" format)
            import re
            income_numbers = re.findall(r'\d+', str(user_income).replace(',', ''))
            if income_numbers:
                user_income_num = int(income_numbers[0])
                if user_income_num > income_max:
                    return False
        except:
            pass
    
    # Military service - very important check with exact matching
    military_criteria = criteria.get('military_service')
    user_military = profile.get('military_or_national_service', profile.get('military_service', ''))
    if military_criteria and military_criteria != ['כל']:
        # Must have exact match in criteria list
        if user_military not in military_criteria:
            return False
    
    # Service length check - critical for military pension rights
    service_length_years = criteria.get('service_length_years')
    if service_length_years:
        user_service_years = profile.get('service_length_years', '')
        if not user_service_years or str(user_service_years).strip() == '':
            # If service length is required but not provided, reject
            return False
        
        try:
            # Extract number from service length (e.g., "חמש" -> need conversion)
            import re
            numbers = re.findall(r'\d+', str(user_service_years))
            if numbers:
                user_years = int(numbers[0])
            else:
                # Handle Hebrew numbers
                hebrew_to_num = {'אחת': 1, 'שתיים': 2, 'שלוש': 3, 'ארבע': 4, 'חמש': 5, 'שש': 6, 'שבע': 7, 'שמונה': 8, 'תשע': 9, 'עשר': 10, 'אחת עשרה': 11, 'שתים עשרה': 12, 'שלוש עשרה': 13, 'ארבע עשרה': 14, 'חמש עשרה': 15, 'עשרים': 20}
                user_years = hebrew_to_num.get(user_service_years.strip(), 0)
            
            if user_years < service_length_years:
                return False
        except:
            return False  # If can't parse, reject
    
    # Strict boolean criteria checks - must match exactly
    strict_boolean_checks = [
        ('recognized_disability', 'recognized_disability'),
        ('health_issue', 'health_issue'),
        ('has_children', 'has_children'),
        ('child_special_needs', 'child_special_needs'),
        ('is_new_immigrant', 'is_new_immigrant'),
        ('injured_in_service', 'injured_in_service')
    ]
    
    for profile_key, criteria_key in strict_boolean_checks:
        profile_val = profile.get(profile_key)
        criteria_val = criteria.get(criteria_key)
        
        if criteria_val is not None:
            profile_bool = str(profile_val).strip().lower() in ['כן', 'true', 'yes']
            if criteria_val != profile_bool:
                return False
    
    # Employment status check
    employment_criteria = criteria.get('employment_status')
    user_employment = profile.get('employment_status')
    if employment_criteria and employment_criteria != ['כל'] and user_employment:
        if user_employment not in employment_criteria:
            return False
    
    # Gender check - important for military-related rights
    gender_criteria = criteria.get('gender')
    user_gender = profile.get('gender')
    if gender_criteria and gender_criteria != ['כל'] and user_gender:
        if user_gender not in gender_criteria:
            return False
    
    # Additional strict checks for new criteria fields
    
    # Service length check for military pensions
    service_years_criteria = criteria.get('service_length_years')
    user_service_years = profile.get('service_length_years')
    if service_years_criteria and user_service_years:
        try:
            if int(user_service_years) < service_years_criteria:
                return False
        except:
            pass
    
    # Paid courses check for tax deductions
    if criteria.get('paid_courses') == True and profile.get('paid_courses') != 'כן':
        return False
    
    # Medical expense receipts check
    if criteria.get('medical_expense_receipts') == True and profile.get('medical_expense_receipts') != 'כן':
        return False
    
    # Business decline check for crisis grants
    if criteria.get('business_decline') == True and profile.get('business_decline') != 'כן':
        return False
    
    # Receiving business grants exclusion
    receiving_grants_criteria = criteria.get('receiving_business_grants')
    if receiving_grants_criteria == False and profile.get('receiving_business_grants') == 'כן':
        return False
    
    # Children school type checks
    school_type_criteria = criteria.get('children_school_type')
    user_school_type = profile.get('children_school_type')
    if school_type_criteria and user_school_type and school_type_criteria != user_school_type:
        return False
    
    # Afterschool payment check
    if criteria.get('paying_afterschool') == 'כן' and profile.get('paying_afterschool') != 'כן':
        return False
    
    # Children transportation check
    if criteria.get('children_transportation') == 'כן' and profile.get('children_transportation') != 'כן':
        return False
    
    # Disability type check
    disability_type_criteria = criteria.get('disability_type')
    user_disability_type = profile.get('disability_type')
    if disability_type_criteria and user_disability_type and disability_type_criteria != user_disability_type:
        return False
    
    # Additional strict checks for common exclusions
    # Don't give disability rights to non-disabled people
    if ('נכות' in criteria.get('keywords', []) or 'נכה' in str(criteria) or 
        'נכים' in str(right.get('name', '')) or 'נכות' in str(right.get('name', '')) or
        'נפגעי' in str(right.get('name', '')) or 'מוגבלויות' in str(right.get('name', '')) or
        'שיפוץ לבעלי מוגבלויות' in str(right.get('name', '')) or
        criteria.get('recognized_disability') == True):
        if profile.get('recognized_disability') != 'כן':
            return False
    
    # Don't give child-related rights to people without children
    if criteria.get('child_special_needs') == True and profile.get('has_children') != 'כן':
        return False
    
    # Don't give student rights to non-students
    if ('סטודנט' in str(right.get('name', '')) or 'מלגה' in str(right.get('name', ''))):
        # Only give to actual students
        if profile.get('employment_status') not in ['סטודנט', 'לא עובד']:
            return False
    
    # Don't give training courses to people over 45 unless unemployed
    if ('קורס' in str(right.get('name', '')) or 'הכשר' in str(right.get('name', ''))):
        age = profile.get('age')
        if (age and age.isdigit() and int(age) > 45 and 
            profile.get('employment_status') not in ['מובטל', 'לא עובד']):
            return False
    
    # Don't give unemployment benefits to employed people (but allow severance pay info)
    if ('מובטל' in str(right.get('name', '')) or 
        'הכנסה מבטחת' in str(right.get('name', '')) or 'מענקי עידוד' in str(right.get('name', '')) or
        'שיקום תעסוקתי' in str(right.get('name', '')) or 'יציאה לעצמאות' in str(right.get('name', ''))):
        if profile.get('employment_status') not in ['מובטל', 'לא עובד']:
            return False
    
    # Special case: Severance pay is relevant for employed people to know their rights
    # (they don't get it now, but it's good to know for the future)
    
    # Don't give work injury benefits to people who haven't been injured
    if ('תאונת עבודה' in str(right.get('name', '')) or 'מחלה מקצועית' in str(right.get('name', '')) or
        'נפגע עבודה' in str(right.get('name', ''))):
        if profile.get('injured_in_service') != 'כן' and profile.get('work_injury') != 'כן':
            return False
    
    # Only give medical expense rights to people with health issues or families
    if ('הוצאות רפואיות' in str(right.get('name', '')) and 
        profile.get('health_issue') != 'כן' and 
        profile.get('has_children') != 'כן' and
        profile.get('recognized_disability') != 'כן'):
        return False
    
    # Only give travel reimbursement to people with ongoing medical treatment
    if ('החזרי נסיעות' in str(right.get('name', '')) and 'טיפול' in str(right.get('name', ''))):
        if (profile.get('health_issue') != 'כן' and 
            profile.get('recognized_disability') != 'כן'):
            return False
        
    return True

def has_significant_value(amount_str: str, threshold: int):
    """Check if the right has significant monetary value"""
    if not amount_str or amount_str.lower() in ['משתנה', 'לא ידוע', '']:
        return True  # Include unknown amounts for safety
    
    # Special handling for worker rights (always include)
    if any(word in amount_str for word in ['ימי שכר', 'ימים', 'חודש שכר']):
        return True
        
    # Extract numbers from amount string
    import re
    numbers = re.findall(r'\d+', amount_str.replace(',', ''))
    if numbers:
        # Take the highest number found
        max_amount = max(int(num) for num in numbers)
        return max_amount >= threshold
    
    return True  # Include if can't parse

def extract_max_amount(amount_str: str) -> int:
    """Extract maximum amount from amount string for sorting"""
    if not amount_str:
        return 0
    
    # Special handling for worker rights - estimate high value
    if 'ימי שכר' in amount_str:
        import re
        numbers = re.findall(r'\d+', amount_str.replace(',', ''))
        if numbers:
            days = max(int(num) for num in numbers)
            # Estimate: 28 days = ~30,000 NIS (average monthly salary)
            return days * 1000  # Rough estimate
    
    if 'חודש שכר' in amount_str:
        import re
        numbers = re.findall(r'\d+', amount_str.replace(',', ''))
        if numbers:
            months = max(int(num) for num in numbers)
            return months * 10000  # Average monthly salary estimate
        else:
            # If no number found but mentions "חודש שכר", assume 1 month per year of service (average 5 years)
            return 50000  # Estimate for 5 months salary
    
    import re
    numbers = re.findall(r'\d+', amount_str.replace(',', ''))
    if numbers:
        return max(int(num) for num in numbers)
    return 0

def parse_amount_range(amount_str: str) -> tuple:
    """Parse amount string and return (min, max) tuple"""
    if not amount_str or amount_str.lower() in ['משתנה', 'לא ידוע']:
        return (0, 0)
    
    import re
    numbers = re.findall(r'\d+', amount_str.replace(',', ''))
    if numbers:
        numbers = [int(num) for num in numbers]
        if len(numbers) == 1:
            return (numbers[0], numbers[0])
        else:
            return (min(numbers), max(numbers))
    return (0, 0)

def get_basic_rights_response(profile: dict) -> str:
    return "נמשיך לשאול מספר שאלות כדי שנוכל לבדוק את הזכויות שמגיעות לך."

def get_detailed_rights_report(profile: dict, clarifications: list) -> str:
    # First, try to find matching rights in our catalog
    matching_rights = filter_matching_rights(profile, min_value_threshold=500)
    
    if len(matching_rights) > 0:
        # We found rights in catalog, use catalog data
        return generate_report_from_catalog(profile, matching_rights)
    else:
        # No rights found in catalog, fallback to web search + GPT as last resort
        print("No rights found in catalog, falling back to web search")
        return generate_report_with_web_search(profile, clarifications, matching_rights)

def generate_report_from_catalog(profile: dict, rights: list) -> str:
    """Generate clean and simple report based on catalog data"""
    
    # Initialize validator
    validator = RightsValidator()
    
    # Create validation report
    validation_report = create_validation_report(rights, profile, validator)
    
    # Sort by estimated value (highest first)
    rights_sorted = sorted(rights, key=lambda x: extract_max_amount(x.get('amount_estimation', '0')), reverse=True)
    
    # Build clean report
    report_parts = []
    
    # Simple header
    report_parts.append("🎯 הזכויות שמגיעות לך")
    report_parts.append("")
    
    # Clean list of rights (max 3 for simplicity)
    for i, right in enumerate(rights_sorted[:3], 1):
        amount = right.get('amount_estimation', 'לא ידוע')
        
        # Get validation confidence
        validation = validation_report["rights_validations"][i-1]["validation"]
        confidence = validation["confidence_score"]
        if confidence >= 80:
            confidence_icon = "🟢"
        elif confidence >= 60:
            confidence_icon = "🟡"
        else:
            confidence_icon = "🔴"
        
        # Generate specific reason why this right applies to this user
        reason = generate_eligibility_reason(profile, right)
        
        # Simple, clean format with specific reason
        report_parts.append(f"{i}. {right['name']}")
        if reason:
            report_parts.append(f"   ✅ למה זה מגיע לך: {reason}")
        report_parts.append(f"   💰 {format_amount_nicely(amount)}")
        report_parts.append(f"   {confidence_icon} מהימנות: {confidence:.0f}%")
        report_parts.append("")
    
    # Simple summary - use actual displayed count
    displayed_count = min(len(rights_sorted), 3)
    avg_confidence = validation_report['average_confidence']
    report_parts.append("📊 סיכום:")
    report_parts.append(f"נמצאו {displayed_count} זכויות רלוונטיות")
    report_parts.append(f"ממוצע מהימנות: {avg_confidence:.0f}%")
    report_parts.append("")
    
    # Call to action - removed contact form per user request
    report_parts.append("🎯 רוצה לממש את הזכויות?")
    report_parts.append("צור קשר איתנו ונטפל בכל התהליך עבורך:")
    report_parts.append("• בדיקת זכאות מדויקת")
    report_parts.append("• הכנת מסמכים") 
    report_parts.append("• הגשת בקשות")
    report_parts.append("• מעקב עד לקבלת הכסף")
    
    return "\n".join(report_parts)

def get_right_emoji(right_name: str) -> str:
    """Get appropriate emoji for right type"""
    name_lower = right_name.lower()
    
    if 'נכות' in name_lower or 'נכה' in name_lower:
        return '🧑‍🦽'
    elif 'ילד' in name_lower:
        return '👶'
    elif 'חינוך' in name_lower or 'לימוד' in name_lower:
        return '📚'
    elif 'דיור' in name_lower or 'שכר דירה' in name_lower:
        return '🏠'
    elif 'תחבורה' in name_lower or 'רכב' in name_lower:
        return '🚗'
    elif 'עבודה' in name_lower or 'תעסוקה' in name_lower:
        return '💼'
    elif 'רפואי' in name_lower or 'בריאות' in name_lower:
        return '🏥'
    elif 'מס' in name_lower or 'פטור' in name_lower:
        return '💳'
    elif 'מלגה' in name_lower:
        return '🎓'
    else:
        return '💬'

def generate_eligibility_reason(profile: dict, right: dict) -> str:
    """Generate specific reason why user is eligible for this right"""
    reasons = []
    
    # Age-based reasons
    age = profile.get('age')
    if age and age.isdigit():
        age_num = int(age)
        if age_num < 30:
            reasons.append(f"גיל צעיר ({age})")
        elif age_num > 60:
            reasons.append(f"גיל בוגר ({age})")
    
    # Family-based reasons
    if profile.get('has_children') == 'כן':
        if profile.get('num_children'):
            reasons.append(f"הורה ל-{profile.get('num_children')} ילדים")
        else:
            reasons.append("הורה לילדים")
        
        if profile.get('child_special_needs') == 'כן':
            reasons.append("ילד עם צרכים מיוחדים")
    
    if profile.get('marital_status') in ['גרושה', 'גרוש']:
        reasons.append("הורה יחיד")
    
    # Income-based reasons
    income = profile.get('avg_monthly_income')
    if income and income.replace(',', '').isdigit():
        income_num = int(income.replace(',', ''))
        if income_num < 12000:
            reasons.append(f"הכנסה נמוכה ({income}₪)")
    
    if profile.get('income_drop') == 'כן':
        reasons.append("ירידה בהכנסה")
    
    # Health-based reasons
    if profile.get('health_issue') == 'כן':
        reasons.append("בעיות בריאות")
    
    if profile.get('recognized_disability') == 'כן':
        reasons.append("נכות מוכרת")
    
    # Military service reasons
    military = profile.get('military_or_national_service')
    if military and 'צבאי' in military:
        reasons.append("חייל משוחרר")
    elif military and 'לאומי' in military:
        reasons.append("שירות לאומי")
    
    # Housing reasons
    if profile.get('housing_status') == 'שכירות':
        reasons.append("גר בשכירות")
    
    # Immigration reasons
    if profile.get('is_new_immigrant') == 'כן':
        reasons.append("עולה חדש")
    
    # Employment reasons
    employment = profile.get('employment_status')
    if employment == 'מובטל':
        reasons.append("מובטל")
    elif employment == 'עצמאי':
        reasons.append("עצמאי")
    
    if profile.get('business_decline') == 'כן':
        reasons.append("ירידה בעסק")
    
    # Combine reasons intelligently
    if len(reasons) > 3:
        main_reasons = reasons[:3]
        return ", ".join(main_reasons) + " ועוד"
    elif reasons:
        return ", ".join(reasons)
    else:
        return "עומד בתנאי הזכאות"

def format_amount_nicely(amount_str: str) -> str:
    """Format amount string nicely and concisely"""
    if not amount_str or amount_str.lower() in ['משתנה', 'לא ידוע']:
        return 'משתנה לפי מקרה'
    
    # Shorten very long descriptions
    if len(amount_str) > 150:
        # Extract key numbers and info
        import re
        numbers = re.findall(r'[\d,]+', amount_str)
        if numbers:
            main_amount = int(numbers[0].replace(',', ''))
            if 'הלוואה' in amount_str:
                return f"הלוואה עד {main_amount:,} ₪ בתנאים מועדפים"
            elif 'הפקדה' in amount_str and 'מס' in amount_str:
                return f"הטבת מס על הפקדות - חיסכון עד {main_amount:,} ₪"
            elif 'פטור' in amount_str and 'מס' in amount_str:
                return f"פטור ממס עד {main_amount:,} ₪ לשנה"
            else:
                return f"עד {main_amount:,} ₪"
    
    # Add currency symbol if missing
    import re
    if '₪' not in amount_str and 'ש"ח' not in amount_str and re.search(r'\d', amount_str):
        amount_str += ' ₪'
    
    return amount_str

def generate_report_with_web_search(profile: dict, clarifications: list, existing_rights: list) -> str:
    """Generate report using web search when catalog is insufficient"""
    clarifications_text = "\n".join(clarifications)
    disability = profile.get('recognized_disability') or profile.get('health_issue')
    
    # Include existing catalog rights in the prompt
    catalog_info = ""
    if existing_rights:
        catalog_info = "זכויות שכבר נמצאו בקטלוג:\n"
        for right in existing_rights:
            catalog_info += f"- {right['name']}: {right.get('amount_estimation', 'לא ידוע')}\n"
        catalog_info += "\nחפש זכויות נוספות באינטרנט לחיזוק הדוח:\n"

    prompt = f"""מתמחה בזכויות ממשלתיות בישראל. המטרה: מידע מדויק בלבד.

🚨 חובות עליונות:
- אם לא בטוח ב-100% - אל תציין
- עדיף "לא נמצאו זכויות" מהמצאה
- רק מקורות אמינים: ביטוח לאומי, מס הכנסה, משרד החינוך/בריאות/בטחון

פרופיל מפורט:
- גיל: {profile.get('age')}
- מין: {profile.get('gender')}
- מצב אישי: {profile.get('marital_status')}
- עיר: {profile.get('city')}
- תעסוקה: {profile.get('employment_status')}
- הכנסה חודשית: {profile.get('avg_monthly_income')}
- ירידה בהכנסה: {profile.get('income_drop', 'לא צוין')}
- ילדים: {profile.get('has_children')}
- מספר ילדים: {profile.get('num_children', 'לא צוין')}
- גילאי ילדים: {profile.get('children_ages', 'לא צוין')}
- ילד עם צרכים מיוחדים: {profile.get('child_special_needs', 'לא צוין')}
- שירות צבאי: {profile.get('military_or_national_service')}
- אורך שירות: {profile.get('service_length_years', 'לא צוין')} שנים
- תפקיד בשירות: {profile.get('service_role', 'לא צוין')}
- נפגע בשירות: {profile.get('injured_in_service', 'לא צוין')}
- נכות מוכרת: {profile.get('recognized_disability')}
- בעיות בריאות: {profile.get('health_issue')}
- זקוק לסיוע יומיומי: {profile.get('need_daily_assistance', 'לא צוין')}
- עולה חדש: {profile.get('is_new_immigrant')}
- דיור: {profile.get('housing_status', 'לא צוין')}
- חינוך: {profile.get('education', 'לא צוין')}
- קורסים בתשלום: {profile.get('paid_courses', 'לא צוין')}
- סוג עסק: {profile.get('business_type', 'לא צוין')}
- ירידה בעסק: {profile.get('business_decline', 'לא צוין')}
- מקבל מענקי עסק: {profile.get('receiving_business_grants', 'לא צוין')}

פורמט תגובה:

🎯 זכויות שזוהו עבורך:

📋 זכות #1: [שם הזכות]
💡 למה זה מגיע לך: [הסבר קצר מה הזכות]
✅ הסיבה: [לפי אילו נתונים ספציפיים מהשאלון אתה זכאי]
💰 סכום: [סכום מדויק] ₪ ל[חודש/שנה]

---

📋 זכות #2: [שם הזכות]
💡 למה זה מגיע לך: [הסבר קצר מה הזכות]  
✅ הסיבה: [לפי אילו נתונים ספציפיים מהשאלון אתה זכאי]
💰 סכום: [סכום מדויק] ₪ ל[חודש/שנה]

---

📋 זכות #3: [שם הזכות]
💡 למה זה מגיע לך: [הסבר קצר מה הזכות]
✅ הסיבה: [לפי אילו נתונים ספציפיים מהשאלון אתה זכאי] 
💰 סכום: [סכום מדויק] ₪ ל[חודש/שנה]

═══════════════════════════════

💼 סיכום כספי: [סכום כולל] ₪ לחודש

אם אין זכויות מוכחות - כתוב "❌ לא נמצאו זכויות רלוונטיות לפרופיל שלך"."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2  # Lower temperature for more consistent, conservative responses
        )
        gpt_response = response.choices[0].message.content
        
        # Basic validation of GPT response
        if validate_gpt_response(gpt_response):
            return gpt_response
        else:
            print("GPT response failed validation checks")
            if existing_rights:
                return generate_report_from_catalog(profile, existing_rights)
            else:
                return "לא הצלחנו לזהות זכויות מתאימות לפרופיל שלך. מומלץ לפנות ישירות לגורמים הרלוונטיים: ביטוח לאומי, מס הכנסה, או רשות מקומית."
        
    except Exception as e:
        # If web search fails, return message about insufficient rights
        print(f"GPT search failed: {e}")
        if existing_rights:
            return generate_report_from_catalog(profile, existing_rights)
        else:
            return "לא נמצאו זכויות משמעותיות המתאימות לפרופיל שלך. אנא בדוק שוב בעתיד או פנה לגורמים מקצועיים."

def validate_gpt_response(response: str) -> bool:
    """Validate GPT response for common hallucination patterns"""
    import re
    # Check for suspicious content that might indicate hallucination
    suspicious_patterns = [
        r'מענק.*\d{4,}',  # Very high amounts that seem unrealistic
        r'עד.*\d{5,}',    # Claims of very high maximum amounts
        r'משרד.*(?:החלומות|הדמיון|הכסף)',  # Made-up ministry names
        r'זכות.*(?:חדשה|מיוחדת|ייחודית).*\d{4,}',  # Claims of new/special rights with high amounts
        r'קצבה.*\d{5,}',  # Unrealistically high allowances
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, response):
            print(f"Suspicious pattern detected: {pattern}")
            return False
    
    # Check for required realistic elements
    realistic_sources = ['ביטוח לאומי', 'מס הכנסה', 'משרד החינוך', 'משרד הבריאות', 'משרד הבטחון']
    has_realistic_source = any(source in response for source in realistic_sources)
    
    if not has_realistic_source and 'לא נמצאו' not in response:
        print("No realistic government sources found in response")
        return False
    
    return True

def generate_dynamic_questions(profile: dict) -> list:
    """Return the next question to ask based on the profile."""
    # שאלות בסיס
    for question in BASIC_QUESTIONS:
        if not profile.get(question["key"]):
            return [{"key": question["key"], "text": question["question"], "type": question.get("type"), "options": question.get("options")}]

    # שאלות מותנות
    for block in CONDITIONAL_QUESTIONS:
        if block["condition"](profile):
            for question in block["questions"]:
                if isinstance(question, dict):
                    # New format: dictionary with key, question, type, options
                    if not profile.get(question["key"]):
                        return [{"key": question["key"], "text": question["question"], "type": question.get("type"), "options": question.get("options")}]
                else:
                    # Old format: tuple (key, text) or list
                    try:
                        if isinstance(question, (tuple, list)) and len(question) >= 2:
                            key, text = question[0], question[1]
                            if not profile.get(key):
                                return [{"key": key, "text": text}]
                        else:
                            print(f"Warning: Unexpected question format: {question}")
                    except ValueError as e:
                        print(f"Error unpacking question: {question}, error: {e}")
                        continue
    # שאלות משניות
    for block in SECONDARY_QUESTIONS:
        if block["condition"](profile):
            for question in block["questions"]:
                if isinstance(question, dict):
                    if not profile.get(question["key"]):
                        return [{"key": question["key"], "text": question["question"], "type": question.get("type"), "options": question.get("options")}]
                else:
                    # Handle old format if any exists
                    try:
                        if isinstance(question, (tuple, list)) and len(question) >= 2:
                            key, text = question[0], question[1]
                            if not profile.get(key):
                                return [{"key": key, "text": text}]
                    except (ValueError, IndexError):
                        print(f"Error unpacking secondary question: {question}")
                        continue

    return []

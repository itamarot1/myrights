#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rights Validation System - מערכת אימות זכויות
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class RightsValidator:
    """מערכת אימות זכויות מול מקורות ממשלתיים"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.trusted_sources = [
            "btl.gov.il",  # ביטוח לאומי
            "misim.gov.il",  # מס הכנסה
            "moed.gov.il",  # משרד החינוך
            "health.gov.il",  # משרד הבריאות
            "kolzchut.org.il"  # כל זכות - מוכר ומהימן
        ]
    
    def _load_validation_rules(self) -> Dict:
        """טעינת כללי אימות"""
        return {
            "income_thresholds": {
                "2024": {
                    "minimum_wage": 5300,
                    "average_wage": 11500,
                    "tax_threshold": 6790,
                    "disability_allowance_max": 18000
                }
            },
            "age_limits": {
                "child_allowance_max": 18,
                "retirement_age_men": 67,
                "retirement_age_women": 62,
                "military_service_min": 18
            },
            "amounts_ranges": {
                "child_allowance": (150, 300),
                "disability_allowance": (1500, 5000),
                "unemployment_benefit": (1000, 3000),
                "old_age_pension": (1500, 4000)
            }
        }
    
    def validate_right(self, right: Dict, profile: Dict) -> Dict:
        """אימות זכות ספציפית"""
        validation_result = {
            "is_valid": True,
            "confidence_score": 0,
            "issues": [],
            "recommendations": [],
            "last_verified": datetime.now().isoformat()
        }
        
        # 1. בדיקת עקביות פנימית
        internal_check = self._check_internal_consistency(right, profile)
        validation_result["confidence_score"] += internal_check["score"]
        validation_result["issues"].extend(internal_check["issues"])
        
        # 2. בדיקת הגיונות סכומים
        amount_check = self._check_amount_reasonableness(right)
        validation_result["confidence_score"] += amount_check["score"]
        validation_result["issues"].extend(amount_check["issues"])
        
        # 3. בדיקת תקינות קריטריונים
        criteria_check = self._check_criteria_validity(right, profile)
        validation_result["confidence_score"] += criteria_check["score"]
        validation_result["issues"].extend(criteria_check["issues"])
        
        # 4. בדיקת מקור המידע
        source_check = self._check_source_reliability(right)
        validation_result["confidence_score"] += source_check["score"]
        validation_result["issues"].extend(source_check["issues"])
        
        # חישוב ציון אמינות סופי (0-100)
        validation_result["confidence_score"] = min(100, max(0, validation_result["confidence_score"]))
        
        # קביעת סטטוס סופי
        if validation_result["confidence_score"] < 60:
            validation_result["is_valid"] = False
            validation_result["recommendations"].append("יש לבדוק זכות זו ישירות אצל הגורם המטפל")
        elif validation_result["confidence_score"] < 80:
            validation_result["recommendations"].append("מומלץ לוודא פרטים נוספים אצל הגורם הרלוונטי")
        
        return validation_result
    
    def _check_internal_consistency(self, right: Dict, profile: Dict) -> Dict:
        """בדיקת עקביות פנימית"""
        issues = []
        score = 25  # ציון בסיס
        
        # בדיקה: אם זכות דורשת ילדים, המשתמש צריך להיות הורה
        criteria = right.get('eligibility_criteria', {})
        if criteria.get('has_children') and profile.get('has_children') != 'כן':
            issues.append("זכות דורשת ילדים אך המשתמש לא דיווח על ילדים")
            score -= 10
        
        # בדיקה: אם זכות דורשת נכות, המשתמש צריך להיות נכה
        if criteria.get('recognized_disability') and profile.get('recognized_disability') != 'כן':
            issues.append("זכות דורשת נכות מוכרת אך המשתמש לא דיווח על נכות")
            score -= 15
        
        # בדיקה: גיל הגיוני
        age_min = criteria.get('age_min')
        age_max = criteria.get('age_max')
        user_age = profile.get('age')
        
        if user_age and user_age.isdigit():
            age = int(user_age)
            if age_min and age < age_min:
                issues.append(f"גיל המשתמש ({age}) נמוך מהנדרש ({age_min})")
                score -= 20
            if age_max and age > age_max:
                issues.append(f"גיל המשתמש ({age}) גבוה מהמותר ({age_max})")
                score -= 20
        
        return {"score": score, "issues": issues}
    
    def _check_amount_reasonableness(self, right: Dict) -> Dict:
        """בדיקת הגיונות סכומים"""
        issues = []
        score = 25  # ציון בסיס
        
        amount_str = right.get('amount_estimation', '')
        if not amount_str:
            issues.append("חסר מידע על סכום הזכות")
            score -= 5
            return {"score": score, "issues": issues}
        
        # חילוץ מספרים מתיאור הסכום
        numbers = re.findall(r'\d+', amount_str.replace(',', ''))
        if numbers:
            amounts = [int(num) for num in numbers]
            max_amount = max(amounts)
            
            # בדיקות סבירות
            right_name = right.get('name', '').lower()
            
            # קצבת ילדים
            if 'ילד' in right_name and 'קצבת' in right_name:
                expected_range = self.validation_rules["amounts_ranges"]["child_allowance"]
                if not (expected_range[0] <= max_amount <= expected_range[1] * 5):  # עד 5 ילדים
                    issues.append(f"סכום קצבת ילדים ({max_amount}) נראה לא סביר")
                    score -= 10
            
            # זכויות נכות
            elif 'נכות' in right_name or 'נכה' in right_name:
                expected_range = self.validation_rules["amounts_ranges"]["disability_allowance"]
                if not (expected_range[0] <= max_amount <= expected_range[1] * 2):
                    issues.append(f"סכום זכות נכות ({max_amount}) נראה לא סביר")
                    score -= 10
            
            # סכומים מפוצצים
            if max_amount > 100000:
                issues.append(f"סכום גבוה במיוחד ({max_amount:,}) - יש לוודא")
                score -= 15
            
            # סכומים זעירים
            if max_amount < 50:
                issues.append(f"סכום נמוך במיוחד ({max_amount}) - יש לוודא")
                score -= 5
        
        return {"score": score, "issues": issues}
    
    def _check_criteria_validity(self, right: Dict, profile: Dict) -> Dict:
        """בדיקת תקינות קריטריונים"""
        issues = []
        score = 25  # ציון בסיס
        
        criteria = right.get('eligibility_criteria', {})
        
        # בדיקת הכנסה מקסימלית
        income_max = criteria.get('income_max')
        if income_max:
            current_thresholds = self.validation_rules["income_thresholds"]["2024"]
            if income_max > current_thresholds["average_wage"] * 3:
                issues.append(f"סף הכנסה ({income_max:,}) גבוה מדי - חשוד")
                score -= 10
            elif income_max < 1000:
                issues.append(f"סף הכנסה ({income_max}) נמוך מדי - חשוד")
                score -= 5
        
        # בדיקת אחוז נכות
        disability_percentage = criteria.get('disability_percentage')
        if disability_percentage:
            if not (0 <= disability_percentage <= 100):
                issues.append(f"אחוז נכות לא תקין ({disability_percentage})")
                score -= 15
        
        # בדיקת גילאים
        age_min = criteria.get('age_min')
        age_max = criteria.get('age_max')
        if age_min and age_max and age_min > age_max:
            issues.append("גיל מינימלי גבוה מגיל מקסימלי")
            score -= 10
        
        return {"score": score, "issues": issues}
    
    def _check_source_reliability(self, right: Dict) -> Dict:
        """בדיקת אמינות המקור"""
        issues = []
        score = 25  # ציון בסיס
        
        website_url = right.get('website_url', '')
        if website_url:
            # בדיקה אם המקור מהימן
            is_trusted = any(source in website_url for source in self.trusted_sources)
            if is_trusted:
                score += 10
            else:
                issues.append("המקור אינו ממקורות ממשלתיים מוכרים")
                score -= 10
        else:
            issues.append("חסר מידע על מקור הזכות")
            score -= 5
        
        # בדיקת עדכניות
        last_updated = right.get('last_updated')
        if last_updated:
            try:
                update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                days_old = (datetime.now() - update_date.replace(tzinfo=None)).days
                if days_old > 365:
                    issues.append(f"המידע לא עודכן כבר {days_old} ימים")
                    score -= 15
                elif days_old > 180:
                    issues.append(f"המידע לא עודכן {days_old} ימים")
                    score -= 5
            except:
                issues.append("תאריך עדכון לא תקין")
                score -= 5
        else:
            issues.append("חסר מידע על תאריך עדכון")
            score -= 10
        
        return {"score": score, "issues": issues}
    
    def validate_user_profile(self, profile: Dict) -> Dict:
        """אימות תקינות פרופיל המשתמש"""
        issues = []
        
        # בדיקת גיל
        age = profile.get('age')
        if age and age.isdigit():
            age_int = int(age)
            if not (0 <= age_int <= 120):
                issues.append("גיל לא סביר")
        elif age:
            issues.append("גיל לא תקין")
        
        # בדיקת הכנסה
        income = profile.get('avg_monthly_income')
        if income and income.isdigit():
            income_int = int(income)
            if income_int > 100000:
                issues.append("הכנסה גבוהה במיוחד - יש לוודא")
            elif income_int < 0:
                issues.append("הכנסה שלילית")
        
        # בדיקות עקביות
        if profile.get('has_children') == 'כן' and not profile.get('num_children'):
            issues.append("דווח על ילדים אבל לא נמסר מספרם")
        
        if profile.get('recognized_disability') == 'כן' and not profile.get('disability_percentage'):
            issues.append("דווח על נכות אבל לא נמסר אחוז הנכות")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "confidence_score": max(0, 100 - len(issues) * 10)
        }

def create_validation_report(rights: List[Dict], profile: Dict, validator: RightsValidator) -> Dict:
    """יצירת דוח אימות מקיף"""
    
    # אימות פרופיל משתמש
    profile_validation = validator.validate_user_profile(profile)
    
    # אימות כל זכות
    rights_validations = []
    total_confidence = 0
    valid_rights = 0
    
    for right in rights:
        validation = validator.validate_right(right, profile)
        rights_validations.append({
            "right_name": right.get('name', 'לא ידוע'),
            "validation": validation
        })
        
        if validation["is_valid"]:
            valid_rights += 1
        total_confidence += validation["confidence_score"]
    
    avg_confidence = total_confidence / len(rights) if rights else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "profile_validation": profile_validation,
        "rights_count": len(rights),
        "valid_rights_count": valid_rights,
        "average_confidence": avg_confidence,
        "rights_validations": rights_validations,
        "overall_assessment": _get_overall_assessment(avg_confidence, valid_rights, len(rights)),
        "recommendations": _get_general_recommendations(avg_confidence, profile_validation)
    }

def _get_overall_assessment(avg_confidence: float, valid_rights: int, total_rights: int) -> str:
    """הערכה כללית של מהימנות הדוח"""
    if avg_confidence >= 85 and valid_rights == total_rights:
        return "מהימנות גבוהה - הזכויות נראות מדויקות ועדכניות"
    elif avg_confidence >= 70:
        return "מהימנות בינונית-גבוהה - רוב הזכויות נראות תקינות"
    elif avg_confidence >= 60:
        return "מהימנות בינונית - מומלץ לוודא פרטים נוספים"
    else:
        return "מהימנות נמוכה - יש לבדוק ישירות אצל הגורמים המטפלים"

def _get_general_recommendations(avg_confidence: float, profile_validation: Dict) -> List[str]:
    """המלצות כלליות"""
    recommendations = []
    
    if not profile_validation["is_valid"]:
        recommendations.append("יש לוודא נכונות הפרטים האישיים שהוזנו")
    
    if avg_confidence < 70:
        recommendations.append("מומלץ לפנות ישירות לביטוח לאומי לאישור הזכויות")
    
    recommendations.append("המידע מוצג לצורך הכוונה בלבד ואינו מהווה ייעוץ משפטי")
    recommendations.append("זכויות עשויות להשתנות - מומלץ לעדכן מעת לעת")
    
    return recommendations
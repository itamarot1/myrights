#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test script for rights matching system validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt_response import filter_matching_rights, check_eligibility_match, load_rights_catalog
import json

def analyze_rights_catalog():
    """Analyze the rights catalog structure"""
    rights_catalog = load_rights_catalog()
    print(f"Rights catalog analysis:")
    print(f"Total rights: {len(rights_catalog)}")
    
    # Analyze categories
    categories = {}
    for right in rights_catalog:
        category = right.get('category', 'Unknown')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print(f"\nCategories breakdown:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    
    # Analyze common criteria
    criteria_stats = {}
    for right in rights_catalog:
        eligibility = right.get('eligibility_criteria', {})
        for key, value in eligibility.items():
            if value is not None and value != [] and value != ['כל']:
                if key not in criteria_stats:
                    criteria_stats[key] = 0
                criteria_stats[key] += 1
    
    print(f"\nMost common eligibility criteria:")
    for criteria, count in sorted(criteria_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {criteria}: {count}")
    
    return rights_catalog

def test_profile_matching(profile, profile_name):
    """Test how profile matches against catalog"""
    print(f"\n{'='*80}")
    print(f"Testing Profile: {profile_name}")
    print('='*80)
    
    # Show profile details
    print("Profile details:")
    for key, value in profile.items():
        print(f"  {key}: {value}")
    
    # Test filtering
    matching_rights = filter_matching_rights(profile, min_value_threshold=500)
    print(f"\nMatching rights found: {len(matching_rights)}")
    
    if matching_rights:
        print(f"\nMatched rights:")
        for i, right in enumerate(matching_rights, 1):
            amount = right.get('amount_estimation', 'Unknown')
            category = right.get('category', 'Unknown')
            print(f"  {i}. {right['name']}")
            print(f"     Category: {category}")
            print(f"     Amount: {amount}")
            
            # Show why it matched
            eligibility = right.get('eligibility_criteria', {})
            matching_criteria = []
            for key, value in eligibility.items():
                if value is not None and value != [] and value != ['כל']:
                    profile_val = profile.get(key)
                    if key in ['age_min', 'age_max'] and profile.get('age'):
                        age = int(profile['age'])
                        if key == 'age_min' and value <= age:
                            matching_criteria.append(f"age >= {value}")
                        elif key == 'age_max' and value >= age:
                            matching_criteria.append(f"age <= {value}")
                    elif key == 'income_max' and profile.get('avg_monthly_income'):
                        try:
                            income = int(profile['avg_monthly_income'].replace(',', ''))
                            if income <= value:
                                matching_criteria.append(f"income <= {value}")
                        except:
                            pass
                    elif isinstance(value, bool) and profile_val:
                        profile_bool = str(profile_val).strip().lower() in ['כן', 'true', 'yes']
                        if profile_bool == value:
                            matching_criteria.append(f"{key}={value}")
                    elif isinstance(value, list) and profile_val:
                        if profile_val in value:
                            matching_criteria.append(f"{key} in {value}")
            
            if matching_criteria:
                print(f"     Matching criteria: {', '.join(matching_criteria[:3])}")
            print()
    else:
        print("No matching rights found")
        
        # Test individual criteria against sample rights
        rights_catalog = load_rights_catalog()
        print(f"\nTesting against first 5 rights to see why no matches:")
        for i, right in enumerate(rights_catalog[:5]):
            eligibility = right.get('eligibility_criteria', {})
            result = check_eligibility_match(profile, eligibility)
            print(f"  {right['name']}: {'MATCH' if result else 'NO MATCH'}")
            if not result:
                # Show which criteria failed
                failed_criteria = []
                
                # Age check
                age = profile.get('age')
                if age and age.isdigit():
                    age = int(age)
                    age_min = eligibility.get('age_min')
                    age_max = eligibility.get('age_max')
                    if age_min and age < age_min:
                        failed_criteria.append(f"age {age} < min {age_min}")
                    if age_max and age > age_max:
                        failed_criteria.append(f"age {age} > max {age_max}")
                
                # Income check
                income_max = eligibility.get('income_max')
                user_income = profile.get('avg_monthly_income')
                if income_max and user_income:
                    try:
                        import re
                        income_numbers = re.findall(r'\d+', str(user_income).replace(',', ''))
                        if income_numbers:
                            user_income_num = int(income_numbers[0])
                            if user_income_num > income_max:
                                failed_criteria.append(f"income {user_income_num} > max {income_max}")
                    except:
                        pass
                
                # Boolean criteria
                boolean_checks = [
                    ('recognized_disability', 'recognized_disability'),
                    ('has_children', 'has_children'),
                    ('is_new_immigrant', 'is_new_immigrant'),
                ]
                
                for profile_key, criteria_key in boolean_checks:
                    profile_val = profile.get(profile_key)
                    criteria_val = eligibility.get(criteria_key)
                    if criteria_val is not None:
                        profile_bool = str(profile_val).strip().lower() in ['כן', 'true', 'yes']
                        if criteria_val != profile_bool:
                            failed_criteria.append(f"{criteria_key}: need {criteria_val}, have {profile_bool}")
                
                if failed_criteria:
                    print(f"    Failed: {', '.join(failed_criteria[:2])}")

# Test profiles for different scenarios
test_profiles = [
    {
        "name": "Military Veteran (25-35, with disability)",
        "profile": {
            "age": "30",
            "gender": "זכר",
            "marital_status": "נשוי",
            "employment_status": "שכיר",
            "recognized_disability": "כן",
            "health_issue": "כן",
            "military_or_national_service": "שירות צבאי (צה\"ל)",
            "service_length_years": "4",
            "recognized_combat_or_disabled": "כן",
            "injured_in_service": "כן",
            "has_children": "כן",
            "num_children": "1",
            "avg_monthly_income": "8000",
            "disability_percentage": "50",
            "filed_disability_claim": "כן"
        }
    },
    {
        "name": "Family with children (employed, middle income)",
        "profile": {
            "age": "35",
            "gender": "נקבה",
            "marital_status": "נשוי",
            "employment_status": "שכיר",
            "recognized_disability": "לא",
            "health_issue": "לא",
            "military_or_national_service": "לא שירתתי",
            "has_children": "כן",
            "children_under_18": "כן",
            "num_children": "2",
            "children_ages": "5,8",
            "child_special_needs": "לא",
            "avg_monthly_income": "12000",
            "is_new_immigrant": "לא"
        }
    },
    {
        "name": "New immigrant (various backgrounds)",
        "profile": {
            "age": "32",
            "gender": "זכר",
            "marital_status": "נשוי",
            "employment_status": "מובטל",
            "recognized_disability": "לא",
            "health_issue": "לא",
            "military_or_national_service": "לא שירתתי",
            "has_children": "כן",
            "num_children": "1",
            "is_new_immigrant": "כן",
            "avg_monthly_income": "3000",
            "education": "תואר ראשון"
        }
    },
    {
        "name": "Disability profile (various conditions)",
        "profile": {
            "age": "40",
            "gender": "נקבה",
            "marital_status": "גרוש",
            "employment_status": "מובטל",
            "recognized_disability": "כן",
            "health_issue": "כן",
            "military_or_national_service": "שירות לאומי",
            "has_children": "כן",
            "num_children": "2",
            "disability_percentage": "75",
            "need_daily_assistance": "כן",
            "filed_disability_claim": "כן",
            "avg_monthly_income": "2000"
        }
    },
    {
        "name": "High income (should match fewer rights)",
        "profile": {
            "age": "45",
            "gender": "זכר",
            "marital_status": "נשוי",
            "employment_status": "עצמאי",
            "recognized_disability": "לא",
            "health_issue": "לא",
            "military_or_national_service": "שירות צבאי (צה\"ל)",
            "has_children": "כן",
            "num_children": "3",
            "avg_monthly_income": "25000",
            "is_new_immigrant": "לא"
        }
    }
]

def main():
    print("Comprehensive Rights System Analysis")
    print("=" * 80)
    
    # First analyze the catalog
    analyze_rights_catalog()
    
    # Test each profile
    for test_case in test_profiles:
        test_profile_matching(test_case["profile"], test_case["name"])
    
    print(f"\n{'='*80}")
    print("Analysis Complete")
    print('='*80)

if __name__ == "__main__":
    main()
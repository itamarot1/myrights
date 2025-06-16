#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug filtering logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt_response import load_rights_catalog, has_specific_criteria, check_eligibility_match, has_significant_value

def debug_filtering():
    """Debug why certain rights are being filtered out"""
    rights_catalog = load_rights_catalog()
    
    # Test profile - family with children
    test_profile = {
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
    
    print("Debug: Family Profile Filtering")
    print("=" * 50)
    
    # Test first 10 rights
    for i, right in enumerate(rights_catalog[:10]):
        name = right['name']
        eligibility = right.get('eligibility_criteria', {})
        amount = right.get('amount_estimation', '')
        
        print(f"\n{i+1}. {name}")
        print(f"   Amount: {amount}")
        
        # Test each filter stage
        has_specific = has_specific_criteria(eligibility)
        print(f"   Has specific criteria: {has_specific}")
        
        if has_specific:
            eligibility_match = check_eligibility_match(test_profile, eligibility)
            print(f"   Eligibility match: {eligibility_match}")
            
            if eligibility_match:
                significant_value = has_significant_value(amount, 500)
                print(f"   Has significant value: {significant_value}")
                
                if significant_value:
                    print("   >>> WOULD BE INCLUDED <<<")
                else:
                    print("   >>> FILTERED OUT: Low value")
            else:
                print("   >>> FILTERED OUT: No eligibility match")
                # Show why it failed
                failed_reasons = []
                
                # Income check
                income_max = eligibility.get('income_max')
                if income_max:
                    user_income = test_profile.get('avg_monthly_income')
                    if user_income:
                        try:
                            user_income_num = int(user_income.replace(',', ''))
                            if user_income_num > income_max:
                                failed_reasons.append(f"Income {user_income_num} > {income_max}")
                        except:
                            pass
                
                # Boolean checks
                boolean_checks = [
                    ('recognized_disability', 'recognized_disability'),
                    ('has_children', 'has_children'),
                    ('is_new_immigrant', 'is_new_immigrant'),
                ]
                
                for profile_key, criteria_key in boolean_checks:
                    profile_val = test_profile.get(profile_key)
                    criteria_val = eligibility.get(criteria_key)
                    if criteria_val is not None:
                        profile_bool = str(profile_val).strip().lower() in ['כן', 'true', 'yes']
                        if criteria_val != profile_bool:
                            failed_reasons.append(f"{criteria_key}: need {criteria_val}, got {profile_bool}")
                
                if failed_reasons:
                    print(f"   Failed reasons: {', '.join(failed_reasons)}")
        else:
            print("   >>> FILTERED OUT: No specific criteria")
            
            # Show why it's not specific
            meaningful_criteria = 0
            for key, value in eligibility.items():
                if value is not None and value != [] and value != ['כל']:
                    if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                        meaningful_criteria += 1
            print(f"   Meaningful criteria count: {meaningful_criteria} (need >= 2)")

def find_immigrant_rights():
    """Look for new immigrant specific rights"""
    rights_catalog = load_rights_catalog()
    
    print("\n" + "=" * 50)
    print("Looking for New Immigrant Rights")
    print("=" * 50)
    
    immigrant_rights = []
    for right in rights_catalog:
        eligibility = right.get('eligibility_criteria', {})
        name = right['name']
        
        # Check for immigrant-related criteria
        is_immigrant = eligibility.get('is_new_immigrant')
        if is_immigrant == True:
            immigrant_rights.append(right)
        elif 'עולה' in name or 'עלייה' in name or 'חדש' in name:
            immigrant_rights.append(right)
    
    print(f"Found {len(immigrant_rights)} immigrant-related rights:")
    for right in immigrant_rights:
        print(f"- {right['name']}")
        eligibility = right.get('eligibility_criteria', {})
        print(f"  is_new_immigrant: {eligibility.get('is_new_immigrant')}")
        print(f"  Amount: {right.get('amount_estimation', 'Unknown')}")

def find_family_rights():
    """Look for family/children rights"""
    rights_catalog = load_rights_catalog()
    
    print("\n" + "=" * 50)
    print("Looking for Family/Children Rights")
    print("=" * 50)
    
    family_rights = []
    for right in rights_catalog:
        eligibility = right.get('eligibility_criteria', {})
        name = right['name']
        
        # Check for family-related criteria
        has_children = eligibility.get('has_children')
        child_special_needs = eligibility.get('child_special_needs')
        
        if has_children == True or child_special_needs == True:
            family_rights.append(right)
        elif 'ילד' in name or 'משפח' in name or 'הור' in name:
            family_rights.append(right)
    
    print(f"Found {len(family_rights)} family-related rights:")
    for right in family_rights[:10]:  # Show first 10
        print(f"- {right['name']}")
        eligibility = right.get('eligibility_criteria', {})
        print(f"  has_children: {eligibility.get('has_children')}")
        print(f"  child_special_needs: {eligibility.get('child_special_needs')}")
        print(f"  income_max: {eligibility.get('income_max')}")
        print(f"  Amount: {right.get('amount_estimation', 'Unknown')}")
        print()

if __name__ == "__main__":
    debug_filtering()
    find_immigrant_rights()
    find_family_rights()
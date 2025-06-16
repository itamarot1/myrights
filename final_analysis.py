#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Final comprehensive analysis of the rights matching system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt_response import load_rights_catalog, has_specific_criteria, check_eligibility_match, has_significant_value

def analyze_catalog_issues():
    """Analyze issues with the rights catalog"""
    rights_catalog = load_rights_catalog()
    
    print("FINAL ANALYSIS: Rights Catalog Issues")
    print("=" * 60)
    
    # Count rights by specificity
    specific_rights = 0
    non_specific_rights = 0
    disability_focused = 0
    family_focused = 0
    high_income_limit = 0
    
    for right in rights_catalog:
        eligibility = right.get('eligibility_criteria', {})
        name = right['name']
        
        if has_specific_criteria(eligibility):
            specific_rights += 1
        else:
            non_specific_rights += 1
            
        # Check if disability-focused
        if (eligibility.get('recognized_disability') == True or 
            'נכות' in name or 'נכה' in name):
            disability_focused += 1
            
        # Check if family-focused
        if (eligibility.get('has_children') == True or 
            'ילד' in name or 'הור' in name or 'משפח' in name):
            family_focused += 1
            
        # Check income limits
        income_max = eligibility.get('income_max')
        if income_max and income_max >= 10000:
            high_income_limit += 1
    
    print(f"Total rights in catalog: {len(rights_catalog)}")
    print(f"Rights with specific criteria: {specific_rights}")
    print(f"Rights with non-specific criteria: {non_specific_rights}")
    print(f"Disability-focused rights: {disability_focused}")
    print(f"Family-focused rights: {family_focused}")
    print(f"Rights with high income limits (≥10,000): {high_income_limit}")
    
    print(f"\nPercentage breakdown:")
    print(f"- Specific criteria: {specific_rights/len(rights_catalog)*100:.1f}%")
    print(f"- Non-specific criteria: {non_specific_rights/len(rights_catalog)*100:.1f}%")
    print(f"- Disability-focused: {disability_focused/len(rights_catalog)*100:.1f}%")
    print(f"- Family-focused: {family_focused/len(rights_catalog)*100:.1f}%")

def test_profile_scenarios():
    """Test specific profile scenarios and identify issues"""
    
    test_scenarios = [
        {
            "name": "Military Veteran (disability)",
            "profile": {
                "age": "30",
                "employment_status": "שכיר",
                "recognized_disability": "כן",
                "military_or_national_service": "שירות צבאי (צה\"ל)",
                "service_length_years": "4",
                "avg_monthly_income": "8000",
                "disability_percentage": "50",
                "filed_disability_claim": "כן"
            },
            "expected_categories": ["נכות", "בריאות ונכות", "זכויות ייחודיות לאוכלוסיות ספציפיות"]
        },
        {
            "name": "Middle-class Family",
            "profile": {
                "age": "35",
                "employment_status": "שכיר",
                "recognized_disability": "לא",
                "has_children": "כן",
                "num_children": "2",
                "avg_monthly_income": "12000"
            },
            "expected_categories": ["משפחה והורות", "מיסוי וחיסכון"]
        },
        {
            "name": "New Immigrant",
            "profile": {
                "age": "32",
                "employment_status": "מובטל",
                "recognized_disability": "לא",
                "is_new_immigrant": "כן",
                "avg_monthly_income": "3000"
            },
            "expected_categories": ["זכויות ייחודיות לאוכלוסיות ספציפיות", "עבודה ותעסוקה"]
        },
        {
            "name": "Low-income Disability",
            "profile": {
                "age": "40",
                "employment_status": "מובטל",
                "recognized_disability": "כן",
                "disability_percentage": "75",
                "avg_monthly_income": "2000",
                "filed_disability_claim": "כן"
            },
            "expected_categories": ["נכות", "בריאות ונכות"]
        }
    ]
    
    print(f"\n{'='*60}")
    print("SCENARIO TESTING")
    print('='*60)
    
    rights_catalog = load_rights_catalog()
    
    for scenario in test_scenarios:
        profile = scenario["profile"]
        name = scenario["name"]
        expected = scenario["expected_categories"]
        
        print(f"\nScenario: {name}")
        print("-" * 40)
        
        # Find matching rights manually
        potential_matches = []
        actual_matches = []
        
        for right in rights_catalog:
            eligibility = right.get('eligibility_criteria', {})
            category = right.get('category', 'Unknown')
            
            # Check if it should match based on expected categories
            if any(exp_cat in category for exp_cat in expected):
                potential_matches.append(right)
                
                # Check if it actually matches
                if has_specific_criteria(eligibility):
                    if check_eligibility_match(profile, eligibility):
                        amount = right.get('amount_estimation', '')
                        if has_significant_value(amount, 500):
                            actual_matches.append(right)
        
        print(f"Potential matches (by category): {len(potential_matches)}")
        print(f"Actual matches (after filtering): {len(actual_matches)}")
        
        if len(actual_matches) < len(potential_matches):
            print(f"ISSUE: {len(potential_matches) - len(actual_matches)} rights lost in filtering")
            
            # Analyze why rights were filtered out
            filtered_out = []
            for right in potential_matches:
                if right not in actual_matches:
                    eligibility = right.get('eligibility_criteria', {})
                    reason = "Unknown"
                    
                    if not has_specific_criteria(eligibility):
                        reason = "Non-specific criteria"
                    elif not check_eligibility_match(profile, eligibility):
                        reason = "Eligibility mismatch"
                    else:
                        amount = right.get('amount_estimation', '')
                        if not has_significant_value(amount, 500):
                            reason = "Low value"
                    
                    filtered_out.append((right['name'], reason))
            
            print("Filtered out rights:")
            for name, reason in filtered_out[:5]:  # Show first 5
                print(f"  - {name}: {reason}")
        
        print(f"Final matches: {[r['name'] for r in actual_matches]}")

def identify_improvements():
    """Identify specific improvements needed"""
    
    print(f"\n{'='*60}")
    print("IMPROVEMENT RECOMMENDATIONS")
    print('='*60)
    
    improvements = [
        {
            "issue": "Too many rights have non-specific criteria",
            "impact": "Family and general population rights are being filtered out",
            "solution": "Update rights data to include more specific eligibility criteria like has_children=true for family rights"
        },
        {
            "issue": "Income limits are too low for middle-class families",
            "impact": "Families earning 12,000+ NIS are excluded from most rights",
            "solution": "Review and update income thresholds to reflect 2024 economic reality"
        },
        {
            "issue": "New immigrant rights are not properly tagged",
            "impact": "New immigrants get no matches despite having dedicated rights",
            "solution": "Add is_new_immigrant=true to relevant rights in the catalog"
        },
        {
            "issue": "Over-reliance on disability-related rights",
            "impact": "System appears biased toward disability benefits",
            "solution": "Ensure broader range of rights have specific criteria"
        },
        {
            "issue": "Value estimation is inconsistent",
            "impact": "Some valuable rights may be filtered out due to 'משתנה' amounts",
            "solution": "Standardize amount estimation format and provide ranges where possible"
        }
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"{i}. ISSUE: {improvement['issue']}")
        print(f"   IMPACT: {improvement['impact']}")
        print(f"   SOLUTION: {improvement['solution']}")
        print()

if __name__ == "__main__":
    analyze_catalog_issues()
    test_profile_scenarios()
    identify_improvements()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Load rights data
with open('rights_data.json', 'r', encoding='utf-8') as f:
    rights = json.load(f)

# Rights that should specifically target military veterans
military_specific_rights = [
    'מלגות לחיילים משוחררים',
    'נקודות זיכוי לחיילים משוחררים', 
    'זכויות לחיילים משוחררים'
]

print("Fixing military-specific rights criteria...")

# Update military-specific rights
for right in rights:
    name = right.get('name', '')
    
    if name in military_specific_rights:
        criteria = right.get('eligibility_criteria', {})
        print(f"\nUpdating: {name}")
        print(f"  Before: military_service = {criteria.get('military_service')}")
        
        # Update military service criteria to be specific
        criteria['military_service'] = ['שירות צבאי (צה"ל)', 'שירות צבאי']
        
        # For scholarship specifically, add age criteria (typically for younger veterans)
        if 'מלגות' in name:
            criteria['age_max'] = 35  # Scholarships typically for younger people
            
        # For tax credits, no additional age limit needed
        # For general rights, no additional criteria needed
        
        print(f"  After:  military_service = {criteria.get('military_service')}")
        if 'age_max' in criteria:
            print(f"  Also added: age_max = {criteria.get('age_max')}")

# Save the updated data
with open('rights_data.json', 'w', encoding='utf-8') as f:
    json.dump(rights, f, ensure_ascii=False, indent=2)

print("\n✅ Military rights criteria updated successfully!")
print("\nNow testing the updated rights...")

# Test the fixes
from gpt_response import filter_matching_rights, has_specific_criteria

veteran_profile = {
    'age': '28',
    'gender': 'זכר',
    'marital_status': 'רווק',
    'employment_status': 'שכיר',
    'military_service': 'שירות צבאי (צה"ל)',
    'service_length_years': '5',
    'avg_monthly_income': '8000',
    'has_children': 'לא',
    'recognized_disability': 'לא',
    'health_issue': 'לא',
    'is_new_immigrant': 'לא'
}

print(f"\nTesting veteran profile after fix:")
matches = filter_matching_rights(veteran_profile, min_value_threshold=0)
print(f'Matches found: {len(matches)}')
for match in matches:
    print(f'- {match["name"]}')

# Check if the specific rights now have meaningful criteria
print(f"\nChecking if military rights now pass has_specific_criteria:")
for right in rights:
    if right.get('name') in military_specific_rights:
        criteria = right.get('eligibility_criteria', {})
        has_criteria = has_specific_criteria(criteria)
        print(f'{right["name"]}: {has_criteria}')
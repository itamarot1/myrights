#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gpt_response import has_specific_criteria
import json

# Check the military scholarship right
with open('rights_data.json', 'r', encoding='utf-8') as f:
    rights = json.load(f)

# Find military-related rights
military_rights = []
for right in rights:
    if 'חיילים משוחררים' in right.get('name', '') or 'זכויות לחיילים משוחררים' == right.get('name', ''):
        military_rights.append(right)

for right in military_rights:
    criteria = right.get('eligibility_criteria', {})
    print(f'Right: {right["name"]}')
    print(f'has_specific_criteria: {has_specific_criteria(criteria)}')
    
    # Count specific criteria manually
    meaningful_criteria = 0
    for key, value in criteria.items():
        is_all = value == ['כל']
        is_empty = value is None or value == []
        if not is_all and not is_empty:
            if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                meaningful_criteria += 1
                print(f'  {key}: {value} (counts as specific)')
    print(f'Total meaningful criteria: {meaningful_criteria}')
    print('-' * 40)
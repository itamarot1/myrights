#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('rights_data.json', 'r', encoding='utf-8') as f:
    rights = json.load(f)

print('Rights that should specifically target military veterans:')
target_names = ['חיילים', 'צבא', 'משוחררים', 'שירות צבאי']
for right in rights:
    name = right.get('name', '')
    if any(target in name for target in target_names):
        criteria = right.get('eligibility_criteria', {})
        military_service = criteria.get('military_service', [])
        print(f'\n{name}:')
        print(f'  military_service: {military_service}')
        if military_service != ['כל']:
            print('  ^^ This has specific military criteria!')
        else:
            print('  ^^ This should have specific military criteria but uses generic ["כל"]')
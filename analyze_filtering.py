#!/usr/bin/env python3
"""
Script to analyze the has_specific_criteria function and understand why so many rights are filtered out.
"""

import json
from gpt_response import has_specific_criteria

def load_rights_data():
    """Load the rights data from JSON file"""
    with open('rights_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_criteria_filtering():
    """Analyze which rights pass/fail the criteria filtering"""
    rights_data = load_rights_data()
    
    passed_rights = []
    failed_rights = []
    
    for right in rights_data:
        eligibility = right.get('eligibility_criteria', {})
        if has_specific_criteria(eligibility):
            passed_rights.append(right)
        else:
            failed_rights.append(right)
    
    print(f"Total rights: {len(rights_data)}")
    print(f"Rights that PASS filtering: {len(passed_rights)}")
    print(f"Rights that FAIL filtering: {len(failed_rights)}")
    print(f"Pass rate: {len(passed_rights)/len(rights_data)*100:.1f}%")
    print()
    
    # Analyze why rights are failing
    print("=== ANALYSIS OF FAILED RIGHTS ===")
    print()
    
    # Sample some failed rights to understand patterns
    print("Sample of rights that FAILED filtering:")
    print("-" * 50)
    
    for i, right in enumerate(failed_rights[:10]):
        print(f"{i+1}. {right['name']}")
        eligibility = right.get('eligibility_criteria', {})
        
        # Count meaningful criteria according to current logic
        meaningful_count = 0
        criteria_details = []
        
        for key, value in eligibility.items():
            if value is not None and value != [] and value != ['כל']:
                if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                    meaningful_count += 1
                    criteria_details.append(f"{key}: {value}")
        
        print(f"   Meaningful criteria count: {meaningful_count} (need ≥2)")
        print(f"   Specific criteria: {criteria_details}")
        print(f"   Amount: {right.get('amount_estimation', 'N/A')}")
        print()
    
    print("=== ANALYSIS OF PASSED RIGHTS ===")
    print()
    
    # Sample some passed rights
    print("Sample of rights that PASSED filtering:")
    print("-" * 50)
    
    for i, right in enumerate(passed_rights[:5]):
        print(f"{i+1}. {right['name']}")
        eligibility = right.get('eligibility_criteria', {})
        
        # Count meaningful criteria according to current logic
        meaningful_count = 0
        criteria_details = []
        
        for key, value in eligibility.items():
            if value is not None and value != [] and value != ['כל']:
                if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                    meaningful_count += 1
                    criteria_details.append(f"{key}: {value}")
        
        print(f"   Meaningful criteria count: {meaningful_count}")
        print(f"   Specific criteria: {criteria_details}")
        print(f"   Amount: {right.get('amount_estimation', 'N/A')}")
        print()
    
    # Analyze patterns in generic criteria
    print("=== ANALYSIS OF GENERIC CRITERIA PATTERNS ===")
    print()
    
    generic_patterns = {}
    
    for right in failed_rights:
        eligibility = right.get('eligibility_criteria', {})
        for key, value in eligibility.items():
            if value == ['כל'] or value == [] or value is None:
                if key not in generic_patterns:
                    generic_patterns[key] = 0
                generic_patterns[key] += 1
    
    print("Most common generic criteria (in failed rights):")
    for key, count in sorted(generic_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count} rights have generic/empty values")
    
    print()
    
    # Check if there are legitimate rights with few specific criteria
    print("=== POTENTIALLY OVER-FILTERED RIGHTS ===")
    print()
    
    potentially_good_rights = []
    for right in failed_rights:
        # Look for rights that might be valuable but have few specific criteria
        amount = right.get('amount_estimation', '')
        if amount and any(char.isdigit() for char in amount):
            # Extract number from amount
            import re
            numbers = re.findall(r'\d+', amount.replace(',', ''))
            if numbers:
                max_amount = max(int(num) for num in numbers)
                if max_amount >= 1000:  # Significant amount
                    potentially_good_rights.append((right, max_amount))
    
    # Sort by amount
    potentially_good_rights.sort(key=lambda x: x[1], reverse=True)
    
    print("High-value rights that were filtered out:")
    print("-" * 50)
    
    for right, amount in potentially_good_rights[:10]:
        print(f"• {right['name']}")
        print(f"  Amount: {right.get('amount_estimation', 'N/A')}")
        
        eligibility = right.get('eligibility_criteria', {})
        meaningful_count = 0
        for key, value in eligibility.items():
            if value is not None and value != [] and value != ['כל']:
                if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                    meaningful_count += 1
        
        print(f"  Criteria count: {meaningful_count}/2 required")
        
        # Show what specific criteria it does have
        specific_criteria = []
        for key, value in eligibility.items():
            if value is not None and value != [] and value != ['כל']:
                if isinstance(value, bool) or (isinstance(value, list) and len(value) < 5):
                    specific_criteria.append(f"{key}={value}")
        
        print(f"  Has: {', '.join(specific_criteria[:3])}")
        print()

if __name__ == "__main__":
    analyze_criteria_filtering()
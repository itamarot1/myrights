#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for new worker rights functionality
"""

from gpt_response import filter_matching_rights, get_detailed_rights_report

def test_worker_rights():
    """Test that new worker rights appear in results"""
    print("🧪 בדיקת זכויות עובדים חדשות")
    print("="*50)
    
    # Profile of a typical employee
    worker_profile = {
        'age': '35',
        'gender': 'זכר', 
        'employment_status': 'שכיר',
        'avg_monthly_income': '8000',
        'has_children': 'לא',
        'recognized_disability': 'לא',
        'health_issue': 'לא',
        'military_or_national_service': 'שירות צבאי (צה"ל)',
        'is_new_immigrant': 'לא'
    }
    
    print("פרופיל עובד:")
    for key, value in worker_profile.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50)
    
    # Test direct filter
    print("בדיקה ישירה עם filter_matching_rights:")
    rights = filter_matching_rights(worker_profile, min_value_threshold=500)
    
    worker_rights_found = []
    for i, right in enumerate(rights, 1):
        name = right['name']
        amount = right.get('amount_estimation', 'לא ידוע')
        if any(word in name for word in ['דמי מחלה', 'חופשה', 'פיצוי']):
            worker_rights_found.append(name)
            print(f"✅ {i}. {name} - {amount}")
        else:
            print(f"{i}. {name} - {amount}")
    
    print(f"\nזכויות עובדים שנמצאו: {len(worker_rights_found)}")
    for right in worker_rights_found:
        print(f"  - {right}")
    
    # Test through full report generation
    print("\n" + "="*50)
    print("בדיקה דרך get_detailed_rights_report:")
    
    report = get_detailed_rights_report(worker_profile, [])
    
    # Check if worker rights appear in report
    worker_rights_in_report = []
    if 'דמי מחלה' in report:
        worker_rights_in_report.append('דמי מחלה')
    if 'חופשה שנתית' in report:
        worker_rights_in_report.append('חופשה שנתית')  
    if 'פיצויי פיטורים' in report:
        worker_rights_in_report.append('פיצויי פיטורים')
    
    print(f"זכויות עובדים בדוח: {len(worker_rights_in_report)}")
    for right in worker_rights_in_report:
        print(f"  - {right}")
    
    # Display partial report
    print(f"\nחלק מהדוח (500 תווים ראשונים):")
    print(report[:500] + "...")
    
    return len(worker_rights_found) > 0, len(worker_rights_in_report) > 0

def test_soldier_rights():
    """Test that new soldier rights appear in results"""
    print("\n" + "🎖️ בדיקת זכויות חיילים משוחררים")
    print("="*50)
    
    # Profile of a discharged soldier
    soldier_profile = {
        'age': '23',
        'gender': 'זכר',
        'employment_status': 'סטודנט',
        'military_or_national_service': 'שירות צבאי (צה"ל)',
        'service_length_years': '3',
        'education': 'בגרות',
        'has_children': 'לא',
        'recognized_disability': 'לא',
        'health_issue': 'לא',
        'is_new_immigrant': 'לא'
    }
    
    print("פרופיל חייל משוחרר:")
    for key, value in soldier_profile.items():
        print(f"  {key}: {value}")
    
    rights = filter_matching_rights(soldier_profile, min_value_threshold=500)
    
    soldier_rights_found = []
    for i, right in enumerate(rights, 1):
        name = right['name']
        amount = right.get('amount_estimation', 'לא ידוע')
        if any(word in name for word in ['ממדים', 'מענק שחרור', 'IMPACT', 'מלגת']):
            soldier_rights_found.append(name)
            print(f"✅ {i}. {name} - {amount}")
        else:
            print(f"{i}. {name} - {amount}")
    
    print(f"\nזכויות חיילים שנמצאו: {len(soldier_rights_found)}")
    for right in soldier_rights_found:
        print(f"  - {right}")
    
    return len(soldier_rights_found) > 0

if __name__ == "__main__":
    print("בדיקת זכויות חדשות שנוספו למערכת")
    print("="*60)
    
    worker_direct, worker_report = test_worker_rights()
    soldier_success = test_soldier_rights()
    
    print("\n" + "="*60)
    print("תוצאות הבדיקה:")
    print(f"✅ זכויות עובדים בסינון: {'מוצלח' if worker_direct else 'נכשל'}")
    print(f"✅ זכויות עובדים בדוח: {'מוצלח' if worker_report else 'נכשל'}")
    print(f"✅ זכויות חיילים: {'מוצלח' if soldier_success else 'נכשל'}")
    
    if worker_direct and soldier_success:
        print("\n🎯 המשימה הראשונה הושלמה בהצלחה!")
        print("המאגר עודכן בזכויות חדשות מאתר כל-זכות")
    else:
        print("\n⚠️ יש עדיין בעיות שדורשות תיקון")
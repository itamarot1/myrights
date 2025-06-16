#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test enhanced questionnaire - comparing before and after
"""

from gpt_response import filter_matching_rights

def test_income_based_rights():
    """Test that income-based filtering works better"""
    print("🧪 בדיקת זכויות מבוססות הכנסה")
    print("="*50)
    
    # Low income profile
    low_income_profile = {
        'age': '30',
        'gender': 'נקבה',
        'employment_status': 'שכיר',
        'avg_monthly_income': '4000',  # Low income - new parameter!
        'has_children': 'כן',
        'num_children': '2',
        'marital_status': 'גרוש',  # Single parent
        'recognized_disability': 'לא'
    }
    
    # High income profile  
    high_income_profile = {
        'age': '45',
        'gender': 'זכר',
        'employment_status': 'שכיר',
        'avg_monthly_income': '25000',  # High income - new parameter!
        'has_children': 'כן',
        'num_children': '2',
        'marital_status': 'נשוי',
        'recognized_disability': 'לא'
    }
    
    print("פרופיל הכנסה נמוכה (4,000 ש\"ח):")
    low_rights = filter_matching_rights(low_income_profile, min_value_threshold=500)
    for i, right in enumerate(low_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nפרופיל הכנסה גבוהה (25,000 ש\"ח):")
    high_rights = filter_matching_rights(high_income_profile, min_value_threshold=500)
    for i, right in enumerate(high_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nהשוואה:")
    print(f"  הכנסה נמוכה: {len(low_rights)} זכויות")
    print(f"  הכנסה גבוהה: {len(high_rights)} זכויות")
    
    return len(low_rights) > len(high_rights)

def test_disability_percentage_rights():
    """Test disability percentage filtering"""
    print("\n🦽 בדיקת זכויות לפי אחוז נכות")
    print("="*50)
    
    # Mild disability
    mild_disability_profile = {
        'age': '35',
        'gender': 'זכר',
        'employment_status': 'שכיר',
        'recognized_disability': 'כן',
        'disability_percentage': '30',  # Mild - new parameter!
        'avg_monthly_income': '8000'
    }
    
    # Severe disability
    severe_disability_profile = {
        'age': '35',
        'gender': 'זכר',
        'employment_status': 'מובטל',
        'recognized_disability': 'כן',
        'disability_percentage': '75',  # Severe - new parameter!
        'avg_monthly_income': '3000'
    }
    
    print("נכות קלה (30%):")
    mild_rights = filter_matching_rights(mild_disability_profile, min_value_threshold=500)
    for i, right in enumerate(mild_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nנכות קשה (75%):")
    severe_rights = filter_matching_rights(severe_disability_profile, min_value_threshold=500)
    for i, right in enumerate(severe_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nהשוואה:")
    print(f"  נכות קלה: {len(mild_rights)} זכויות")
    print(f"  נכות קשה: {len(severe_rights)} זכויות")
    
    return len(severe_rights) >= len(mild_rights)

def test_military_service_details():
    """Test detailed military service rights"""
    print("\n🎖️ בדיקת זכויות חיילים מפורטות")
    print("="*50)
    
    # Short service
    short_service_profile = {
        'age': '25',
        'gender': 'זכר',
        'employment_status': 'סטודנט',
        'military_or_national_service': 'שירות צבאי (צה\"ל)',
        'service_length_years': '2',  # Short service - new parameter!
        'service_role': 'תומך',
        'injured_in_service': 'לא'
    }
    
    # Long combat service with injury
    long_service_profile = {
        'age': '30',
        'gender': 'זכר',
        'employment_status': 'שכיר',
        'military_or_national_service': 'שירות צבאי (צה\"ל)',
        'service_length_years': '20',  # Career military - new parameter!
        'service_role': 'קרבי',
        'injured_in_service': 'כן'
    }
    
    print("שירות קצר (2 שנים, תומך):")
    short_rights = filter_matching_rights(short_service_profile, min_value_threshold=500)
    for i, right in enumerate(short_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nשירות ארוך (20 שנים, קרבי, נפגע):")
    long_rights = filter_matching_rights(long_service_profile, min_value_threshold=500)
    for i, right in enumerate(long_rights, 1):
        print(f"  {i}. {right['name']}")
    
    print(f"\nהשוואה:")
    print(f"  שירות קצר: {len(short_rights)} זכויות")
    print(f"  שירות ארוך: {len(long_rights)} זכויות")
    
    return len(long_rights) >= len(short_rights)

if __name__ == "__main__":
    print("בדיקת השאלון המשופר")
    print("="*60)
    
    income_test = test_income_based_rights()
    disability_test = test_disability_percentage_rights()
    military_test = test_military_service_details()
    
    print("\n" + "="*60)
    print("תוצאות הבדיקה:")
    print(f"✅ סינון לפי הכנסה: {'עובד כמצופה' if income_test else 'דורש תיקון'}")
    print(f"✅ סינון לפי אחוז נכות: {'עובד כמצופה' if disability_test else 'דורש תיקון'}")
    print(f"✅ סינון לפי פרטי שירות: {'עובד כמצופה' if military_test else 'דורש תיקון'}")
    
    if income_test and disability_test and military_test:
        print("\n🎯 השאלון המשופר עובד מצוין!")
        print("המערכת כעת תופסת זכויות בצורה מדויקת יותר")
    else:
        print("\n⚠️ יש עדיין שיפורים שנדרשים")
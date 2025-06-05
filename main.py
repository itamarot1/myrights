from session_manager import UserSession, extract_unclaimed_value
import re

def main():
    session = UserSession()

    # שלב 1 – איסוף פרופיל מלא
    while not session.is_profile_complete():
        for key in session.profile:
            if session.profile[key] is None:
                user_input = input(f"הזן ערך עבור '{key}': ")
                session.update_profile(key, user_input)

    # שלב 2 – הרצת GPT-3.5 לבירור
    print("\nGPT (שלב 1 - בירור):\n")
    basic_response = session.ask_for_clarifications()
    print(basic_response)

    # שלב 3 – המשתמש עונה על שאלות ההבהרה
    print("\nכעת ענה בקצרה על השאלות שנשאלת:")
    clarifications = []
    for line in basic_response.split("\n"):
        if re.match(r"^\d+\.\s", line.strip()):
            answer = input(line.strip() + " ")
            clarifications.append(f"{line.strip()} {answer}")

    # שלב 4 – דו״ח זכויות סופי
    continue_input = input("\nהאם לעבור לניתוח סופי? (כן/לא): ")
    if continue_input.strip().lower() == "כן":
        print("\nGPT (שלב 2 - דוח זכויות סופי):\n")
        final_response = session.generate_final_report(clarifications)
        print(final_response)

        # שלב 5 – סכום כולל של זכויות לא מומשות
        if final_response.strip():
            estimated_value = extract_unclaimed_value(final_response)
            if estimated_value > 0:
                print(f"\n💰 נראה שלא מימשת זכויות בשווי כולל של כ־{estimated_value:,} ₪. ממליץ מאוד לטפל בזה השבוע.")
            else:
                print("\n✅ נראה שמימשת את מרבית הזכויות שלך. כל הכבוד!")
        else:
            print("\n⚠️ לא התקבלה תגובה מ-GPT.")

if __name__ == "__main__":
    main()

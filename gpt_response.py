import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_basic_rights_response(profile: dict) -> str:
    return "נמשיך לשאול מספר שאלות כדי שנוכל לבדוק את הזכויות שמגיעות לך."

def get_detailed_rights_report(profile: dict, clarifications: list) -> str:
    clarifications_text = "\n".join(clarifications)

    prompt = f"""
אתה יועץ אישי לזכויות בישראל. אל תשתמש בניסוח ממשלתי, אל תצטט טפסים — תדבר בגובה העיניים, כאילו אתה חבר טוב שמבין בתחום.

מטרתך:
1. להסביר לאדם הזה (על סמך הפרופיל והבהרותיו) אילו זכויות מגיעות לו.
2. עבור כל זכות – פרט:
   - מה היא
   - למה מגיעה לו ספציפית
   - כמה שווה בחודש
3. אם יש זכויות נוספות קטנות – אפשר לקבץ אותן.
4. בסיום, סכום את כלל הזכויות הלא ממומשות (ב₪ לחודש).
5. כתוב משפט ברור שמעודד אותו להשאיר פרטים כדי שנוכל לעזור.

סגנון כתיבה:
- אנושי, בגובה העיניים, לא פורמלי מדי
- מעודד, אך כן וישיר
- בלי "ייתכן", בלי טפסים, בלי סעיפים חוקיים
- בלי להגיד לו לפנות לביטוח לאומי או לאתרים אחרים שהם לא אנחנו
- בלי להגיד אחרי כל זכות שנמצאה ״כדאי לך לבדוק את זכאותך לקצבה זו״ או משהו כזה
- לא להגיד ללקוח שעליו להגיש בקשה לביטוח לאומי !

פורמט הדוח:
1. פסקת פתיחה אישית (לפי גיל, מצב אישי וכו')
2. רשימה ממוספרת של זכויות — כל אחת בפסקה חדשה עם ירידת שורה בין הזכויות:
   - שם הזכות
   - הסבר קצר למה היא רלוונטית אליו
   - שווי חודשי משוער
3. שורת סיכום עם הסכום הכולל (ב₪)
4. פסקת סיום שמניעה אותו להשאיר פרטים, בטון רך וברור

הנתונים:
- גיל: {profile.get('age')}
- מצב תעסוקתי: {profile.get('employment_status')}
- נכות: {profile.get('disability')}
- שירות צבאי: {profile.get('military_service')}
- מצב משפחתי: {profile.get('marital_status')}

{clarifications_text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

def generate_dynamic_questions(profile: dict) -> list:
    questions = []

    age = profile.get("age")
    employment = profile.get("employment_status")
    disability = profile.get("disability")
    military_service = profile.get("military_service")
    marital_status = profile.get("marital_status")

    if not age:
        questions.append("מה גילך?")
    if age and int(age) >= 18 and not military_service:
        questions.append("האם שירתת בצבא?")
    if not employment:
        questions.append("האם אתה עובד כרגע? אם כן, במה?")
    if not disability:
        questions.append("האם יש לך נכות כלשהי? אם כן, באיזה אחוז?")
    if not marital_status:
        questions.append("מה מצבך המשפחתי?")

    return questions

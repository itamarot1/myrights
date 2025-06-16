from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gpt_response import (
    get_basic_rights_response,
    get_detailed_rights_report,
)
from adaptive_questionnaire import get_relevant_questions, estimate_completion_percentage

app = Flask(__name__, static_url_path="/static", static_folder="static")
CORS(app)

@app.route("/")
def serve_index():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        profile = data.get("profile", {})
        clarifications = data.get("clarifications", [])

        print(">>> chat הופעלה!")
        print(">>> פרופיל שהתקבל:", profile)
        print(">>> מספר שדות בפרופיל:", len([k for k, v in profile.items() if str(v).strip()]))

        if not profile or all(str(v).strip() == "" for v in profile.values()):
            return jsonify({"reply": "שלום! אני כאן לעזור לך למצוא את כל הזכויות שמגיעות לך.\nבואו נתחיל עם השאלה הראשונה: מה גילך?", "field": "age", "done": False, "type": "number", "progress": 0})

        # Use adaptive questionnaire
        next_questions = get_relevant_questions(profile)
        completion = estimate_completion_percentage(profile)
        
        print(f">>> שאלות שנותרו: {len(next_questions)}")
        print(f">>> אחוז השלמה: {completion:.0f}%")
        
        if next_questions:
            q = next_questions[0]
            print(f">>> שאלה הבאה: {q['key']} - {q['question'][:50]}...")
            
            response = {
                "reply": q['question'], 
                "field": q["key"], 
                "done": False,
                "type": q.get("type", "text"),
                "options": q.get("options", []),
                "progress": completion
            }
            return jsonify(response)

        print(">>> גונר דוח GPT - כל השאלות נענו!")
        try:
            report = get_detailed_rights_report(profile, clarifications)
            print(f">>> דוח נוצר בהצלחה ({len(report)} תווים)")
        except Exception as e:
            print(f">>> שגיאה ביצירת דוח GPT: {e}")
            return jsonify({"reply": f"שגיאה ביצירת הדוח: {str(e)}", "done": "error"})
    
        keywords = ["קצבה", "פטור", "הנחה", "מענק", "סיוע", "מלגה", "שירותים מיוחדים", "תמיכה"]
        if any(word in report for word in keywords):
            return jsonify({"reply": report, "done": True})
        else:
            return jsonify({
                "reply": "נכון לעכשיו לא מצאתי זכויות שעשויות להיות רלוונטיות לפי הנתונים שסיפקת.",
                "done": "no-rights"
            })
    
    except Exception as e:
        print(f">>> שגיאה כללית בצ'אט: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"שגיאה: {str(e)}", "done": "error"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=True)
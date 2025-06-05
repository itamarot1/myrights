from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gpt_response import get_basic_rights_response, get_detailed_rights_report, generate_dynamic_questions

app = Flask(__name__, static_url_path="/static", static_folder="static")
CORS(app)

@app.route("/")
def serve_index():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    profile = data.get("profile", {})
    clarifications = data.get("clarifications", [])

    print(">>> chat הופעלה!")
    print(">>> פרופיל שהתקבל:", profile)

    if not profile or all(str(v).strip() == "" for v in profile.values()):
        return jsonify({"reply": "שלום! נתחיל מהשאלה הראשונה: מה גילך?", "done": False})

    questions = generate_dynamic_questions(profile)
    if questions:
        return jsonify({"reply": questions[0], "done": False})

    report = get_detailed_rights_report(profile, clarifications)
    keywords = ["קצבה", "פטור", "הנחה", "מענק", "סיוע", "מלגה", "שירותים מיוחדים", "תמיכה"]
    if any(word in report for word in keywords):
        return jsonify({"reply": report, "done": True})
    else:
        return jsonify({
            "reply": "נכון לעכשיו לא מצאתי זכויות שעשויות להיות רלוונטיות לפי הנתונים שסיפקת.",
            "done": "no-rights"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

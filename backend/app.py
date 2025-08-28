from flask import Flask, request, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
import re

app = Flask(__name__)
CORS(app)  # Allow React frontend to access this backend

# Symptom keywords mapping with base medication suggestions
symptoms_responses = {
    "headache": {
        "general": "For a headache, you can take **paracetamol** and rest.",
        "male": "For males, **ibuprofen** or **paracetamol** is usually effective.",
        "female": "For females, **paracetamol** is safer (avoid ibuprofen if pregnant)."
    },
    "fever": {
        "general": "For a fever, stay hydrated and take **paracetamol** if needed.",
        "male": "Males can take **paracetamol** or **ibuprofen** (if no stomach issues).",
        "female": "Females should prefer **paracetamol** as it’s gentler."
    },
    "cold": {
        "general": "For a common cold, drink fluids, rest, and try **loratadine** if needed.",
        "male": "Males can use **loratadine** or steam inhalation.",
        "female": "Females can use **loratadine** (avoid strong meds in pregnancy)."
    },
    "cough": {
        "general": "For a cough, honey, warm drinks, and **dextromethorphan syrup** can help.",
        "male": "Males can try **dextromethorphan syrup** or ginger tea.",
        "female": "Females can try honey, warm water, and mild cough syrups."
    },
    "stomach": {
        "general": "For stomach pain, eat light food, avoid spicy meals, and take **ORS**.",
        "male": "Males can try **ORS** and light food.",
        "female": "Females can try **ORS**, warm water, and rest."
    },
    "back": {
        "general": "For back pain, gentle stretching, rest, and **acetaminophen** may help.",
        "male": "Males may use **ibuprofen** if needed.",
        "female": "Females should prefer **paracetamol**."
    },
    "allergy": {
        "general": "For mild allergies, take **loratadine** or **cetirizine**.",
        "male": "Males can take **cetirizine** at night.",
        "female": "Females should prefer **loratadine** (less drowsy)."
    },
    "fatigue": {
        "general": "Fatigue may improve with rest, hydration, and balanced meals.",
        "male": "Males may need more hydration and iron-rich foods.",
        "female": "Females may need iron-rich foods (especially during menstruation)."
    },
    "throat": {
        "general": "For a sore throat, gargle with salt water and use lozenges.",
        "male": "Males can try warm ginger tea.",
        "female": "Females can try warm honey-lemon water."
    }
}


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        message = data.get("message", "")
        gender = data.get("gender", "").lower()
        age = data.get("age", "")
        language = data.get("language", "en-US")

        # Convert age to integer safely
        try:
            age = int(age)
        except:
            age = None

        message_lower = message.lower()
        replies = []

        for keyword, response_set in symptoms_responses.items():
            if re.search(r"\b" + re.escape(keyword) + r"\b", message_lower):
                reply_text = response_set.get("general", "")

                # Gender specific
                if gender == "male" and "male" in response_set:
                    reply_text = response_set["male"]
                elif gender == "female" and "female" in response_set:
                    reply_text = response_set["female"]

                # Age specific rules
                if age is not None:
                    if age < 12:
                        reply_text = f"For children under 12, avoid strong medicines. Use mild remedies only. {reply_text}"
                    elif age > 60:
                        reply_text = f"For elderly patients, use medicines cautiously and consult a doctor. {reply_text}"

                replies.append(reply_text)

        if replies:
            reply_en = " ".join(replies)
        else:
            reply_en = "I’m not sure. Please consult a doctor for proper advice."

        # Translate if needed
        lang_code = language.split("-")[0]
        if lang_code != "en":
            try:
                reply = GoogleTranslator(source="en", target=lang_code).translate(reply_en)
            except Exception as e:
                print("Translation error:", e)
                reply = reply_en
        else:
            reply = reply_en

        print(f"Message: {message} | Gender: {gender} | Age: {age} | Reply: {reply}")
        return jsonify({"reply": reply})

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({"reply": "Sorry, the assistant is currently unavailable. Please try again later."})


if __name__ == "__main__":
    app.run(debug=True)

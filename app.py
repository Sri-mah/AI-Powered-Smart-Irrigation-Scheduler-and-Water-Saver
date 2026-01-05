from flask import Flask, render_template, request
from datetime import date
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Global variables
water_credit = 50
last_date = date.today()
history = []
moisture_history = []

def get_badge(score):
    if score < 50:
        return "Beginner 🟢"
    elif 50 <= score < 80:
        return "Water Saver 💧"
    else:
        return "Eco Smart Farmer 🌱"

@app.route("/", methods=["GET", "POST"])
def home():
    global water_credit, last_date, history, moisture_history
    today = date.today()

    # Daily reset
    if today != last_date:
        water_credit = 50
        history.clear()
        moisture_history.clear()
        last_date = today

    result = ""
    status = ""
    water = ""
    save = ""
    prediction = ""
    badge = get_badge(water_credit)

    if request.method == "POST":
        moisture = int(request.form["moisture"])
        threshold = int(request.form["threshold"])

        # Add current reading to history
        moisture_history.append(moisture)

        # AI Moisture Prediction (Linear Regression)
        if len(moisture_history) >= 3:
            X = np.array(range(len(moisture_history))).reshape(-1, 1)
            y = np.array(moisture_history)
            model = LinearRegression()
            model.fit(X, y)
            predicted_next = int(model.predict([[len(moisture_history)]]))
        else:
            predicted_next = moisture
        prediction = f" AI Predicted Next Moisture: {predicted_next}%"

        # Pump ON/OFF Logic
        if moisture < threshold:
            result = "🚰 Pump ON"
            status = "on"
            water = "Soil dry – irrigation started"
            save = "💧 10% Water Saved"
            water_credit += 5
        else:
            result = "✅ Pump OFF"
            status = "off"
            water = "Soil has enough moisture"
            save = "💡 100% Water Saved"
            water_credit += 10

        history.append(water_credit)
        badge = get_badge(water_credit)

    return render_template(
        "index.html",
        result=result,
        status=status,
        water=water,
        save=save,
        water_credit=water_credit,
        history=history,
        prediction=prediction,
        badge=badge,
        moisture=moisture_history[-1] if moisture_history else 40,
        threshold=request.form["threshold"] if request.method=="POST" else 40
    )

if __name__ == "__main__":
    app.run(debug=True)
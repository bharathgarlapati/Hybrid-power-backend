from flask import Flask, render_template, jsonify, request, send_file
import firebase_admin
from firebase_admin import credentials, db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime

app = Flask(__name__)

# ================= FIREBASE INITIALIZATION =================
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://cloud-energy-system-default-rtdb.firebaseio.com/"
})

# ================= DASHBOARD PAGE =================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ================= ESP DATA UPLOAD =================
@app.route("/api/upload", methods=["POST"])
def upload_data():
    data = request.json

    # Add timestamp
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store ESP data as history
    ref = db.reference("controllers/hybrid_controller_01/records")
    ref.push(data)

    return jsonify({"status": "ESP data stored"}), 200

# ================= GET LATEST LIVE DATA =================
@app.route("/api/live")
def live_data():
    ref = db.reference("controllers/hybrid_controller_01/records")
    latest = ref.order_by_key().limit_to_last(1).get()

    # If ESP data exists, use it
    if latest:
        record = list(latest.values())[0]
    else:
        # Fallback to sample data
        record = db.reference(
            "controllers/hybrid_controller_01/record_1"
        ).get()

    if not record:
        return jsonify({"error": "No data found"})

    return jsonify({
        "sv": record.get("sv"),
        "si": record.get("si"),
        "sp": record.get("sp"),
        "bt": record.get("bt"),
        "fan": record.get("fan"),
        "wv": record.get("wv"),
        "wi": record.get("wi"),
        "wp": record.get("wp"),
        "timestamp": record.get("timestamp")
    })

# ================= DOWNLOAD PDF (LATEST DATA) =================
@app.route("/download/pdf")
def download_pdf():
    ref = db.reference("controllers/hybrid_controller_01/records")
    latest = ref.order_by_key().limit_to_last(1).get()

    if latest:
        record = list(latest.values())[0]
    else:
        record = db.reference(
            "controllers/hybrid_controller_01/record_1"
        ).get()

    if not record:
        return "No data available to generate PDF", 400

    file_name = "Hybrid_Energy_Report.pdf"
    pdf = SimpleDocTemplate(file_name, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [Paragraph("Hybrid Energy System Report", styles["Title"])]

    table_data = [["Parameter", "Value"]]
    for key, value in record.items():
        table_data.append([key.upper(), str(value)])

    content.append(Table(table_data))
    pdf.build(content)

    return send_file(file_name, as_attachment=True)

# ================= RUN SERVER ===============  
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

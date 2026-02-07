from flask import Flask, render_template, jsonify, request, send_file
import firebase_admin
from firebase_admin import credentials, db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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

# ================= GET SAMPLE DATA FOR DASHBOARD =================
@app.route("/api/live")
def live_data():
    ref = db.reference("controllers/hybrid_controller_01/record_1")
    record = ref.get()

    if not record:
        return jsonify({"error": "No sample data found"})

    return jsonify({
        "sv": record.get("sv"),
        "si": record.get("si"),
        "sp": record.get("sp"),
        "bt": record.get("bt"),
        "fan": record.get("fan"),
        "wv": record.get("wv"),
        "wi": record.get("wi"),
        "wp": record.get("wp")
    })

# ================= DOWNLOAD PDF (FROM SAMPLE DATA) =================
@app.route("/download/pdf")
def download_pdf():
    ref = db.reference("controllers/hybrid_controller_01/record_1")
    record = ref.get()

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

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


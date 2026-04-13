import io, os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from utils import analyze_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
CORS(app)
app.secret_key = "dqc_secret_key_2024"

# --- FOLDER & DATABASE PATHS (Cloud Compatible) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- USER MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

# --- FRONTEND ROUTES ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# --- AUTH ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get("username"), data.get("password")
    if User.query.filter_by(username=u).first():
        return jsonify({"message": "Username taken"}), 400
    user = User(username=u, password=p)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Success"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username"), password=data.get("password")).first()
    if user:
        return jsonify({"message": "ok"})
    return jsonify({"message": "Invalid credentials"}), 401

# --- DATA ANALYSIS ROUTE ---
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save file temporarily for processing
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    
    try:
        # Calls the detailed function in utils.py
        result = analyze_file(path)
        result['filename'] = file.filename 
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the file after analysis to save space
        if os.path.exists(path):
            os.remove(path)

# --- PDF REPORT ROUTE ---
@app.route('/report', methods=['POST'])
def report():
    data = request.json
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Building the PDF content
    content = [
        Paragraph(f"<b>Data Quality Intelligence Report</b>", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"<b>Target File:</b> {data.get('filename', 'Unknown')}", styles['Normal']),
        Paragraph(f"<b>Total Rows:</b> {data.get('rows')}", styles['Normal']),
        Paragraph(f"<b>Total Columns:</b> {data.get('cols')}", styles['Normal']),
        Paragraph(f"<b>Detected Errors:</b> {data.get('errors')}", styles['Normal']),
        Paragraph(f"<b>Overall Quality Score:</b> {data.get('quality')}%", styles['Normal']),
        Spacer(1, 12),
        Paragraph("<b>Detailed Inspection Log:</b>", styles['Heading3']),
        Spacer(1, 6)
    ]
    
    # Adding the list of errors to the PDF
    for err in data.get("error_list", []):
        content.append(Paragraph(f"• {err}", styles['Normal']))
    
    if not data.get("error_list"):
        content.append(Paragraph("No errors detected. Data is clean.", styles['Normal']))

    doc.build(content)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="DQC_Pro_Report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
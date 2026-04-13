import io, os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from models import db, User
from utils import analyze_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
CORS(app)

# --- FOLDER SETUP ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DATABASE SETUP ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# --- FRONTEND ROUTES ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# --- API ROUTES ---
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
    return jsonify({"message": "ok"}) if user else (jsonify({"message": "Invalid"}), 401)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    
    try:
        result = analyze_file(path)
        result['filename'] = file.filename 
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [
        Paragraph(f"<b>Data Analysis: {data.get('filename', 'Report')}</b>", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Rows: {data.get('rows')}", styles['Normal']),
        Paragraph(f"Errors: {data.get('errors')}", styles['Normal']),
        Paragraph(f"Score: {data.get('quality')}%", styles['Normal']),
        Spacer(1, 12),
        Paragraph("<b>Error Log:</b>", styles['Heading3'])
    ]
    for err in data.get("error_list", [])[:200]:
        content.append(Paragraph(f"• {err}", styles['Normal']))
    doc.build(content)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
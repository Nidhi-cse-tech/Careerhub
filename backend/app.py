from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resources.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Models
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(200), nullable=False)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    res_id = db.Column(db.Integer, db.ForeignKey("resource.id"), nullable=False)

# Seed initial data
def seed_data():
    if Resource.query.first() is None:  # Only seed if empty
        resources = [
            {"title": "DSA Roadmap", "category": "DSA & Coding", "tags": "DSA", "url": "https://example.com/dsa"},
            {"title": "Python Basics", "category": "Programming", "tags": "Python", "url": "https://example.com/python"},
            {"title": "Flask Tutorial", "category": "Web Development", "tags": "Flask", "url": "https://example.com/flask"},
            {"title": "SQL Basics", "category": "Databases", "tags": "SQL", "url": "https://example.com/sql"},
            {"title": "Frontend Roadmap", "category": "Web Development", "tags": "HTML,CSS,JS", "url": "https://example.com/frontend"},
        ]
        for r in resources:
            db.session.add(Resource(**r))
        db.session.commit()

# Helper to convert SQLAlchemy objects to dict
def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

# Routes
@app.route("/")
def home():
    return "Backend is running! Go to /api/resources to see the data."

@app.route("/api/resources")
def get_resources():
    category = request.args.get("category")
    tag = request.args.get("tag")
    username = request.args.get("user")  # optional

    query = Resource.query
    if category:
        query = query.filter_by(category=category)
    if tag:
        query = query.filter(Resource.tags.contains(tag))

    resources = query.all()

    result = []
    for r in resources:
        r_dict = to_dict(r)
        if username:
            r_dict["completed"] = UserProgress.query.filter_by(username=username, res_id=r.id).first() is not None
        else:
            r_dict["completed"] = False
        result.append(r_dict)

    return jsonify(result)

@app.route("/api/complete/<username>/<int:res_id>", methods=["POST"])
def mark_completed(username, res_id):
    if UserProgress.query.filter_by(username=username, res_id=res_id).first() is None:
        progress = UserProgress(username=username, res_id=res_id)
        db.session.add(progress)
        db.session.commit()
    return jsonify({"message": f"Marked complete for {username}"})

# Initialize DB and seed data
with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)







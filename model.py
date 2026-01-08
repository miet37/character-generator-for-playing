from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    przedmiot = db.Column(db.String(200))
    przedmiot_id = db.Column(db.String(100))
    imie = db.Column(db.String(100))
    nazwisko = db.Column(db.String(100))
    numer_albumu = db.Column(db.String(50))
    uwagi = db.Column(db.Text)
    attdate = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.now())

def upload_students_csv(filepath):
    """Stub function for CSV upload"""
    pass

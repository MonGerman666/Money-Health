# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    text_tiquet = db.Column(db.Text, nullable=True)
    imatge = db.Column(db.String(120), nullable=True)
    # Aquí es podria afegir una relació amb els expenses

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'))
    nom_producte = db.Column(db.String(120), nullable=False)
    preu = db.Column(db.Float, nullable=False)
    quantitat = db.Column(db.Float, nullable=True, default=1)
    categoria = db.Column(db.String(80), nullable=True)
    
class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # Pot ser un text format JSON o similar
    calories = db.Column(db.Integer, nullable=True)
    proteines = db.Column(db.Float, nullable=True)
    carbohidrats = db.Column(db.Float, nullable=True)
    greixos = db.Column(db.Float, nullable=True)

# Model bàsic per un pla de dieta (opcional)
class DietPlan(db.Model):
    __tablename__ = 'diet_plan'
    id = db.Column(db.Integer, primary_key=True)
    data_setmana = db.Column(db.Date, nullable=False)
    # Per simplificar, emmagatzemem els IDs de receptes separats per comes
    recepta_ids = db.Column(db.String(250), nullable=True)

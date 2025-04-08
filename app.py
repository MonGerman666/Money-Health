from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime

from models import db, Receipt, Expense, Recipe, DietPlan
from ocr import processar_tiquet, extract_items_from_image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_tiquet', methods=['POST'])
def upload_tiquet():
    if 'imatge' not in request.files:
        return jsonify({'error': 'No s\'ha proporcionat cap imatge'}), 400
    file = request.files['imatge']
    if file.filename == '':
        return jsonify({'error': 'No s\'ha seleccionat cap fitxer'}), 400

    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)

    # Text sencer (pot ser útil per revisió)
    text = processar_tiquet(file_path)
    # Items detectats
    expenses_list = extract_items_from_image(file_path)

    total = sum(item['preu'] for item in expenses_list) if expenses_list else 0.0
    data_actual = datetime.today().date()

    receipt = Receipt(data=data_actual, total=total, text_tiquet=text, imatge=filename)
    db.session.add(receipt)
    db.session.commit()

    for exp in expenses_list:
        expense = Expense(receipt_id=receipt.id,
                          nom_producte=exp['nom_producte'],
                          preu=exp['preu'])
        db.session.add(expense)
    db.session.commit()

    return jsonify({
        'message': 'Tiquet processat correctament',
        'receipt_id': receipt.id,
        'text_tiquet': text,
        'items': expenses_list
    })

# Exemple d'endpoints de receptes i pla de dieta (sense canvis)
@app.route('/api/recipe', methods=['POST'])
def add_recipe():
    data = request.get_json()
    nom = data.get('nom')
    ingredients = data.get('ingredients')
    calories = data.get('calories')
    proteines = data.get('proteines')
    carbohidrats = data.get('carbohidrats')
    greixos = data.get('greixos')

    recipe = Recipe(nom=nom, ingredients=ingredients, calories=calories,
                    proteines=proteines, carbohidrats=carbohidrats, greixos=greixos)
    db.session.add(recipe)
    db.session.commit()
    return jsonify({'message': 'Recepta afegida', 'recipe_id': recipe.id})

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    result = []
    for r in recipes:
        result.append({
            'id': r.id,
            'nom': r.nom,
            'ingredients': r.ingredients,
            'calories': r.calories,
            'proteines': r.proteines,
            'carbohidrats': r.carbohidrats,
            'greixos': r.greixos
        })
    return jsonify(result)

@app.route('/api/diet_plan', methods=['POST'])
def add_diet_plan():
    data = request.get_json()
    data_setmana = data.get('data_setmana')
    recepta_ids = data.get('recepta_ids')
    recepta_ids_str = ",".join(map(str, recepta_ids))

    diet_plan = DietPlan(
        data_setmana=datetime.strptime(data_setmana, "%Y-%m-%d").date(),
        recepta_ids=recepta_ids_str
    )
    db.session.add(diet_plan)
    db.session.commit()

    return jsonify({'message': 'Pla de dieta creat', 'diet_plan_id': diet_plan.id})

if __name__ == '__main__':
    app.run(debug=True)

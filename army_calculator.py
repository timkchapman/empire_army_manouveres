import os
import configparser
from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from forms.forces import ForcesForm
from forms.fortifications import FortificationsForm

basedir = os.path.abspath(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read('configuration.ini')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'empire_army_manouveres.db')
app.config['SECRET_KEY'] = config['FLASK']['SECRET_KEY']

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

class Force(db.Model):
    force_id = db.Column(db.Integer, primary_key=True, index=True)
    force_name = db.Column(db.String(80), unique=True, nullable=False)
    force_is_army = db.Column(db.Boolean, nullable=False)
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.nation_id'), nullable=False)
    quality_id = db.Column(db.Integer, db.ForeignKey('quality.quality_id'), nullable=False)
    large = db.Column(db.Boolean, nullable=False)

    nation = db.relationship('Nation', lazy='joined')
    quality = db.relationship('Quality', lazy='joined')

    def __repr__(self):
        return '<Force %r>' % self.force_name
    
class Fortification(db.Model):
    fortification_id = db.Column(db.Integer, primary_key=True, index=True)
    fortification_name = db.Column(db.String(80), unique=True, nullable=False)
    fortification_level = db.Column(db.Integer, nullable=False)
    fortification_maximum_strength = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Fortification %r>' % self.fortification_name
    
class Nation(db.Model):
    nation_id = db.Column(db.Integer, primary_key=True, index=True)
    nation_name = db.Column(db.String(80), unique=True, nullable=False)
    nation_faction = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Nation %r>' % self.nation_name
    
quality_order_association = db.Table('quality_order',
    db.Column('quality_id', db.Integer, db.ForeignKey('quality.quality_id'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.order_id'), primary_key=True)
)

class Quality(db.Model):
    quality_id = db.Column(db.Integer, primary_key=True, index=True)
    quality_name = db.Column(db.String(80), unique=True, nullable=False)
    quality_effects = db.Column(db.Text, nullable=False)
    quality_descriptors = db.Column(db.Text, nullable=False)
    quality_description = db.Column(db.Text, nullable=False)
    quality_orders = db.relationship('Order', secondary=quality_order_association,  lazy='subquery',
                             backref=db.backref('qualities', lazy=True))

    def __repr__(self):
        return '<Quality %r>' % self.quality_name
    
    def effects_as_list(self):
        return self.quality_effects.split('. ')

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, index=True)
    order_name = db.Column(db.String(80), unique=True, nullable=False)
    offensive_order = db.Column(db.Boolean, nullable=False)
    order_effects = db.Column(db.Text, nullable=False)
    order_description = db.Column(db.Text(80), nullable=False)
    casualties_inflicted_modifier = db.Column(db.Float, nullable=False)
    casualties_suffered_modifier = db.Column(db.Float, nullable=False)
    territory_claimed_modifier = db.Column(db.Float, nullable=False)
    territory_defence_modifier = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Order %r>' % self.order_name
    
    def effects_as_list(self):
        return self.order_effects.split('. ')

class Force_Ritual(db.Model):
    force_ritual_id = db.Column(db.Integer, primary_key=True, index=True)
    force_ritual_name = db.Column(db.String(80), unique=True, nullable=False)
    army_ritual = db.Column(db.Boolean, nullable=False)
    force_ritual_effects = db.Column(db.Text, nullable=False)
    force_ritual_quality_id = db.Column(db.Integer, db.ForeignKey('quality.quality_id'), nullable=True)
    force_effective_strength_modifier = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Force_Ritual %r>' % self.force_ritual_name

class Fortification_Ritual(db.Model):
    fortification_ritual_id = db.Column(db.Integer, primary_key=True, index=True)
    fortification_ritual_name = db.Column(db.String(80), unique=True, nullable=False)
    fortification_ritual_effects = db.Column(db.Text, nullable=False)
    fortification_effective_strength_modifier = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Fortification_Ritual %r>' % self.fortification_ritual_name

class Territory_Ritual(db.Model):
    territory_ritual_id = db.Column(db.Integer, primary_key=True, index=True)
    territory_ritual_name = db.Column(db.String(80), unique=True, nullable=False)
    territory_ritual_effects = db.Column(db.Text, nullable=False)
    territory_ritual_casualties = db.Column(db.Integer, nullable=False)
    territory_ritual_modifier = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Territory_Ritual %r>' % self.territory_ritual_name

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    imperial_forces = [(force.force_id, force.force_name) for force in Force.query.join(Nation).filter(Nation.nation_faction == 'The Empire').all()]
    barbarian_forces = [(force.force_id, force.force_name) for force in Force.query.join(Nation).filter(Nation.nation_faction == 'Barbarian').all()]
    imperial_forces.insert(0, ('', 'Select Force'))
    barbarian_forces.insert(0, ('', 'Select Force'))
    rituals = []
    rituals.insert(0, ('', 'Select Ritual'))
    orders = []
    orders.insert(0, ('', 'Select Order'))
    strength = 0

    imperial_form = ForcesForm()
    barbarian_form = ForcesForm()
    imperial_form.force.choices = imperial_forces
    barbarian_form.force.choices = barbarian_forces
    imperial_form.order.choices = orders
    barbarian_form.order.choices = orders
    imperial_form.ritual.choices = rituals
    barbarian_form.ritual.choices = rituals
    imperial_form.strength.data = strength
    barbarian_form.strength.data = strength

    return render_template('index.html', imperial_form=imperial_form, barbarian_form=barbarian_form)

@app.route('/get_force_options', methods=['POST'])
def get_force_options():
    role = request.form['role']

    if role == 'imperial':
        forces = [(force.force_id, force.force_name) for force in Force.query.join(Nation).filter(Nation.nation_faction == 'The Empire').all()]
    elif role == 'barbarian':
        forces = [(force.force_id, force.force_name) for force in Force.query.join(Nation).filter(Nation.nation_faction == 'Barbarian').all()]
    else:
        forces = []

    return jsonify({'forces': forces})

@app.route('/get_force_info', methods=['POST'])
def get_force_info():
    force_id = request.form['force_id']
    force = Force.query.get(force_id)
    if force:
        return jsonify({
            'large': force.large
        })
    return jsonify({'error': 'Force not found'}), 404

from flask import Flask, request, jsonify

@app.route('/get_rituals_by_force', methods=['POST'])
def get_rituals_by_force():
    rituals = Force_Ritual.query.filter_by(army_ritual=True).all()
    ritual_list = [(ritual.force_ritual_id, ritual.force_ritual_name) for ritual in rituals]

    return jsonify({'rituals': ritual_list})

@app.route('/get_orders_by_force', methods=['POST'])
def get_orders_by_force():
    force_id = request.form.get('force_id')
    if not force_id:
        return jsonify({'orders': []})
    
    force = Force.query.get(force_id)
    if not force:
        return jsonify({'orders': []})
    
    quality = force.quality
    if not quality:
        return jsonify({'orders': []})
    
    orders = Order.query.filter(Order.order_id.between(1, 8)).all()
    order_list = [(order.order_id, order.order_name, order.offensive_order) for order in orders]

    if force.nation_id == 7:
        national_orders = Order.query.filter(Order.order_id == 40).first()
        if national_orders:
            order_list.append((national_orders.order_id, national_orders.order_name, national_orders.offensive_order))
        order_list = [order for order in order_list if order[0] != 5]

    additional_order_list = [(order.order_id, order.order_name, order.offensive_order) for order in quality.quality_orders]
    order_list.extend(additional_order_list)

    order_list = sorted(order_list, key=lambda x: (not x[2], x[0]))
    order_list = [(order[0], order[1]) for order in order_list]

    return jsonify({'orders': order_list})

@app.route('/get_fortification_options', methods=['POST'])
def get_fortification_options():
    role = request.form['role']

    if role == 'imperial':
        fortifications = [(fortification.fortification_id, fortification.fortification_name) for fortification in Fortification.query.filter(Fortification.fortification_id >= 6, Fortification.fortification_id < 34).all()]
    elif role == 'barbarian':
        fortifications = [(fortification.fortification_id, fortification.fortification_name) for fortification in Fortification.query.filter(Fortification.fortification_id > 0, Fortification.fortification_id < 6).all()]
    else:
        fortifications = []

    return jsonify({'fortifications': fortifications})

@app.route('/get_fortification_info', methods=['POST'])
def get_fortification_info():
    fortification_id = request.form['fortification_id']
    fortification = Fortification.query.get(fortification_id)
    if fortification:
        return jsonify({
            'strength': fortification.fortification_maximum_strength
        })
    return jsonify({'error': 'Fortification not found'}), 404

@app.route('/get_rituals_by_fortification', methods=['POST'])
def get_rituals_by_fortification():
    fortification_rituals = Fortification_Ritual.query.filter(Fortification_Ritual.fortification_ritual_id > 0).all()
    fortification_ritual_list = [(ritual.fortification_ritual_id, ritual.fortification_ritual_name) for ritual in fortification_rituals]

    return jsonify({'rituals': fortification_ritual_list})

@app.route('/calculate_outcome', methods=['POST'])
def calculate_outcome():
    data = request.json
    
    # Initialize variables to store total strengths for forces and fortifications
    total_imperial_force_casualties_inflicted = 0
    total_imperial_force_victory_contribution = 0
    total_imperial_force_offensive_victory_contribution = 0
    total_imperial_force_defensive_victory_contribution = 0
    total_imperial_fortification_casualties_inflicted = 0
    total_imperial_fortification_victory_contribution = 0
    total_barbarian_force_casualties_inflicted = 0
    total_barbarian_force_victory_contribution = 0
    total_barbarian_force_offensive_victory_contribution = 0
    total_barbarian_force_defensive_victory_contribution = 0
    total_barbarian_fortification_casualties_inflicted = 0
    total_barbarian_fortification_victory_contribution = 0
    
    # Calculate total imperial force victory contribution and casualties inflicted
    for imperial_force_data in data['imperial_forces']:
        casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution = calculate_force_strength(imperial_force_data)
        total_imperial_force_casualties_inflicted += int(casualties_inflicted)
        total_imperial_force_offensive_victory_contribution += int(offensive_victory_contribution)
        total_imperial_force_defensive_victory_contribution += int(defensive_victory_contribution)
        total_imperial_force_victory_contribution += int(offensive_victory_contribution) + int(defensive_victory_contribution)

    # Calculate total imperial fortification victory contribution and casualties inflicted
    for imperial_fort_data in data['imperial_fortifications']:
        imperial_fortification_casualties_inflicted, imperial_fortification_victory_contribution = calculate_fortification_strength(imperial_fort_data)
        total_imperial_fortification_victory_contribution += int(imperial_fortification_victory_contribution)
        total_imperial_fortification_casualties_inflicted += int(imperial_fortification_casualties_inflicted)

    # Calculate total barbarian force victory contribution and casualties inflicted
    for barbarian_force_data in data['barbarian_forces']:
        casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution = calculate_force_strength(barbarian_force_data)
        total_barbarian_force_casualties_inflicted += int(casualties_inflicted)
        total_barbarian_force_offensive_victory_contribution += int(offensive_victory_contribution)
        total_barbarian_force_defensive_victory_contribution += int(defensive_victory_contribution)
        total_barbarian_force_victory_contribution += int(offensive_victory_contribution) + int(defensive_victory_contribution)

    # Calculate total barbarian fortification victory contribution and casualties inflicted
    for barbarian_fort_data in data['barbarian_fortifications']:
        barbarian_fortification_casualties_inflicted, barbarian_fortification_victory_contribution = calculate_fortification_strength(barbarian_fort_data)
        total_barbarian_fortification_victory_contribution += int(barbarian_fortification_victory_contribution)
        total_barbarian_fortification_casualties_inflicted += int(barbarian_fortification_casualties_inflicted)

    imperial_victory_contribution = total_imperial_force_victory_contribution + total_imperial_fortification_victory_contribution
    barbarian_victory_contribution = total_barbarian_force_victory_contribution + total_barbarian_fortification_victory_contribution
    imperial_casualties_inflicted = total_imperial_force_casualties_inflicted + total_imperial_fortification_casualties_inflicted
    barbarian_casualties_inflicted = total_barbarian_force_casualties_inflicted + total_barbarian_fortification_casualties_inflicted

    if imperial_victory_contribution > barbarian_victory_contribution:
        outcome = 'Imperial Victory'
        total_victory_points = int((imperial_victory_contribution - barbarian_victory_contribution) / 1000)
        if total_imperial_force_offensive_victory_contribution == 0:
            offensive_victory_points = 0
            defensive_victory_points = int((total_imperial_force_defensive_victory_contribution - barbarian_victory_contribution) / 1000)
        elif total_imperial_force_defensive_victory_contribution == 0:
            offensive_victory_points = int((total_imperial_force_offensive_victory_contribution - barbarian_victory_contribution) / 1000)
            defensive_victory_points = 0
        else:
            difference = (imperial_victory_contribution - barbarian_victory_contribution)
            offensive_split = total_imperial_force_offensive_victory_contribution / imperial_victory_contribution
            defensive_split = total_imperial_force_defensive_victory_contribution / imperial_victory_contribution
            offensive_victory_points = int((difference * offensive_split) / 1000 + 0.5)
            defensive_victory_points = int((difference * defensive_split) / 1000 + 0.5)

    elif imperial_victory_contribution == barbarian_victory_contribution:
        outcome = 'Draw'
        total_victory_points = 0
    
    else:
        outcome = 'Barbarian Victory'
        total_victory_points = int((barbarian_victory_contribution - imperial_victory_contribution) / 1000)
        if total_barbarian_force_offensive_victory_contribution == 0:
            offensive_victory_points = 0
            defensive_victory_points = int((total_barbarian_force_defensive_victory_contribution - imperial_victory_contribution) / 1000)
        elif total_barbarian_force_defensive_victory_contribution == 0:
            offensive_victory_points = int((total_barbarian_force_offensive_victory_contribution - imperial_victory_contribution) / 1000)
            defensive_victory_points = 0
        else:
            difference = (barbarian_victory_contribution - imperial_victory_contribution)
            offensive_split = total_barbarian_force_offensive_victory_contribution / barbarian_victory_contribution
            defensive_split = total_barbarian_force_defensive_victory_contribution / barbarian_victory_contribution
            offensive_victory_points = int((difference * offensive_split) / 1000 + 0.5)
            defensive_victory_points = int((difference * defensive_split) / 1000 + 0.5)

    # Summarize the outcome
    summary = {
        'imperial_victory_contribution': str(imperial_victory_contribution),
        'barbarian_victory_contribution': str(barbarian_victory_contribution),
        'imperial_casualties_inflicted': str(imperial_casualties_inflicted),
        'barbarian_casualties_inflicted': str(barbarian_casualties_inflicted),
        'outcome': outcome,
        'victory_points': str(total_victory_points),
        'offensive_victory_points': str(offensive_victory_points),
        'defensive_victory_points': str(defensive_victory_points),
    }
    
    return jsonify(summary)

def calculate_force_strength(force_data):
    force_strength = int(force_data['strength'])
    order_id = force_data['order']
    if order_id == '':
        order_id = 0
    order = Order.query.filter_by(order_id=order_id).first()
    casualties_inflicted_modifier = order.casualties_inflicted_modifier
    casualties_inflicted = int(((force_strength * (1 + casualties_inflicted_modifier))/10))
    if order.offensive_order:
        offensive_victory_modifier = order.territory_claimed_modifier
        offensive_victory_contribution = force_strength * (1 + offensive_victory_modifier)
        defensive_victory_contribution = 0
    else:
        defensive_victory_modifier = order.territory_defence_modifier
        defensive_victory_contribution = force_strength * (1 + defensive_victory_modifier)
        offensive_victory_contribution = 0
    return casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution

def calculate_fortification_strength(fort_data):
    fort_casualties_inflicted = 0
    fort = fort_data['fortification']
    fort = Fortification.query.filter_by(Fortification_id = fort).first()
    if fort_data['strength'].isdigit():
        fort_strength = int(fort_data['strength'])
    if fort_data['besieged']:
        fort_victory_contribution = fort_strength * 2
        fort_casualties_inflicted = fort_strength/10
    else:
        fort_victory_contribution = fort_strength
    
    return fort_casualties_inflicted, fort_victory_contribution

@app.route('/forces')
def forces():
    forces = Force.query.filter(Force.force_id != 0).all()
    return render_template('forces.html', forces=forces)

@app.route('/qualities')
def qualities():
    qualities = Quality.query.filter(Quality.quality_id != 0).all()
    return render_template('qualities.html', qualities=qualities)

@app.route('/orders')
def orders():
    orders = Order.query.filter(Order.order_id != 0).all()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)

    
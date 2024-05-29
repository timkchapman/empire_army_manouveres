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
    role = request.form.get('role')
    selected_barbarian = request.form.get('selected_barbarian', '')
    is_barbarian = request.form.get('barbarian', 'false') == 'true'

    forces = []

    if is_barbarian:
        force_list = Force.query.filter(Force.force_name.contains(selected_barbarian)).all()
        forces = [(force.force_id, force.force_name) for force in force_list]
    else:
        # Fetch imperial forces or other logic based on the role
        forces = [(force.force_id, force.force_name) for force in Force.query.join(Nation).filter(Nation.nation_faction == 'The Empire').all()]
    
    return jsonify({'forces': forces})

@app.route('/get_force_info', methods=['POST'])
def get_force_info():
    force_id = request.form['force_id']
    force = Force.query.get(force_id)
    if force:
        return jsonify({
            'quality': force.quality.quality_id,
            'large': force.large
        })
    return jsonify({'error': 'Force not found'}), 404

from flask import Flask, request, jsonify

@app.route('/get_rituals_by_force', methods=['POST'])
def get_rituals_by_force():
    rituals = Force_Ritual.query.filter_by(army_ritual=True).all()
    ritual_list = [(ritual.force_ritual_id, ritual.force_ritual_name) for ritual in rituals]

    return jsonify({'rituals': ritual_list})

@app.route('/get_force_ritual_effect', methods=['POST'])
def get_force_ritual_effect():
    ritual_id = request.form.get('ritual_id')
    ritual = Force_Ritual.query.get(ritual_id)
    if ritual:
        return jsonify({
            'force_effective_strength_modifier': ritual.force_effective_strength_modifier,
            'force_ritual_quality_id': ritual.force_ritual_quality_id
        })
    return jsonify({'error': 'Ritual not found'}), 404

@app.route('/get_orders_by_force', methods=['POST'])
def get_orders_by_force():
    force_id = request.form.get('force_id')
    if not force_id:
        return jsonify({'orders': []})
    
    force = Force.query.get(force_id)
    if not force:
        return jsonify({'orders': []})
    
    force_quality = request.form.get('force_quality') 
    quality = Quality.query.get(force_quality)
    if not quality:
        return jsonify({'orders': []})
    
    orders = Order.query.filter(Order.order_id.between(1, 8)).all()
    order_list = [(order.order_id, order.order_name, order.offensive_order) for order in orders]

    if force.nation_id == 7:
        national_orders = Order.query.filter(Order.order_id == 40).first()
        if national_orders:
            order_list.append((national_orders.order_id, national_orders.order_name, national_orders.offensive_order))
        order_list = [order for order in order_list if order[0] != 5]

    if force.nation.nation_faction != "The Empire":
        order_list = [order for order in order_list if order[0] !=4]

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

@app.route('/get_fortification_ritual_effect', methods=['POST'])
def get_fortification_ritual_effect():
    ritual_id = request.form.get('ritual_id')
    ritual = Fortification_Ritual.query.get(ritual_id)
    if ritual:
        return jsonify({
            'fortification_effective_strength_modifier': ritual.fortification_effective_strength_modifier,
        })
    return jsonify({'error': 'Ritual not found'}), 404

@app.route('/calculate_outcome', methods=['POST'])
def calculate_outcome():
    data = request.json
    
    # Initialize variables to store total strengths for forces and fortifications
    total_imperial_casualties_inflicted = 0
    total_imperial_victory_contribution = 0
    imperial_offensive_victory_contribution = 0
    imperial_defensive_victory_contribution = 0
    total_barbarian_casualties_inflicted = 0
    total_barbarian_victory_contribution = 0
    barbarian_offensive_victory_contribution = 0
    barbarian_defensive_victory_contribution = 0
    all_imperial_forces = []
    imperial_forces = []
    imperial_fortifications = []
    all_barbarian_forces = []
    barbarian_forces = []
    barbarian_fortifications = []
    forces_data = {}
    fortifications_data = {}
    
    # Calculate total imperial force victory contribution and casualties inflicted
    for imperial_force_data in data['imperial_forces']:
        force_id = imperial_force_data['force']
        force = Force.query.get(force_id)
        casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution = calculate_force_strength(imperial_force_data, data['imperial_forces'])
        total_imperial_casualties_inflicted += int(casualties_inflicted)
        imperial_offensive_victory_contribution += int(offensive_victory_contribution)
        imperial_defensive_victory_contribution += int(defensive_victory_contribution)
        total_imperial_victory_contribution += int(offensive_victory_contribution) + int(defensive_victory_contribution)
        imperial_forces.append(imperial_force_data)
        all_imperial_forces.append(imperial_force_data)
        forces_data[imperial_force_data['force']] = {
            'force_name': force.force_name,
            'strength': imperial_force_data['strength'],
            'casualties_taken': 0,
            'remaining_strength': imperial_force_data['strength']
        }

    # Calculate total imperial fortification victory contribution and casualties inflicted
    for imperial_fort_data in data['imperial_fortifications']:
        force_id = imperial_fort_data['fortification']
        force = Fortification.query.get(force_id)
        casualties_inflicted, victory_contribution = calculate_fortification_strength(imperial_fort_data)
        imperial_defensive_victory_contribution += int(victory_contribution)
        total_imperial_victory_contribution += int(victory_contribution)
        total_imperial_casualties_inflicted += int(casualties_inflicted)
        imperial_fortifications.append(imperial_fort_data)
        all_imperial_forces.append(imperial_fort_data)
        fortifications_data[imperial_fort_data['fortification']] = {
            'fortification_name': force.fortification_name,
            'strength': imperial_fort_data['strength'],
            'casualties_taken': 0,
            'remaining_strength': imperial_fort_data['strength']
        }

    # Calculate total barbarian force victory contribution and casualties inflicted
    for barbarian_force_data in data['barbarian_forces']:
        force_id = barbarian_force_data['force']
        force = Force.query.get(force_id)
        casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution = calculate_force_strength(barbarian_force_data, data['barbarian_forces'])
        total_barbarian_casualties_inflicted += int(casualties_inflicted)
        barbarian_offensive_victory_contribution += int(offensive_victory_contribution)
        barbarian_defensive_victory_contribution += int(defensive_victory_contribution)
        total_barbarian_victory_contribution += int(offensive_victory_contribution) + int(defensive_victory_contribution)
        barbarian_forces.append(barbarian_force_data)
        all_barbarian_forces.append(barbarian_force_data)
        forces_data[barbarian_force_data['force']] = {
            'force_name': force.force_name,
            'strength': barbarian_force_data['strength'],
            'casualties_taken': 0,
            'remaining_strength': barbarian_force_data['strength']
        }

    # Calculate total imperial fortification victory contribution and casualties inflicted
    for barbarian_fort_data in data['barbarian_fortifications']:
        force_id = barbarian_fort_data['fortification']
        force = Fortification.query.get(force_id)
        casualties_inflicted, victory_contribution = calculate_fortification_strength(barbarian_fort_data)
        barbarian_defensive_victory_contribution += int(victory_contribution)
        total_barbarian_victory_contribution += int(victory_contribution)
        total_barbarian_casualties_inflicted += int(casualties_inflicted)
        barbarian_fortifications.append(barbarian_fort_data)
        all_barbarian_forces.append(barbarian_fort_data)
        fortifications_data[barbarian_fort_data['fortification']] = {
            'fortification_name': force.fortification_name,
            'strength': barbarian_fort_data['strength'],
            'casualties_taken': 0,
            'remaining_strength': barbarian_fort_data['strength']
        }

    print('imperial contribution: ', total_imperial_victory_contribution, ', Barbarian Contribution: ', total_barbarian_victory_contribution)
    total_victory_points, offensive_victory_points, defensive_victory_points, outcome = calculate_victory_points(
        total_imperial_victory_contribution, imperial_offensive_victory_contribution, imperial_defensive_victory_contribution,
        total_barbarian_victory_contribution, barbarian_offensive_victory_contribution, barbarian_defensive_victory_contribution,
        all_imperial_forces, all_barbarian_forces
    )
    
    # Distribute casualties and calculate remaining strengths for forces
    imperial_force_casualties_taken, imperial_force_remaining_strength = distribute_force_casualties(
        total_barbarian_casualties_inflicted, imperial_forces, outcome, defensive_victory_points, imperial_forces, barbarian_forces
    )
    barbarian_force_casualties_taken, barbarian_force_remaining_strength = distribute_force_casualties(
        total_imperial_casualties_inflicted, barbarian_forces, outcome, defensive_victory_points, imperial_forces, barbarian_forces
    )

    # Distribute casualties and calculate remaining strengths for fortifications
    imperial_fort_casualties_taken, imperial_fort_remaining_strength = distribute_fortification_casualties(
        total_barbarian_casualties_inflicted, imperial_fortifications, outcome, defensive_victory_points, imperial_forces, barbarian_forces, is_barbarian=False
    )
    barbarian_fort_casualties_taken, barbarian_fort_remaining_strength = distribute_fortification_casualties(
        total_imperial_casualties_inflicted, barbarian_fortifications, outcome, defensive_victory_points, imperial_forces, barbarian_forces, is_barbarian = True
    )

    # Update forces_data with casualties and remaining strengths for imperial forces and fortifications
    for force_id, casualties in imperial_force_casualties_taken.items():
        forces_data[force_id]['casualties_taken'] = casualties
        forces_data[force_id]['remaining_strength'] = imperial_force_remaining_strength[force_id]
    
    for force_id, casualties in imperial_fort_casualties_taken.items():
        fortifications_data[force_id]['casualties_taken'] = casualties
        fortifications_data[force_id]['remaining_strength'] = imperial_fort_remaining_strength[force_id]

    # Update forces_data with casualties and remaining strengths for barbarian forces and fortifications
    for force_id, casualties in barbarian_force_casualties_taken.items():
        forces_data[force_id]['casualties_taken'] = casualties
        forces_data[force_id]['remaining_strength'] = barbarian_force_remaining_strength[force_id]
    
    for force_id, casualties in barbarian_fort_casualties_taken.items():
        fortifications_data[force_id]['casualties_taken'] = casualties
        fortifications_data[force_id]['remaining_strength'] = barbarian_fort_remaining_strength[force_id]

    # Summarize the outcome
    summary = {
        'total_victory_points': str(total_victory_points),
        'offensive_victory_points': str(offensive_victory_points),
        'defensive_victory_points': str(defensive_victory_points),
        'outcome': outcome,
        'forces_data': forces_data,
        'fortifications_data': fortifications_data
    }
    
    return jsonify(summary)

def calculate_force_strength(force_data, all_forces):
    victory_modifier = 0
    force_data_strength = force_data['strength']
    if force_data_strength == '':
        force_data_strength = 0
    force_strength = int(force_data_strength)
    order_id = force_data['order']
    if order_id == '':
        order_id = 0
    order = Order.query.get(order_id)
    force_ritual_id = force_data['ritual']
    if force_ritual_id == '':
        force_ritual_id = 0
    force_ritual = Force_Ritual.query.get(force_ritual_id)
    ritual_strength = force_ritual.force_effective_strength_modifier
    force_strength += ritual_strength
    casualties_inflicted_modifier = order.casualties_inflicted_modifier
    
    additional_casualties_inflicted_modifier = 0
    for other_force in all_forces:
        if other_force == force_data:
            continue
        other_order_id = other_force['order']
        if other_order_id == '':
            other_order_id = 0
        other_order = Order.query.get(other_order_id)
        if other_order.order_name == "Whatever it Takes":
            additional_casualties_inflicted_modifier += 0.1
        if other_order.order_name == "Fire in the Blood" and force_data.offensive_order:
            additional_casualties_inflicted_modifier += 0.1
    
    casualties_inflicted = int(((force_strength * (1 + casualties_inflicted_modifier + additional_casualties_inflicted_modifier))/10))
    if force_ritual.force_ritual_id == 2:
        victory_modifier = 2000
    if order.offensive_order:
        offensive_victory_modifier = order.territory_claimed_modifier
        offensive_victory_contribution = force_strength * (1 + offensive_victory_modifier) + victory_modifier
        defensive_victory_contribution = 0
    else:
        defensive_victory_modifier = order.territory_defence_modifier
        defensive_victory_contribution = force_strength * (1 + defensive_victory_modifier) + victory_modifier
        offensive_victory_contribution = 0
    return casualties_inflicted, offensive_victory_contribution, defensive_victory_contribution

def calculate_fortification_strength(fort_data):
    fort_casualties_inflicted = 0
    fort_ritual_id = fort_data['ritual']
    if fort_ritual_id == '':
        fort_ritual_id = 0
    fort_ritual = Fortification_Ritual.query.get(fort_ritual_id)
    fort_ritual_strength = fort_ritual.fortification_effective_strength_modifier
    if fort_data['strength'].isdigit():
        fort_strength = int(fort_data['strength'])
    fort_strength += fort_ritual_strength
    if fort_data['besieged']:
        fort_victory_contribution = fort_strength * 2
        fort_casualties_inflicted = fort_strength/10
    else:
        fort_victory_contribution = fort_strength
    
    return fort_casualties_inflicted, fort_victory_contribution

def calculate_victory_points(total_imperial_victory_contribution, imperial_offensive_victory_contribution,
                             imperial_defensive_victory_contribution, total_barbarian_victory_contribution,
                             barbarian_offensive_victory_contribution, barbarian_defensive_victory_contribution,
                             all_imperial_forces, all_barbarian_forces):
    
    offensive_victory_points = 0
    defensive_victory_points = 0
    imperial_orders = []
    imperial_offensive_orders = []
    imperial_defensive_orders = []
    barbarian_offensive_orders = []
    barbarian_defensive_orders = []

    for force in all_imperial_forces:
        if 'force' in force and force['force']:
            order_id = force['order']
            if order_id == '':
                order_id = 0
            order = Order.query.get(order_id)
            imperial_orders.append(order)
            if order.offensive_order:
                imperial_offensive_orders.append(order.order_name)
            else:
                imperial_defensive_orders.append(order.order_name)
    
    for force in all_barbarian_forces:
        if 'force' in force and force['force']:
            order_id = force['order']
            if order_id == '':
                order_id = 0
            order = Order.query.get(order_id)
            if order.offensive_order:
                barbarian_offensive_orders.append(order.order_name)
            else:
                barbarian_defensive_orders.append(order.order_name)

    disciplined_vp = 0
    if 'Strategic Defence' in imperial_defensive_orders:
        disciplined_vp = len(barbarian_offensive_orders)
        if disciplined_vp > 5:
            disciplined_vp = 5

    skirmishing_vp = 0
    if 'Outmanouvere' in imperial_offensive_orders:
        skirmishing_vp = len(barbarian_defensive_orders)
        if skirmishing_vp > 5:
            skirmishing_vp = 5

    if total_imperial_victory_contribution > total_barbarian_victory_contribution:
        outcome = 'Imperial Victory'
        total_victory_points = int((total_imperial_victory_contribution - total_barbarian_victory_contribution) / 1000)

        if imperial_offensive_victory_contribution == 0:
            offensive_victory_points = 0
            defensive_victory_points = int((imperial_defensive_victory_contribution - total_barbarian_victory_contribution) / 1000)
            defensive_victory_points += disciplined_vp
        elif imperial_defensive_victory_contribution == 0:
            offensive_victory_points = int((imperial_offensive_victory_contribution - total_barbarian_victory_contribution) / 1000)
            offensive_victory_points += skirmishing_vp
            defensive_victory_points = 0
        else:
            difference = total_imperial_victory_contribution - total_barbarian_victory_contribution
            offensive_split = imperial_offensive_victory_contribution / total_imperial_victory_contribution
            defensive_split = imperial_defensive_victory_contribution / total_imperial_victory_contribution

            # Calculate victory points without rounding to integers
            offensive_victory_points = int(difference * offensive_split / 1000)
            offensive_victory_points += skirmishing_vp
            defensive_victory_points = int(difference * defensive_split / 1000)
            defensive_victory_points += disciplined_vp

        # Adjust the split to ensure the total victory points remain consistent
        remaining_points = total_victory_points - (int(offensive_victory_points) + int(defensive_victory_points))
        if remaining_points != 0:
            if offensive_split > defensive_split:
                offensive_victory_points += remaining_points
            else:
                defensive_victory_points += remaining_points

    elif total_imperial_victory_contribution == total_barbarian_victory_contribution:
        outcome = 'Draw'
        total_victory_points = 0

    else:
        outcome = 'Barbarian Victory'
        total_victory_points = int((total_barbarian_victory_contribution - total_imperial_victory_contribution) / 1000)
        if barbarian_offensive_victory_contribution == 0:
            offensive_victory_points = 0
            defensive_victory_points = int((barbarian_defensive_victory_contribution - total_imperial_victory_contribution) / 1000)
        elif barbarian_defensive_victory_contribution == 0:
            offensive_victory_points = int((barbarian_offensive_victory_contribution - total_imperial_victory_contribution) / 1000)
            defensive_victory_points = 0
        else:
            difference = total_barbarian_victory_contribution - total_imperial_victory_contribution
            offensive_split = barbarian_offensive_victory_contribution / total_barbarian_victory_contribution
            defensive_split = barbarian_defensive_victory_contribution / total_barbarian_victory_contribution
            offensive_victory_points = int((difference * offensive_split) / 1000 + 0.5)
            defensive_victory_points = int((difference * defensive_split) / 1000 + 0.5)

    return total_victory_points, offensive_victory_points, defensive_victory_points, outcome

def distribute_force_casualties(total_casualties_inflicted, forces, outcome, defensive_victory_points, imperial_forces, barbarian_forces):
    casualties_taken = {}
    remaining_strength = {}
    force_break = 1000
    large_force_break = 1250

    # Filter forces based on conditions
    filtered_forces = [force for force in forces if 'force' in force and force.get('order') != "42"]

    # Check for global effects from barbarian and imperial orders
    if any(force in barbarian_forces for force in forces):
        for force in imperial_forces:
            order_id = force.get('order')
            if order_id:
                order = Order.query.get(order_id)
                if order.order_name == "Cruel":
                    force_break = 1500
                    large_force_break = 2250

    for force in filtered_forces:
        modifier = 1
        force_id = force.get('force')
        order_id = force.get('order', 0)
        force_data_strength = force['strength']
        if force_data_strength == '':
            force_data_strength = 0
        force_strength = int(force_data_strength)

        force_details = Force.query.get(force_id)

        if order_id:
            order = Order.query.get(order_id)
            modifier += order.casualties_suffered_modifier

        additional_casualty_reduction_modifier = 0
        for other_force in filtered_forces:
            if other_force == force:
                continue
            other_order_id = other_force.get('order')
            if other_order_id:
                other_order = Order.query.get(other_order_id)
                if other_order and other_order.order_name == "Tend the Fallen":
                    additional_casualty_reduction_modifier = -0.1
        modifier += additional_casualty_reduction_modifier

        if (outcome == 'Imperial Victory' and force in imperial_forces) or (outcome == 'Barbarian Victory' and force in barbarian_forces):
            modifier -= (defensive_victory_points / 100)

        modified_casualties = int(total_casualties_inflicted / len(filtered_forces) * modifier)
        if order_id and order.order_name == 'Lay Low':
            modified_casualties = 0

        casualties_taken[force_id] = modified_casualties
        new_strength = force_strength - casualties_taken[force_id]

        if not force_details.large and new_strength < force_break:
            new_strength = 0
        elif force_details.large and new_strength < large_force_break:
            new_strength = 0

        remaining_strength[force_id] = new_strength

    return casualties_taken, remaining_strength

def distribute_fortification_casualties(total_casualties_inflicted, forces, outcome, defensive_victory_points, imperial_forces, barbarian_forces, is_barbarian):
    casualties_taken = {}
    remaining_strength = {}
    fortification_break = 1000
    extra_fortification_casualties = 0

    # Filter forces based on conditions
    filtered_fortifications = [force for force in forces if 'fortification' in force and force.get('besieged')]

    # Only apply Storm the Walls logic if processing barbarian fortifications
    if is_barbarian:
        for force in imperial_forces:
            order_id = force.get('order')
            if order_id:
                order = Order.query.get(order_id)
                if order and order.order_name == "Storm the Walls":
                    extra_fortification_casualties = 0.3

    for force in filtered_fortifications:
        modifier = 1
        force_id = force.get('fortification')
        force_data_strength = force['strength']
        if force_data_strength == '':
            force_data_strength = 0
        force_strength = int(force_data_strength)

        modifier += extra_fortification_casualties

        if (outcome == 'Imperial Victory' and force in imperial_forces) or (outcome == 'Barbarian Victory' and force in barbarian_forces):
            modifier -= (defensive_victory_points / 100)

        modified_casualties = int(total_casualties_inflicted / len(filtered_fortifications) * modifier)

        casualties_taken[force_id] = modified_casualties
        new_strength = force_strength - casualties_taken[force_id]

        if new_strength < fortification_break:
            new_strength = 0

        remaining_strength[force_id] = new_strength

    return casualties_taken, remaining_strength


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

    
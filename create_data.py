import json
import os
from army_calculator import app, db
from army_calculator import Force, Fortification, Nation, Quality, Order, Force_Ritual, Fortification_Ritual, Territory_Ritual

def load_json(file_name):
    file_path = os.path.join('JSON', file_name)
    with open(file_path, 'r') as file:
        return json.load(file)
    
def populate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        nations = load_json('nation.json')
        for nation_data in nations:
            nation = Nation(**nation_data)
            db.session.add(nation)

        qualities = load_json('quality.json')
        for quality_data in qualities:
            quality = Quality(**quality_data)
            db.session.add(quality)

        orders = load_json('order.json')
        for order_data in orders:
            order = Order(**order_data)
            db.session.add(order)

        forces = load_json('force.json')
        for force_data in forces:
            force = Force(**force_data)
            db.session.add(force)

        fortifications = load_json('fortification.json')
        for fortification_data in fortifications:
            fortification = Fortification(**fortification_data)
            db.session.add(fortification)

        force_rituals = load_json('force_ritual.json')
        for force_ritual_data in force_rituals:
            force_ritual = Force_Ritual(**force_ritual_data)
            db.session.add(force_ritual)

        fortification_rituals = load_json('fortification_ritual.json')
        for fortification_ritual_data in fortification_rituals:
            fortification_ritual = Fortification_Ritual(**fortification_ritual_data)
            db.session.add(fortification_ritual)

        territory_rituals = load_json('territory_ritual.json')
        for territory_ritual_data in territory_rituals:
            territory_ritual = Territory_Ritual(**territory_ritual_data)
            db.session.add(territory_ritual)

        db.session.commit()
        print('Database populated with initial data.') 

def establish_quality_order_relationships():
    with app.app_context():
        qualities = Quality.query.all()
        orders = Order.query.all()
        for quality in qualities:
            if quality.quality_name == 'Agramant':
                quality.quality_orders = [orders[31]]
            if quality.quality_name == 'Conquering':
                quality.quality_orders = [orders[9]]
            elif quality.quality_name == 'Cruel':
                quality.quality_orders = [orders[10]]
            elif quality.quality_name == 'Cunning':
                quality.quality_orders = [orders[11]]
            elif quality.quality_name == 'Daring':
                quality.quality_orders = [orders[12]]
            elif quality.quality_name == 'Disciplined':
                quality.quality_orders = [orders[13]]
            elif quality.quality_name == 'Driven':
                quality.quality_orders = [orders[14], orders[15]]
            elif quality.quality_name == 'Engineer':
                quality.quality_orders = [orders[16], orders[17]]
            elif quality.quality_name == 'Farsighted':
                quality.quality_orders = [orders[18]]
            elif quality.quality_name == 'Fast':
                quality.quality_orders = [orders[19], orders[20]]
            elif quality.quality_name == 'Favoured':
                quality.quality_orders = [orders[24], orders[29], orders[46], orders[47], orders[48]]
            elif quality.quality_name == 'Foraging':
                quality.quality_orders = [orders[21]]
            elif quality.quality_name == 'Freedom Fighters':
                quality.quality_orders = [orders[22], orders[23]]
            elif quality.quality_name == 'Glorious':
                quality.quality_orders = [orders[24], orders[25]]
            elif quality.quality_name == 'Guerilla':
                quality.quality_orders = [orders[23]]
            elif quality.quality_name == 'Hard Bitten':
                quality.quality_orders = [orders[26]]
            elif quality.quality_name == 'Heroic':
                quality.quality_orders = [orders[27], orders[24], orders[25]]
            elif quality.quality_name == 'Highest Discipline':
                quality.quality_orders = [orders[41], orders[42], orders[43], orders[44], orders[45]]
            elif quality.quality_name == 'Hillwise':
                quality.quality_orders = [orders[49]]
            elif quality.quality_name == 'Indomitable Glory':
                quality.quality_orders = [orders[28], orders[24], orders[25]]
            elif quality.quality_name == 'Magic':
                quality.quality_orders = [orders[29]]
            elif quality.quality_name == 'Physick':
                quality.quality_orders = [orders[30]]
            elif quality.quality_name == 'Relentless':
                quality.quality_orders = [orders[31]]
            elif quality.quality_name == 'Resilient':
                quality.quality_orders = [orders[15]]
            elif quality.quality_name == 'Scouting':
                quality.quality_orders = [orders[33], orders[34]]
            elif quality.quality_name == 'Seawatch':
                quality.quality_orders = [orders[50]]
            elif quality.quality_name == 'Secretive':
                quality.quality_orders = [orders[32], orders[15]]
            elif quality.quality_name == 'Siege':
                quality.quality_orders = [orders[16]]
            elif quality.quality_name == 'Skirmishing':
                quality.quality_orders = [orders[35]]
            elif quality.quality_name == 'Thornbound':
                quality.quality_orders = [orders[36]]
            elif quality.quality_name == 'Venomous':
                quality.quality_orders = [orders[37]]
            elif quality.quality_name == 'Watchful':
                quality.quality_orders = [orders[38], orders[39]]
            elif quality.quality_name == 'Quick-Witted':
                quality.quality_orders = [orders[34], orders[50]]

        db.session.commit()
        print('Quality-Order relationships established.')

if __name__ == '__main__':
    populate_db()
    establish_quality_order_relationships()
from flask import (Flask, g, jsonify, redirect, render_template, request, session)
from passlib.hash import pbkdf2_sha256

from db import Database

DATABASE_PATH = 'properties.db'

app = Flask(__name__)
app.secret_key = b'demokeynotreal!'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = Database(DATABASE_PATH)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/mybookings')
def mybookings():
    if 'user' in session:
        return render_template('mybookings.html')
    else:
        return redirect('/login')
    
@app.route('/manage')
def manage():
    return render_template('manage.html')

@app.route('/addproperty')
def addproperty():
    return render_template('addproperty.html')

def generate_get_properties_response(args):
    user_id = None
    if 'user' in session:
        user_id = session['user']['id']
    print("user id is " + str(user_id))
    
    n = args.get('n', default=6)
    offset = args.get('offset', default=0)
    properties = get_db().get_properties(n, offset)
    
    for property in properties:
        property['type'] = get_db().get_property_type(property['id'], user_id)

    properties = list(filter(lambda property: property['type'] != 'owned', properties))

    return jsonify({
        'properties': properties,
        'total': get_db().get_num_properties(),
    })

@app.route('/api/get_properties', methods=['GET'])
def api_get_properties():
    return generate_get_properties_response(request.args)

@app.route('/api/book_visit', methods=['POST'])
def api_book_visit():
    if 'user' in session:
        property_id = request.form.get('property_id', type=int)
        user_id = session['user']['id']
        # get_db().update_property(property_id, user_id)
        get_db().add_booking_for_user(property_id, user_id)
        return generate_get_properties_response(request.form)    
    else:
        return jsonify('Error: User not authenticated'), 401

def generate_my_properties_response(args, bookedOrOwned):
    user_id = session['user']['id']
    print("user id is " + str(user_id))
    
    n = args.get('n', default=6)
    offset = args.get('offset', default=0)
    properties = get_db().get_user_properties(user_id, bookedOrOwned)

    return jsonify({
        'properties': properties,
        'total': len(properties)
    })

@app.route('/api/my_bookings', methods=['GET'])
def api_my_bookings():
    if 'user' in session:
        return generate_my_properties_response(request.args, -1)
    else:
        return jsonify('Error: User not authenticated')

@app.route('/api/my_properties', methods=['GET'])
def api_my_properties():
    if 'user' in session:
        return generate_my_properties_response(request.args, 2)
    else:
        return jsonify('Error: User not authenticated')


@app.route('/api/cancel_booking', methods=['POST'])
def api_cancel():
        if 'user' in session:
            property_id = request.form.get('property_id')
            user_id = session['user']['id']
            get_db().remove_booking_for_user(property_id, user_id)
            #get_db().update_property(property_id, -1),
            return generate_my_properties_response(request.form, -1)
        else:
            return jsonify('Error: User not authenticated')

@app.route('/api/remove_property', methods=['POST'])
def api_remove():
        if 'user' in session:
            property_id = request.form.get('property_id')
            user_id = session['user']['id']
            get_db().remove_property_for_user(user_id, property_id)
            #get_db().update_property(property_id, -1),
            return generate_my_properties_response(request.form, 2)
        else:
            return jsonify('Error: User not authenticated')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if name and username and typed_password:
            encrypted_password = pbkdf2_sha256.hash(typed_password)
            get_db().create_user(name, username, encrypted_password)
            return redirect('/login')
    return render_template('create_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if username and typed_password:
            user = get_db().get_user(username)
            if user:
                if pbkdf2_sha256.verify(typed_password, user['encrypted_password']):
                    session['user'] = user
                    return redirect('/')
                else:
                    message = "Incorrect password, please try again"
            else:
                message = "Unknown user, please try again"
        elif username and not typed_password:
            message = "Missing password, please try again"
        elif not username and typed_password:
            message = "Missing username, please try again"
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/addproperty', methods=['POST'])
def add_property():
    if 'user' in session:
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        address = request.form.get('address')
        city = request.form.get('city')
        country = request.form.get('country')
        image = request.form.get('image')
        user_id = session['user']['id']
        # get_db().update_property(property_id, user_id)
        get_db().add_property_for_user(user_id, name, description, price, address, city, country, image)
        return redirect('/manage')
    else:
        return jsonify('Error: User not authenticated'), 401
    


if __name__ == '__main__':
    app.run(host='localhost', port=8081, debug=True)


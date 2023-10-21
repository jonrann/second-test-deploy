from tv_shows_flask_app import app
from tv_shows_flask_app.models import user as user_module
from tv_shows_flask_app.models import tv_show as tv_show_module
from tv_shows_flask_app.models import like as like_module
from flask import render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

bcrypt = Bcrypt(app)

# ------- RENDER ROUTES -------

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/shows')
def dashboard():
    if 'user_id' not in session:
        flash('Must log in', 'login_error')
        return redirect(url_for('login_page'))
    # Create a get show with users function
    shows = tv_show_module.TV_show.get_shows_with_creator()
    current_user = user_module.User.get_by_id(session['user_id'])
    current_user.likes = user_module.User.get_user_with_liked_shows(session['user_id'])
    likes_status = {}
    for show in shows:
        likes_status[show.id] = like_module.Like.check_like(current_user.id, show.id)


    return render_template('dashboard.html', shows=shows, current_user=current_user, likes_status=likes_status)


# ------ POST ROUTES -------

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    data = {
        'first_name' : first_name,
        'last_name' : last_name,
        'email' : email,
        'password' : password,
        'confirm_password' : confirm_password
    }

    if not user_module.User.validate_user(data):
        return redirect(url_for('login_page'))
    
    hashed_pw = generate_password_hash(data['password'])
    data['password'] = hashed_pw

    user_id = user_module.User.create_user(data)
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        flash('Failed to register', 'register_error')
        return redirect(url_for('login_page'))
    
@app.route('/login', methods=['POST'])
def login():
    user_data = dict(request.form)
    user = user_module.User.get_by_email(user_data['email'])
    if user:
        if check_password_hash(user.password, user_data['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect password', 'login_error')
            return redirect(url_for('login_page'))
    else:
        flash('Email not found', 'login_error')
        return redirect(url_for('login_page'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))

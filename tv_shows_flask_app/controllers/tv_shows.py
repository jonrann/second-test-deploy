from tv_shows_flask_app import app
from tv_shows_flask_app.models import tv_show as tv_show_module
from tv_shows_flask_app.models import user as user_module
from tv_shows_flask_app.models import like as like_module
from flask import render_template, redirect, url_for, request, session, flash

# ------- RENDER ROUTES -------

@app.route('/shows/new')
def add_show_page():
    if 'user_id' not in session:
        flash('Must log in', 'login_error')
        return redirect(url_for('login_page'))
    return render_template('create_show.html')

@app.route('/shows/<int:show_id>/<user_id>')
def show_page(show_id, user_id):
    if 'user_id' not in session:
        flash('Must log in', 'login_error')
        return redirect(url_for('login_page'))
    show= tv_show_module.TV_show.get_one_show_with_creator(show_id, user_id)
    shows = tv_show_module.TV_show.get_show_with_liked_users(show_id)
    return render_template('view_show.html', show=show, shows=shows)

@app.route('/shows/edit/<int:show_id>')
def edit_page(show_id):
    if 'user_id' not in session:
        flash('Must log in', 'login_error')
        return redirect(url_for('login_page'))
    show = tv_show_module.TV_show.get_by_id(show_id) 
    return render_template('edit_show.html', show=show)


# ------ POST ROUTES ---------

@app.route('/create_show', methods=['POST'])
def create_show():
    show_data = dict(request.form)
    show_data['user_id'] = session['user_id']
    # Validate show data
    if not tv_show_module.TV_show.validate_show(show_data):
        return redirect(url_for('add_show_page'))

    # Create new show
    show_id = tv_show_module.TV_show.create_show(show_data)
    # Intialize new show as object
    show = tv_show_module.TV_show.get_by_id(show_id)
    current_user = user_module.User.get_by_id(session['user_id'])

    show.creator = current_user

    return redirect(url_for('dashboard'))

@app.route('/edit_show', methods=['POST'])
def edit_show():
    show_data = dict(request.form)
    show_data['user_id'] = session['user_id']
    # Validate show data
    if not tv_show_module.TV_show.validate_show(show_data):
        return redirect(url_for('edit_page', show_id=show_data['id']))
    # Create Update function
    tv_show_module.TV_show.update_show(show_data)
    return redirect(url_for('dashboard'))

@app.route('/shows/delete/<show_id>')
def delete_show(show_id):
    tv_show_module.TV_show.delete_show(show_id)
    return redirect(url_for('dashboard'))

@app.route('/shows/like/<int:show_id>', methods=['POST'])
def like_show(show_id):
    show = tv_show_module.TV_show.get_by_id(show_id)
    current_user = user_module.User.get_by_id(session['user_id'])
    
    current_user.add_to_likes(show)
    show.add_to_liked_by(current_user)

    like_module.Like.like_tv_show(current_user.id, show.id)
    
    return redirect(url_for('dashboard'))

@app.route('/shows/dislike/<int:show_id>', methods=['POST'])
def dislike_show(show_id):
    show = tv_show_module.TV_show.get_by_id(show_id)
    current_user = user_module.User.get_by_id(session['user_id'])
    
    current_user.remove_from_likes(show)
    show.remove_from_liked_by(current_user)

    like_module.Like.unlike_tv_show(current_user.id, show.id)

    return redirect(url_for('dashboard'))

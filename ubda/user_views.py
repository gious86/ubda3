from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, Access_level, Device
from . import db
from datetime import datetime


user_views = Blueprint('user_views', __name__)


@user_views.route('/users')
@login_required
def users():
    access_levels = Access_level.query.all()
    access_level_names = {}
    for access_level in access_levels:
        access_level_names.update({access_level.id : access_level.name})
    users = current_user.created_users
    print (access_levels)
    return render_template("users.html", 
                            current_user = current_user, 
                            access_level_names = access_level_names, 
                            users = users )


@user_views.route('/new_user', methods=['GET', 'POST'])
@login_required
def new_user():
    if request.method == 'POST':
        user_name = request.form.get('userName')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        access_level = request.form.get('access_level')
        card_number = request.form.get('card_number')
        print('****')
        try:
            valid_thru = datetime.strptime(request.form.get('valid_thru'), '%Y-%m-%d')
        except:
            valid_thru = None
        user = User.query.filter_by(user_name=user_name).first()
        if user:
            flash('User already exists.', category='error')
        elif len(user_name) < 4:
            flash('User name must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 5:
            flash('Password must be at least 5 characters.', category='error')
        elif valid_thru is None:
            flash('No date.', category='error')
        else:
            new_user = User(user_name = user_name, 
                            first_name = first_name, 
                            password = generate_password_hash(password1, method='sha256'),
                            access_level = access_level,
                            card_number = card_number,
                            valid_thru = valid_thru,
                            created_by = current_user.id)
            db.session.add(new_user)
            db.session.commit()
            flash('User added', category='success')
            return redirect(url_for('user_views.users'))
    accessLevels = Access_level.query.all()
    return render_template("new_user.html", user=current_user, accessLevels = accessLevels)


@user_views.route('/edit_user/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.filter_by(id=id).first()
    if not user :
        flash(f'No person with id:{id}', category='error')
        return redirect(url_for('views.personnel'))
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        access_level_id = request.form.get('access_level')
        card_number = request.form.get('card_number')
        valid_thru = datetime.strptime(request.form.get('valid_thru'), '%Y-%m-%d')
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.access_level = access_level_id
        user.card_number = card_number
        user.valid_thru = valid_thru
        db.session.add(user)
        db.session.commit()
        flash('Person information updated', category='success')
        return redirect(url_for('user_views.users'))
    access_levels = Access_level.query.all() 
    return render_template("edit_user.html", current_user = current_user, 
                                            user = user, 
                                            access_levels = access_levels)


@user_views.route('/delete_user/<string:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user :
        flash(f'No user with id:{id}', category='error')
        return redirect(url_for('user_views.users'))
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash('Person deleted', category='success')
        return redirect(url_for('user_views.users'))
    return render_template("delete_user.html", current_user = current_user, user=user)


@user_views.route('/user_access_log/<string:id>')
@login_required
def user_access_log(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        flash(f'No user with id:{id}', category='error')
        return redirect(url_for('user_views.users'))
    else:
        devices = Device.query.all()
        device_names = {}
        for device in devices:
            device_names.update({device.id : device.name})
        return render_template("user_access_log.html",
                                device_names = device_names, 
                                current_user = current_user, 
                                user = user)
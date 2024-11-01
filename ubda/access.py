from flask import Blueprint, render_template, redirect, flash, url_for, send_file, request
from flask_login import login_user, current_user
from .models import User, Device
from . import hostname
from .device_server import activate_allowed_outputs, online_devices
import qrcode, io
from werkzeug.security import check_password_hash

access = Blueprint('access', __name__)


@access.route("/qr/<string:id>")
def qr_generator(id):
    url = hostname + url_for('access.url_access', id = id)
    qr_img = generate_qr(url)
    return send_file(qr_img, mimetype='image/png')


@access.route("/<string:id>", methods=['GET', 'POST'])
#@login_required
def url_access(id):
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user = User.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error') 
    if current_user.is_authenticated:
        device = Device.query.filter_by(mac = id).first()
        if not device:
            flash(f'device with id:{id} does not exist!', category='error')
        elif activate_allowed_outputs(current_user, device, 'pin') > 0: 
            if device.id in online_devices:
                flash(f'Welcome {current_user.user_name}')
            else: 
                flash(f'Sorry {current_user.user_name}, Device is offline', category='error')
        else:
            flash(f'Sorry {current_user.user_name}, you have no access!', category='error')
    return render_template('acc.html', url = url_for('access.url_access', id=id))


def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io)
    img_io.seek(0)
    return img_io



from . import db, sock, device_models
from flask import request
from .models import Device, Output, User, Access_log, Access_level
import json
import time


to_devices = {}


def activate_allowed_outputs(user, device, method):
    log_entry = Access_log(device = device.id, user = user.id)
    access_level = Access_level.query.filter_by(id = user.access_level).first()
    if not access_level or not device in access_level.devices:
        result = -1
        log_entry.content = "access denied, method: " + method
    else:
        outputs = []
        for o in access_level.outputs:
            if o.device == device.id:
                outputs.append(o.n)
        cmd = '{"open":%s}' %str(outputs)
        to_devices.update({device.id:cmd}) 
        result = 1
        log_entry.content = "access granted, method: " + method
    db.session.add(log_entry)
    db.session.commit()
    return result


@sock.route('/ws/<string:id>')
def dev_server(ws, id):
    client_ip = request.remote_addr
    print(f'incomming connection id:"{id}"')
    data = ws.receive(1)
    if not data:
        print('timeout')
        ws.close()
        return
    else:
        model = None        
        try:
            js = json.loads(data)
            model = js['model']
        except Exception as e:              
            print(f'exception:{e}')
        if not model:
            print('unsupported format, closing connection...')
        elif not model in device_models:     
            print(f'unknown device model "{model}", closing connection...')
        else:
            print(f'connection from:"{client_ip}", device id: "{id}", device model: "{model}"')   
            device = Device.query.filter_by(mac=id).first()
            if not device:
                print(f'new device adding to DB...')
                device = Device(mac = id, 
                                model = model,
                                name = id, 
                                last_seen = int(time.time()))
                db.session.add(device)
                db.session.commit()
                n_of_outputs = device_models[model]['outputs']
                for n in range(1, n_of_outputs+1):
                    output = Output(device = device.id, 
                                    name = f'{id} - {n}',
                                    n=n)
                    db.session.add(output)
                db.session.commit()
                print(f'device with id:{id} added to DB')
            else :
                print('known device')
        while True:
            try:
                data = ws.receive(1) 
                if data:
                    print(f'from device "{device.mac}" - "{data}"')
                    device.last_seen = int(time.time())
                    js = ''
                    try:
                        js = json.loads(data)
                    except: pass
                    if js:
                        if 'card' in js:
                            card = js['card']
                            person = User.query.filter_by(card_number = card).first()
                            if person:
                                if activate_allowed_outputs(person, device, 'card') > 0: 
                                    print(f'access granted - {person.first_name}')
                                else:
                                    print(f'no access - {person.first_name}')
                            else :
                                log_entry = Access_log(device = device.id, 
                                                        content = 'unknown card:' + card)
                                db.session.add(log_entry)
                                db.session.commit()
                                print(f'unknown card:{card}')
                        #if something in js: do something
                    db.session.add(device)
                    db.session.commit()
                if device.id in to_devices:
                    cmd = to_devices[device.id]
                    print(f'to device "{device.mac}" - "{cmd}"')
                    ws.send(cmd)
                    to_devices.pop(device.id)
            except Exception as e:
                print(f'connection with "{id}" closed. e:{e}')
                break
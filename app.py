import os
import jsonpickle
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask import Flask, request, Response, render_template
#from flask_modus import Modus

app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.cfg')

#modus = Modus(app)
db = SQLAlchemy(app)

class DoctorModel(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key= True, autoincrement= "auto")
    doctor_name = db.Column(db.String(50))

    # device_id = db.Column(db.String(32), nullable = True)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate= db.func.now())

    # Relationship
    devices = db.relationship("DeviceModel", backref = 'doctor', lazy='dynamic')
    
    def __repr__(self):
        return f'<DoctorModel {self.doctor_name}>'

class DeviceModel(db.Model):
    __tablename__= 'devices'

    id = db.Column(db.String(50), primary_key =True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable= False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate= db.func.now())

    # Relationship
    image = db.relationship("ImageModel", backref = 'device', lazy='dynamic')

    def __repr__(self):
        return f'<Device {self.id}>'

class ImageModel(db.Model):
    __tablename__ ='patient_images'

    id = db.Column(db.Integer, primary_key= True , autoincrement= "auto")
    device_id = db.Column(db.String(50), db.ForeignKey("devices.id"), nullable= False)

    # doc_id = db.Column(db.String(32), db.ForeignKey('doctor_details.id'), nullable= False)

    label = db.Column(db.String(50), nullable= True)
    image_detail = db.Column(db.String(256))

    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate= db.func.now())

    def __repr__(self):
        return f"<Car {self.device_id}>"

@app.route('/')
def hello():
    return {"hello": "world"}

@app.route('/testimages', methods = ['POST'])
def patient_images():
    # if request.is_json:
    doctor_name = request.values.get('doctor_name')
    device_id = request.values.get('id')
    files = request.files.getlist("fileToUpload")

    doc_detail = DoctorModel.query.filter_by(doctor_name = doctor_name).first()
    if doc_detail is not None:
        doc_id = doc_detail.id
        dev_details = DeviceModel.query.filter_by(doctor_id = doc_id, id= device_id).first()
        if dev_details.id is not None:
            
            doc_path = os.path.join(app.config['UPLOAD_FOLDER'], str(doc_id))
            doc_path_update = doc_path + '/'+ str(dev_details.id)
            mode = 0o777
            print('for the doctorid folder')
            print(os.path.isdir(doc_path))
            print('for the device folder')
            print(os.path.isdir(doc_path_update))

            if os.path.isdir(doc_path) == False:
                # doc_path = doc_path + '/'+ str(dev_details.id)
                os.makedirs(doc_path_update, mode)
            else:
                if os.path.isdir(doc_path_update) == False:
                    os.mkdir(doc_path_update, mode)

            for file_daa in files:
                filename = secure_filename(file_daa.filename)
                file_daa.save(os.path.join(doc_path_update, filename))
                path_for_save = str(doc_id) + '/' + str(dev_details.id) + '/' + str(filename)
                image = ImageModel( image_detail= path_for_save , device_id = str(dev_details.id))
                db.session.add(image)
            db.session.commit()
    response = {'message': 'image received'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200,
                mimetype='application/json')

@app.route('/index/<string:doc_name>.html', methods=['GET'])
def show_index(doc_name):
    doctor_instance = DoctorModel.query.filter_by(doctor_name=doc_name).first()
    return render_template('index.html', doctor=doctor_instance,  folder = app.config['UPLOAD_FOLDER'])


# @app.route('/images', methods = ['POST', 'GET'])
# def handle_images():
#     if request.method == 'POST':
#         if request.is_json:
#             data = request.get_json()
#             new_image = ImageModel(name = data['name'], model= data['model'], doors= data['doors'])
#             db.session.add(new_image)
#             db.session.commit()

#             return {"message": f"car {new_image.name} has been created successfully."}
#         else:
#             return {"error": "The request payload is not in JSON format."}
#     elif request.method == 'GET':
#         images = ImageModel.query.all()
#         results = [
#             {
#                 "name": image.name,
#                 "model": image.model,
#                 "doors": image.doors
#             }for image in images ]

#         return {"count": len(results), "images": results , "message": "success" }

if __name__ == '__main__':
    app.run()

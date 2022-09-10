from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json, warnings, pickle, urllib, mailer
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solarData.db'
db = SQLAlchemy(app)
app.app_context().push()

class Classifiers(db.Model):
    __tablename__ = 'classifiers'
    arduinoId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nSer = db.Column(db.Integer, nullable=False)
    nPar = db.Column(db.Integer, nullable=False)
    clf = db.Column(db.String, unique=True)
    email = db.Column(db.String, nullable=False)

predict_result={1:"Normal",
                2:"Open Circuit Fault",
                3:"Line-Line Fault"}

@app.route('/classify', methods=['POST'])
def classify():
    print("Request received for classifying")
    data = json.loads(request.get_data().decode('UTF-8'))
    print(data)
    rec = Classifiers.query.filter(Classifiers.arduinoId==data['arduinoId']).first()
    if not rec:
        return "Arduino Data not found. Please setup again"
    rf = pickle.load(open(rec.clf, 'rb'))
    test_ip = [[data['Irradiance'], data['Temperature'], data['Current'], data['Voltage']]]
    print("Classifying Condition...")
    prediction = rf.predict(test_ip)
    print("Classification Result: ", predict_result[prediction[0]])
    if prediction[0] != 1:
    	mailer.sendMail(rec.email, predict_result[prediction[0]], rec.arduinoId)
    	print("Sending Result to Microcontroller")
    return predict_result[prediction[0]]

@app.route('/')
def home():
	return "<p>App Running...</p>"

@app.route('/setup', methods=['POST'])
def setup():
    print("Setup Request Received")
    print("Setting up device...")
    
    try:
        data = json.loads(request.get_data().decode('UTF-8'))
        print(data)
        classifier = Classifiers(nSer=data['nSer'], nPar=data['nPar'], email=data['email'])
        urllib.request.urlretrieve(data['trainSetUrl'], 'temp.csv')
        ds = pd.read_csv("temp.csv", on_bad_lines='skip')
        X = ds.values[:, :4]
        Y = ds.values[:, 4] 
        rf = RandomForestClassifier()
        rf.fit(X,Y)
        print("Model has been trained")
        db.session.add(classifier)
        db.session.commit()
        filename = f'classifiers/Ard-{classifier.arduinoId}.sav'
        pickle.dump(rf, open(filename, 'wb'))
        classifier.clf = filename
        db.session.commit()
        print("Microncontroller ID: ", classifier.arduinoId)
    except Exception as e:
        print(e)
        print("Setup Failed!")
    print("Setup Successful!")
    return str(classifier.arduinoId)


if __name__ == "__main__":
    # User can change the host IP
    app.run(host='0.0.0.0', port=8080, debug=True)
   

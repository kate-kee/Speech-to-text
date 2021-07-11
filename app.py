from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from ibm_watson import SpeechToTextV1 
import json
import wget
import os
from pandas.io.json import json_normalize
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import time
start_time = time.time()
url_s2t = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/73c19406-585b-4097-b536-7108cfca339a"
iam_apikey_s2t = "jQzePja386V1VYh-2nY5byJn0-hZvpCpFmSKTuB4ncFW"
app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def index():
        return render_template('index.html')
@app.route('/opt1')
def opt():
        return render_template('opt1.html')
@app.route('/update', methods=['GET', 'POST'])
def update():
        if request.method == 'POST':
                f = request.files['file']
                name=f.filename
                f.save(secure_filename(f.filename))
                url=os.getcwd()+'/'+'PolynomialRegressionandPipelines.mp3'
                authenticator = IAMAuthenticator(iam_apikey_s2t)
                s2t = SpeechToTextV1(authenticator=authenticator)
           
                s2t.set_service_url(url_s2t)
                print(time.time() - start_time)
                with open(url, mode="rb")  as wav:
                        response = s2t.recognize(audio=wav, content_type='audio/mp3')
                print(time.time() - start_time)     
                json_normalize(response.result['results'],"alternatives")
                print(time.time() - start_time)
                recognized_text=""
                for i in range (0,len(response.result['results'])):
                        recognized_text=recognized_text+response.result['results'][i]['alternatives'][0]["transcript"]+". "
                print(time.time() - start_time)
                return render_template('/update.html',text=recognized_text)
                
if __name__ == "__main__":
    app.run(debug=True)

    
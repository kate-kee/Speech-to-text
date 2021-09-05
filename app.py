from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from ibm_watson import SpeechToTextV1 
import json
import wget
import os
from pandas.io.json import json_normalize
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from pandas.io.json import json_normalize
from ibm_watson import TextToSpeechV1 
import shutil
lang=""
url_s2t = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/73c19406-585b-4097-b536-7108cfca339a"
iam_apikey_s2t = "jQzePja386V1VYh-2nY5byJn0-hZvpCpFmSKTuB4ncFW"
url_lt='https://api.us-south.language-translator.watson.cloud.ibm.com/instances/aa508f1a-3790-4b52-9ee9-c3fbbd6bfd5f'
apikey_lt='9SMOKltm-Ap0fn_3jocOaksIt82OkS6gYG6JXIR_aq88'
version_lt='2018-05-01'
url_ts="https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/1ae877c3-ef77-4391-a652-65a8a25a709f"        
key_ts="qqMKgZ9rjFYHLvpN9LRt-x_oEoJkf-dn-LruxFqJQqVk"
app = Flask(__name__)
k=0
@app.route('/', methods=['POST', 'GET'])
def index():
        return render_template('index.html')
@app.route('/opt1')
def opt():
        return render_template('opt1.html')
s=[] 
@app.route('/update2/<int:j>', methods=['GET', 'POST'])
def update2(j):
                authenticator = IAMAuthenticator(apikey_lt)
                language_translator = LanguageTranslatorV3(version=version_lt,authenticator=authenticator)
                language_translator.set_service_url(url_lt)
                s=json_normalize(language_translator.list_identifiable_languages().get_result(), "languages")
                n=[]
                for i in range(0,76):
                        n.append(s.name[i])
                return render_template('update2.html',text=n,m=j)                   
@app.route('/opt2/<string:i>/<int:m>')
def opt2(i,m):
        lang=i;
        print(lang)
        return render_template('opt2.html',lang=lang,m=m)   
def speechtotext(url):
                recognized_text=""
                authenticator = IAMAuthenticator(iam_apikey_s2t)
                s2t = SpeechToTextV1(authenticator=authenticator)
                s2t.set_service_url(url_s2t)
                with open(url, mode="rb")  as wav:
                        response = s2t.recognize(audio=wav, content_type='audio/mp3')  
                json_normalize(response.result['results'],"alternatives")
                for i in range (0,len(response.result['results'])):
                        recognized_text=recognized_text+response.result['results'][i]['alternatives'][0]["transcript"]+". "
                if recognized_text==" ":
                        recognized_text="Sorry, no text to translate!"
                return recognized_text
def texttranslator(lang,recognized_text):
                authenticator = IAMAuthenticator(apikey_lt)
                language_translator = LanguageTranslatorV3(version=version_lt,authenticator=authenticator)
                language_translator.set_service_url(url_lt)
                i=0
                s=json_normalize(language_translator.list_identifiable_languages().get_result(), "languages")
                for i in range(0,76):
                        if s.name[i]==lang:
                                break
                print(i)
                l='en-'+s.language[i]
                translation_response = language_translator.translate(text=recognized_text, model_id=l)
                translation=translation_response.get_result()
                print("done2")
                my_translation =translation['translations'][0]['translation']
                return my_translation
def texttospeech(my_translation):
                recognized_text=my_translation
                f1="one.mp3"
                authenticator = IAMAuthenticator(key_ts)
                text_translator = TextToSpeechV1(authenticator=authenticator)
                text_translator.set_service_url(url_ts)   
                url=os.getcwd()
                try:
                        with open(f1, 'wb') as audio_file:
                                audio_file.write(text_translator.synthesize(recognized_text,voice='en-US_AllisonV3Voice',accept='audio/mp3').get_result().content)
                        de=url+'/'+'static'
                        so=url+'/'+f1   
                        dest = shutil.move(so,de) 
                        return "file moved to static folder"
                except:
                        return 'There was an issue adding your task'
                return f1
        

@app.route('/update', methods=['GET', 'POST'])
def update():
        f = request.files['file']
        name=f.filename
        print(name)
        f.save(secure_filename(f.filename))
        url=os.getcwd()+'/'+name
        recognized_text =speechtotext(url)
        return render_template('update.html',text=recognized_text)

@app.route('/update3/<string:lang>/<int:m>', methods=['GET', 'POST'])
def update3(lang,m):
        translated=""
        recognized_text=""
        f = request.files['file']
        name=f.filename
        print(name)
        f.save(secure_filename(f.filename))
        url=os.getcwd()+'/'+name
        recognized_text = speechtotext(url)
        translated=texttranslator(lang,recognized_text)
        if m==2:
                return render_template('update3.html',text=translated)
        else:
                texttospeech(translated)
                return render_template('update4.html') 
        
if __name__ == "__main__":
    app.run(debug=True)

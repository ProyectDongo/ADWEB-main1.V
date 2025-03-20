from io import BytesIO
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import base64
import os

app = Flask(__name__)
LIC_STR = '' 
app.secret_key = 'your_secret_key'

# Data storage for display follow up pages
input_data = {}
response_data = {}
response_data_1 = {}
response_data_2 = {}
match_score = {}

def TranslateErrorNumber(ErrorNumber):
    match ErrorNumber:
            # 0 - 999 - Comes from SgFplib.h
            # 1,000 - 9,999 - SGIBioSrv errors 
            # 10,000 - 99,999 license errors
            case 3:
                return "Failure to reach SecuGen Fingerprint Scanner"
        
            case 51:
                return "System file load failure";
            case 52:
                return "Sensor chip initialization failed";
            case 53:
                return "Device not found";
            case 54:
                return "Fingerprint image capture timeout";
            case 55:
                return "No device available";
            case 56:
                return "Driver load failed";
            case 57:
                return "Wrong Image";
            case 58:
                return "Lack of bandwidth";
            case 59:
                return "Device Busy";
            case 60:
                return "Cannot get serial number of the device";
            case 61:
                return "Unsupported device";
            case 63:
                return "SgiBioSrv didn't start; Try image capture again";
            case _:
                return "Unknown error code or Update code to reflect latest result";

@app.route('/')
def home():
    return render_template('home.html')

# First page: Submit predefined data and display image from response
@app.route('/SimpleScan', methods=['GET', 'POST'])
def SimpleScan():
    input_data['SecuGen_Lic'] = LIC_STR
    input_data['Timeout'] = 10000
    input_data['Quality'] = 50
    input_data['Fake_Detect'] = 0
    input_data['TemplateFormat'] = 'ISO'
    input_data['ImageWSQRate'] = '0.75'
    # 5/15/24 -> At this time, only ImageWSQRate only has 2 options:  0.75 or 2.25
    # input_data['ImageWSQRate'] = '2.25'
    input_data['FakeDetect'] = '0'
    return render_template('SimpleScan.html', user_input=input_data)

# Display_Image page: Form to input data, send, and display image from response
@app.route('/Display_Image', methods=['GET', 'POST'])
def DisplayImage():
    ErrorNumber = int(request.form.get('ErrorCode'))
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))

    input_data['Timeout'] = request.form.get('timeout')
    input_data['Quality'] = request.form.get('quality')
    input_data['Fake_Detect'] = request.form.get('fake_detect')
    input_data['TemplateFormat'] = request.form.get('template_format')
    input_data['ImageWSQRate'] = request.form.get('imagewsqrate')

    # Extract data coming from the external API
    response_data['Manufacturer'] = request.form.get('Manufacturer')
    response_data['Model'] = request.form.get('Model')
    response_data['SerialNumber'] = request.form.get('SerialNumber')
    response_data['ImageWidth'] = request.form.get('ImageWidth')
    response_data['ImageHeight'] = request.form.get('ImageHeight')
    response_data['ImageDPI'] = request.form.get('ImageDPI')
    response_data['ImageQuality'] = request.form.get('ImageQuality')
    response_data['NFIQ'] = request.form.get('NFIQ')
    response_data['TemplateBase64'] = request.form.get('TemplateBase64')
    response_data['WSQImageSize'] = request.form.get('WSQImageSize')
    response_data['WSQImage'] = request.form.get('WSQImage')
    response_data['BMPBase64'] = request.form.get('BMPBase64')    
    return render_template('display_image.html', metadata=response_data, user_input=input_data)

# Second page: Form to input data, send, and display image from response
@app.route('/AdvancedScan', methods=['GET', 'POST'])
def AdvancedScan():
    input_data['Display_Input_Params'] = 0
    input_data['SecuGen_Lic'] = LIC_STR
    input_data['ImageWSQRate'] = '2.25'

    return render_template('AdvancedScan.html', user_input=input_data)

# Third page: Multiple actions to submit data and display images
@app.route('/scan1', methods=['GET', 'POST'])
def scan1():
    input_data['SecuGen_Lic'] = LIC_STR
    input_data['Timeout'] = 10000
    input_data['Quality'] = 50
    input_data['TemplateFormat'] = 'ISO'
    input_data['ImageWSQRate'] = '0.75'
    return render_template('scan1.html', user_input=input_data)

@app.route('/scan2', methods=['GET', 'POST'])
def scan2():
    ErrorNumber = int(request.form.get('ErrorCode'))
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    response_data_1['template'] = request.form.get('TemplateBase64')
    response_data_1['BMPBase64'] = request.form.get('BMPBase64')

    return render_template('scan2.html', user_input=input_data, metadata1=response_data_1)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    ErrorNumber = int(request.form.get('ErrorCode'))
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    response_data_2['template'] = request.form.get('TemplateBase64')
    response_data_2['BMPBase64'] = request.form.get('BMPBase64')

    return render_template('compare.html', user_input=input_data, metadata1=response_data_1, metadata2=response_data_2, MatchQuality=100)

@app.route('/matchscore', methods=['GET', 'POST'])
def matchscore():
    ErrorNumber = int(request.form.get('ErrorCode'))
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    match_score['matchingscore'] = int(request.form.get('MatchingScore'))
    match_score['userquality'] = int(request.form.get('userquality'))
    match_message = 'MATCHED. Score is: ' + str(match_score['matchingscore']) if match_score['matchingscore'] > match_score['userquality'] else 'NOT MATCHED. Score is: ' + str(match_score['matchingscore'])
    return render_template('match_score.html', user_input=input_data, metadata1=response_data_1, metadata2=response_data_2, match_score=match_message)

if __name__ == '__main__':
    app.run(debug=True)

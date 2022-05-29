from email import message
from urllib import response
from apps.home import blueprint
from flask import render_template, request, redirect, flash, Response
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound
import os
from apps.home.extractTrxData import extractData


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['pdf']

def handleFile(request):
    if request.method == 'POST':
            if 'files[]' not in request.files:                
                return "Please select a file", 400
            
            files = request.files.getlist('files[]')
            bankname = request.form.get('selectedBank')

            fileList = []
            for file in files:                
                if file.filename == '':                
                    return "Please provide a proper file", 422

                if file and allowed_file(file.filename):
                    fileList.append([secure_filename(file.filename), file])
                else:                
                    return "Extension Not Supported", 422
            response = extractData(fileList, bankname)
            return fileList, 200, response
            # return Response(
            #     response=fileList,
            #     status=200,
            #     headers=response1
            # )
    return

@blueprint.route('/')
def index():

    return render_template('home/index.html', segment='index', pagename='Dashboard', message='')


@blueprint.route('/<template>',methods=['GET','POST'])
def route_template(template):

    try:
        
        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)        
        if segment.endswith('.html'):
            pagename = segment.replace('.html','')
            pagename = 'Dashboard' if pagename == 'index' else pagename.capitalize()            
            print(pagename)
        
        message = handleFile(request)
        print('Url',message)
        return render_template("home/" + template, segment=segment, pagename=pagename, message=message)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


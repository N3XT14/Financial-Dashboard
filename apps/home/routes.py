from email import message
from apps.home import blueprint
from flask import render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['pdf']

def handleFile(request):
    if request.method == 'POST':
            if 'files[]' not in request.files:                
                return "Please select a file", 400
            
            files = request.files.getlist('files[]')

            fileList = []
            for file in files:                
                if file.filename == '':                
                    return "Please provide a proper file", 422

                if file and allowed_file(file.filename):
                    fileList.append(secure_filename(file.filename))
                else:                
                    return "Extension Not Supported", 422
            return fileList, 200
    return

@blueprint.route('/')
def index():

    return render_template('home/index.html', segment='index', pagename='Dashboard', message='')


@blueprint.route('/<template>',methods=['GET','POST'])
def route_template(template):

    try:
        print(request.method)
        

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


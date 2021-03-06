"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename

# Note: that when using Flask-WTF we need to import the Form Class that we created in forms.py
from forms import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if not session.get('logged_in'):
        abort(401)
        

    # Instantiate your form class
    photoForm = UploadForm()
    
    # Validate file upload on submit
    if request.method == 'POST' and photoForm.validate_on_submit():
        
        # Get file data and save to your uploads folder
        photo = photoForm.photo.data   #photo here is variable inwhich we stored file field in forms.py
        #description = photoform.description.data
        
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        flash('File Saved', 'success')
        return redirect(url_for('home'))
    
    flash_errors(photoForm)
    return render_template('upload.html',form = photoForm)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            
            flash('You were logged in', 'success')
            return redirect(url_for('upload'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('home'))

#iterates over the  contents of the app/static/uploads folder and stores the filenames in a python list which the function will return 
def get_uploaded_images():
    
    #Get contents of Current working directory
    rootdir = os.getcwd()
    print rootdir
    filenames = []

    '''
    imagefiles = os.listdir(/app/static/uploads)
    for file in imagefiles:
        name,ext = file.split(".")
        if ext == ("jpg") or ext == ("png") or ext == ("jpeg") or ext == ("JPG") or ext == ("PNG") or ext == ("JPEG") :
            filenames.append(ext)
            '''
            
    #Traversing root directory recursively
    for subdir, dirs, files in os.walk(rootdir + '/app/static/uploads'):
	    for file in files:
	        filenames.append(os.path.join(subdir, file).split('/')[-1])
    return filenames

@app.route('/files')
def files():
    """Render the and lists the image files uploaded in the static/uploads folder as an HTML list (ie. using an unordered or ordered list) of images."""
    
    if not session.get('logged_in'):
        abort(401)
    
    images = get_uploaded_images()
        
    return render_template('files.html', images = images)
    
    
   
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")

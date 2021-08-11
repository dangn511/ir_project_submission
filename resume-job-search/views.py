import os
import time
import resumeparser
import master_file
from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results/', methods=['POST'])
def results():
    uploaded_file = request.files['resume-file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.stream.seek(0)
        resume_text = resumeparser.read_pdf(uploaded_file)
        query_start_time = time.clock()
        search_results = master_file.retrieve_from_query(resume_text)
        query_time = time.clock() - query_start_time
        return render_template('search-results.html', query_time=query_time, search_results=search_results)
    else:
        abort(400)

@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(405)
def not_allowed(error):
    return render_template('405.html'), 405

if __name__ == '__main__':
    app.run(debug=True)

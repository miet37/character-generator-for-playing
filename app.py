
import csv
import os
import json
import random
import time
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from werkzeug.utils import secure_filename

import feedparser # for rss
# --- Configuration ---
# The RSS feed URL for Ars Technica
RSS_URL = 'http://feeds.arstechnica.com/arstechnica/index'
# Limit the display to the last 5 items
ITEM_LIMIT = 5
# ------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import stream_with_context, Response, jsonify
from flask_bootstrap import Bootstrap
from datetime import datetime

# pip install Flask-SQLAlchemy
from model import db, Attendance, upload_students_csv  # import db and Attendance from model.py
from sqlalchemy import text # for explicit sql select

# to suppress cache bootstrap 304
import logging
class Filter304(logging.Filter):
    def filter(self, record):
        # Only log messages that do NOT contain '304'
        return ' 304 ' not in record.getMessage()
#-------------------------------------------------

app = Flask(__name__)

# to suppress cache bootstrap 304
log = logging.getLogger('werkzeug')
log.addFilter(Filter304())
# ----------------------------------

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'Sandstone'
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = 'static/media'
app.config['UPLOAD_FOLDER_DATA'] = 'static/data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = 'mpRec20813'

# SQLite database config ------------------------------------------
# SQLite DB named att_register.db
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///att_register.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# -----------------------------------------------------------------

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}

bootstrap = Bootstrap(app)

# initialize db with app --
db.init_app(app)

# Ensure table creation
with app.app_context():
    db.create_all()
#--------------------------

#--------------------------------------------
from db_browser import bp as db_browser_bp
app.register_blueprint(db_browser_bp)

#--------------------------------------------
from data_browser2 import bp as data_browser_bp
app.register_blueprint(data_browser_bp)

#-------------------------------------------
from blockchain_basic import bc_basic as bc_basic_bp
app.register_blueprint(bc_basic_bp)

#-------------------------------------------
from blockchain_fgindex import bc_fg_bp
app.register_blueprint(bc_fg_bp)

# ------------------------------------------
from recipe_bp import recipe_bp
app.register_blueprint(recipe_bp)

# ------------------------------------------
from recipe_bp2 import recipe_bp2
app.register_blueprint(recipe_bp2)

# ------------------------------------------
from letter_picker import letter_picker_bp
app.register_blueprint(letter_picker_bp)



@app.route('/')
def index():

# rss ----------------------    
    try:
        # Parse the RSS feed
        feed = feedparser.parse(RSS_URL)

        # Get the first N entries (latest items)
        news_items = feed.entries[:ITEM_LIMIT]

    except Exception as e:
        # Simple error handling
        print(f"Error fetching or parsing feed: {e}")
        news_items = []
# ----------------------------
  
    
    return render_template('index.html', 
                           year=datetime.now().year,
                           items=news_items,
                           limit=ITEM_LIMIT
                           )

@app.route('/form3', methods=['GET', 'POST'])
def form3():
    
    if request.method == 'POST':

        # Check if the 'save' action was requested (Zapisz button)
        action = request.form.get('action')
        
        if action == 'save':        

            przedmiot_data_json = request.form.get('przedmiot_data')
            print('przedmiot select-->',przedmiot_data_json)
            try:
                # This 'record' variable will be the full dictionary, e.g.:
                # {'id': 2, 'przedmiot': 'Blockchain ...', 'przedmiot_id': 'E-BADS...'}
                record = json.loads(przedmiot_data_json)
            except (json.JSONDecodeError, TypeError):
                # Fallback in case something goes wrong
                record = {}
    
            # 3. Get all your data from the record and the form
            
            przedmiot = record.get('przedmiot')
            przedmiot_id = record.get('przedmiot_id')
    #        class_id = record.get('id')
            
            
            imie = request.form.get('imie')
            nazwisko = request.form.get('nazwisko')
            numer_albumu = request.form.get('numer_albumu')
            att_date = request.form.get('att_date')
            uwagi = request.form.get('uwagi')
    
            
            
    
            new_entry = Attendance(
                przedmiot = przedmiot,
                przedmiot_id = przedmiot_id,
                imie=imie,
                nazwisko=nazwisko,
                numer_albumu=numer_albumu,
                uwagi=uwagi,
                attdate = att_date
            )
            db.session.add(new_entry)
            db.session.commit()
    
            # Redirect to index
            # return redirect(url_for('index'))
    
            # Redirect to confirmation page, passing form data via URL parameters
            return redirect(url_for('confirm_attendance'))
    
    with db.engine.connect() as conn:
        query = text('SELECT przedmiot, przedmiot_id, id FROM CLASSES order by przedmiot')

        try:
            result = conn.execute(query)            
            # Use mappings() to ensure dict-like rows (avoids tuple indexing errors)
            mappings = result.mappings().all()
            
            rows = [dict(m) for m in mappings]  # ensure plain dicts            
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

    return render_template('form2-bs.html',subjects=rows)

@app.route('/confirm_attendance')
def confirm_attendance():
    imie = request.args.get('imie', '')
    nazwisko = request.args.get('nazwisko', '')
    numer_albumu = request.args.get('numer_albumu', '')
    # uwagi

    return render_template(
        'confirm_attendance.html',
        imie=imie,
        nazwisko=nazwisko,
        numer_albumu=numer_albumu
    )

@app.route('/attendance')
def show_attendance():
    # Query all attendance records
    records = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    mess = 'Attendance.query.order_by'

    # alternative explicit select
    # sql = text("SELECT id, imie, nazwisko, numer_albumu, uwagi, timestamp FROM attendance ORDER BY timestamp DESC")
    # result = db.session.execute(sql)
    # records = result.fetchall()
    # mess = "select ..."

    return render_template('attendance_table.html', records=records, message=mess)


@app.route('/admin/upload_students', methods=['GET', 'POST'])
def admin_upload_students():
    if request.method == 'POST':
        # Get file from form
        file = request.files.get('csv_file')
        if not file:
            flash("No file selected.", "danger")
            return redirect(url_for('admin_upload_students'))

        # Save to temp location
        filename = file.filename
        if not filename.endswith('.csv'):
            flash("Invalid file format. Please upload a CSV file.", "danger")
            return redirect(url_for('admin_upload_students'))

        temp_path = os.path.join(app.config['UPLOAD_FOLDER_DATA'], 'upload_temp.csv')
        os.makedirs(app.config['UPLOAD_FOLDER_DATA'], exist_ok=True)
        file.save(temp_path)


        # Validate CSV structure
        required_columns = [
            "nr_albumu", "nr_karty_bibl", "nazwisko", "imie", "imie2", "email"
        ]
        # Only open/read/check inside the 'with' block
        validation_failed = False
        with open(temp_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            if reader.fieldnames is None or any(col not in reader.fieldnames for col in required_columns):
                validation_failed = True

        # Now that the file is closed, you may safely delete it
        if validation_failed:
            flash(
                f"CSV missing required columns. Required: {', '.join(required_columns)}.",
                "danger"
            )
            os.remove(temp_path)
            return redirect(url_for('admin_upload_students'))

        # If validation passes, upload to DB
        try:
            upload_students_csv(temp_path)
            flash('Students uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error uploading students: {str(e)}', 'danger')
        finally:
            # Remove temp file after everything is done and closed
            os.remove(temp_path)
        return redirect(url_for('admin_upload_students'))

    return render_template('admin_upload_students.html')

# --- live chart ----

random.seed()

@app.route('/live_chart')
def chart_data_page():
    return render_template("live_chart.html")


def generate_random_data():
    """
    Generates random value between 0 and 100
    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.random() * 100,
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(1)

def cpu_util_data():
    """
    Generates random value between 0 and 100
    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.random() * 100,
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(1)

# The yield keyword in Python turns a regular function
# into a generator, which produces a sequence of values
# on demand instead of computing them all at once.

# Python functions don't always have a return statement.
# Generator functions are functions that have the yield keyword
# instead of return.

@app.route("/chart-data")
def chart_data() -> Response:
    response = Response(
        stream_with_context(generate_random_data()),
        mimetype="text/event-stream"
        )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


# -----------------


# Generate a scatter plot and save it
def get_plot():
	data = {
		'a': np.arange(50),
		'c': np.random.randint(0, 50, 50),
		'd': np.random.randn(50)
	}
	data['b'] = data['a'] + 10 * np.random.randn(50)
	data['d'] = np.abs(data['d']) * 100

	plt.figure(figsize=(10, 6))
	plt.scatter(data['a'], data['b'], c=data['c'], s=data['d'])
	plt.xlabel('X label')
	plt.ylabel('Y label')
	plt.colorbar(label='Color scale')

	# Save the figure
	plot_path = os.path.join('static', 'images', 'plot.png')
	os.makedirs(os.path.join('static', 'images'), exist_ok=True)
	plt.savefig(plot_path)
	plt.close()
	return plot_path

# Root URL
@app.get('/mpl_stat_plot')
def single_converter():
	# Generate and save the matplotlib plot
	get_plot()

	return render_template('matplotlib-plot1.html')


# ---------------------------------

@app.route('/chart')
def chart():
    labels = ['1','2','3','4','5','6']
    data = [random.randint(10, 100) for _ in range(6)]       # [10,15,6,17,2,16]
    return render_template('chart.html',data=data, labels=labels)



# upload files
# optional: use existing config value or fallback
DATA_UPLOAD_FOLDER = app.config.get('UPLOAD_FOLDER_DATA', 'static/data')
ALLOWED_DATA_EXT = {'csv', 'txt', 'xlsx', 'json'}

def allowed_data_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DATA_EXT

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check that the POST includes the file part
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)

        file = request.files['file']

        # No file selected
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        # Validate extension
        if not allowed_data_file(file.filename):
            flash('File type not allowed. Allowed: ' + ', '.join(sorted(ALLOWED_DATA_EXT)), 'danger')
            return redirect(request.url)

        # Save file
        filename = secure_filename(file.filename)
        upload_folder = Path(DATA_UPLOAD_FOLDER)
        upload_folder.mkdir(parents=True, exist_ok=True)
        dest = upload_folder / filename
        file.save(str(dest))

        flash(f'File uploaded to {dest.as_posix()}', 'success')
        return redirect(url_for('upload_file'))

    # GET -> render the upload form
    return render_template('upload_form.html')


if __name__ == '__main__':
    app.run(debug=True)

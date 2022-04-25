import json
from email.utils import parseaddr

import ui.utils as utils
from flask import Flask, render_template, make_response, abort, request, \
    redirect, url_for  # noqa: F401
from models.models import Job, ApiKeys
from ui import app, db
from models.models import Job

OMDB_API_KEY = ""


@app.route('/error')
@app.errorhandler(404)
def was_error(e):
    return render_template('error.html', title='error', e=e)


@app.route('/api/v1/', methods=['GET', 'POST'])
def feed_json():
    x = request.args.get('mode')
    crc64 = request.args.get('crc64')
    if x == "s":
        j = utils.search(crc64)
    elif x == "p":
        api_key = request.args.get('api_key')
        title = request.args.get('t')
        year = request.args.get('y')
        video_type = request.args.get('vt')
        imdb = request.args.get('imdb')
        tmdb = request.args.get('tmdb')
        omdb = request.args.get('omdb')
        hasnicetitle = request.args.get('hnt')
        disctype = request.args.get('dt')  # not needed
        label = request.args.get('l')

        j = utils.post(api_key, crc64, title, year, video_type, imdb, tmdb, omdb, hasnicetitle, disctype, label)
    elif x == "rk":
        # we check for post or get to make debugging easier
        if request.method == 'POST':
            email = request.form['email']
        else:
            email = request.args.get('email')
        # Disallow temp emails
        temp_emails = utils.get_burner_email_domains()
        if '@' in parseaddr(email)[1] and email.rsplit('@', 1)[-1] not in temp_emails:
            j = utils.request_key(email)
        else:
            j = {'success': False, 'message': 'email isn\'t valid'}
    elif x == "latest":
        j = utils.get_latest()
    else:
        return {'success': False, 'message': 'nothing here'}

    return app.response_class(response=json.dumps(j, indent=4, sort_keys=True),
                              status=200,
                              mimetype='application/json')


@app.route('/request/key', methods=['GET', 'POST'])
def request_key():
    return render_template('request_key.html')


@app.route('/')
@app.route('/index.html')
@app.route('/index')
def home():
    # app.logger.info('Processing default request')
    # app.logger.debug('DEBUGGING')
    # app.logger.error('ERROR Inside /logreader')
    return render_template('index.html')


@app.route('/fix')
def fix_db():
    # Used to fix bad entries - temp fix
    return {}
    c = db.session.query(Job).order_by(Job.job_id.desc())
    json_return = {}
    i = 0
    for job in c:
        job_json = utils.call_omdb_api(OMDB_API_KEY, job.title, job.year, job.imdb_id)
        if job_json:
            job.disctype = "dvd"
            job.poster_img = job_json['Poster']
            job.video_type = job_json['Type']
            db.session.commit()
        json_return[i] = job_json
        i += 1
    return app.response_class(response=json.dumps(json_return, indent=4, sort_keys=True),
                              status=200,
                              mimetype="application/json")

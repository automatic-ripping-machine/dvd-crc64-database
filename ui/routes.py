import json
import ui.utils as utils
from flask import Flask, render_template, make_response, abort, request, \
    redirect, url_for  # noqa: F401
from ui import app, db
from models.models import Job


@app.route('/error')
@app.errorhandler(404)
def was_error(e):
    return render_template('error.html', title='error', e=e)


@app.route('/api/v1/', methods=['GET', 'POST'])
def feed_json():
    x = request.args.get('mode')
    crc64 = request.args.get('crc64')
    app.logger.debug(crc64)
    if x == "s":
        app.logger.debug("search")
        j = utils.search(crc64)
    else:
        return {'success': False, 'message': 'nothing here'}
    return app.response_class(response=json.dumps(j, indent=4, sort_keys=True),
                              status=200,
                              mimetype='application/json')


@app.route('/')
@app.route('/index.html')
@app.route('/index')
def home():
    # app.logger.info('Processing default request')
    # app.logger.debug('DEBUGGING')
    # app.logger.error('ERROR Inside /logreader')
    return render_template('index.html')

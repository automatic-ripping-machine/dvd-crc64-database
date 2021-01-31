import hashlib
import re
import urllib

from ui import app, db
from models.models import Job, ApiKeys


def search(find_crc):
    """ Queries ARMui db for the movie/show matching the query"""
    new_crc = re.sub('[^a-zA-Z0-9-]', '', find_crc)
    app.logger.debug("search - q=" + str(new_crc))
    posts = db.session.query(Job).filter_by(crc_id=new_crc)
    # posts = Job.query.get(crc_id=new_crc)
    app.logger.debug("search - posts=" + str(posts))
    r = {}
    i = 0
    for p in posts:
        app.logger.debug("job obj = " + str(p.get_d()))
        x = p.get_d().items()
        r[i] = {}
        for key, value in iter(x):
            r[i][str(key)] = str(value)
            app.logger.debug(str(key) + "= " + str(value))
        i += 1
    success = False if i < 1 else True
    return {'success': success, 'mode': 'search', 'results': r}


def post(api_key, crc, title, year, video_type, imdb, tmdb, omdb, hasnicetitle, disctype, label):
    """
    Adds a new entry to the database
    :param api_key: the users api key - Do not let user add data without this!
    :param crc: the crc64 of dvd
    :param title: title of dvd
    :param year:  year of release of dvd
    :param video_type: the video type (movie or series)
    :param imdb: the imdb id for dvd
    :param tmdb: the tmdb id for dvd
    :param omdb: the omdb id for dvd
    :param hasnicetitle: did it have a nice title when it left the users ARM ?
    :param disctype: not needed!
    :param label: the original label for the dvd
    :return:
    """
    # TODO: check for a valid api_key from the table
    if api_key is None or api_key == "":
        return {'success': False, 'mode': 'post', "Error": "Not authorised"}

    valid = db.session.query(ApiKeys).filter_by(key=api_key).first()
    if not bool(valid):
        return {'success': False, 'mode': 'post', "Error": "Not Authorised"}

    # Find any crc matching what the user gave us
    posts = db.session.query(Job).filter_by(crc_id=crc).first()
    if bool(posts):
        return {'success': False, 'mode': 'post', "Error": "DVD with that CRC64 exists"}

    # Make sure we have enough to add to the db
    if crc is None or title is None or year is None:
        return {'success': False, 'mode': 'post', "Error": "Not enough information"}

    job = Job(crc, title, year)
    job.user_id = api_key
    job.video_type = video_type

    job.imdb_id = imdb
    job.tmdb_id = tmdb
    job.omdb_id = omdb

    job.hasnicetitle = hasnicetitle
    job.disctype = disctype
    job.label = label
    job.validated = False
    x = job.get_d()
    app.logger.debug(f" x = {x}")
    db.session.add(job)
    try:
        db.session.commit()
        success = True
    except Exception:
        success = False
    return {'success': success, 'mode': 'search', 'results': x}


def request_key(email):
    # TODO: api_key should be send to the email address
    #  displaying it in browser allows the system to be easily manipulated
    x = hashlib.sha224(email.encode('utf-8')).hexdigest()
    api_key = ApiKeys(x)
    db.session.add(api_key)
    try:
        db.session.commit()
        success = True
    except Exception:
        success = False
    return {'success': success, 'mode': 'Request key', "api_key": x}


def fetch_url(url):
    """Naive URL fetch."""
    fp = urllib.request.urlopen(url)
    s = fp.read().decode("utf8")
    return s


def get_burner_email_domains():
    """Using well maintained list of burner domains.
    This will drop Mailinator etc and all.
    """
    url = "https://raw.githubusercontent.com/wesbos/burner-email-providers/master/emails.txt"
    s = fetch_url(url)
    return s.split('\n')

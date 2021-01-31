import datetime

from ui import db
from prettytable import PrettyTable


class Job(db.Model):
    job_id = db.Column(db.Integer, primary_key=True)
    crc_id = db.Column(db.String(63), unique=True, nullable=False)
    user_id = db.Column(db.String(63))
    date_added = db.Column(db.DateTime)

    no_of_titles = db.Column(db.Integer)
    title = db.Column(db.String(256))
    year = db.Column(db.String(4))
    video_type = db.Column(db.String(20))

    imdb_id = db.Column(db.String(15))
    tmdb_id = db.Column(db.String(15))
    omdb_id = db.Column(db.String(15))

    hasnicetitle = db.Column(db.Boolean)
    disctype = db.Column(db.String(20))  # dvd/bluray/data/music/unknown
    label = db.Column(db.String(256))
    validated = db.Column(db.Boolean)

    def __init__(self, crc, title, year):
        """Return a disc object"""
        self.crc_id = crc
        self.title = title
        self.year = year
        self.hasnicetitle = False
        self.video_type = "unknown"
        self.date_added = datetime.datetime.now()

    def __str__(self):
        """Returns a string of the object"""

        s = self.__class__.__name__ + ": "
        for attr, value in self.__dict__.items():
            s = s + "(" + str(attr) + "=" + str(value) + ") "

        return s

    def pretty_table(self):
        """Returns a string of the prettytable"""
        x = PrettyTable()
        x.field_names = ["Config", "Value"]
        x._max_width = {"Config": 50, "Value": 60}
        for attr, value in self.__dict__.items():
            x.add_row([str(attr), str(value)])
        return str(x.get_string())

    def get_d(self):
        r = {}
        for key, value in self.__dict__.items():
            if '_sa_instance_state' not in key:
                r[str(key)] = str(value)
        return r

    def __repr__(self):
        return '<Job {}>'.format(self.label)

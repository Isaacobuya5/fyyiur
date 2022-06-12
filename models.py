from sqlalchemy import ARRAY, String
from flask_sqlalchemy import SQLAlchemy
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(ARRAY(String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    shows = db.relationship("Show", backref="Venue", lazy="dynamic")



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    shows = db.relationship("Show", backref="Artist", lazy=True)


class Show(db.Model):

    __tablename__ = 'Show'
    id = db.Column(db.Integer,primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String(), nullable=False)

    def detail(self):
        return{
            'venue_id' :self.venue_id,
            'venue_name' :self.Venue.name,
            'artist_id' :self.artist_id,
            'artist_name' :self.Artist.name,
            'artist_image_link' :self.Artist.image_link,
            'start_time' :self.start_time
        }

    def artist_details(self):
        return{
            'artist_id' :self.venue_id,
            'artist_name' :self.Artist.name,
            'artist_image_link' :self.Artist.image_link,
            'start_time' :self.start_time

        }
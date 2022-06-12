#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import ARRAY, String
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from models import db, Venue, Show, Artist
from config import SQLALCHEMY_DATABASE_URI
import os
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
migrate = Migrate(app, db)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  venue_state_city = ''
  data = []
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  try:
  #loop through venues to check for upcoming shows, city, states and venue information
    for venue in venues:
    # fetch the upcoming shows
    #filter(Show.start_time > datetime.now())
      upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
      if venue_state_city == venue.city + venue.state:
          data[len(data) - 1]["venues"].append({
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows) # a count of the number of shows
          })
      else:
        venue_state_city == venue.city + venue.state
        data.append({
          "city":venue.city,
          "state":venue.state,
          "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows)
          }]
        })
  except Exception as e:
    print("Error occurred")
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form['search_term'].get('search_term', '')
    venue_query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
    venue_list_data = list(map(Venue.short, venue_query)) 
    response = {
    "count":len(venue_list_data),
    "data": venue_list_data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  try:
    if venue:
      #venue_details = Venue.detail(venue_query)
      current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      new_shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
      new_show = list(map(Show.artist_details, new_shows_query))
      venue["upcoming_shows"] = new_show
      venue["upcoming_shows_count"] = len(new_show)
      past_shows = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
      past_shows_with_artists = list(map(Show.artist_id, past_shows))
      venue["past_shows"] = past_shows_with_artists
      venue["past_shows_count"] = len(Show.artist_details, past_shows_with_artists)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion


  try:
    new_venue_detail = Venue()
    if 'seeking_talent' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
    new_venue_detail.name=request.form['name']
    new_venue_detail.genres=request.form['genres']
    new_venue_detail.address=request.form['address']
    new_venue_detail.city=request.form['city']
    new_venue_detail.state=request.form['state']
    new_venue_detail.phone=request.form['phone']
    new_venue_detail.website=request.form['website_link']
    new_venue_detail.facebook_link=request.form['facebook_link']
    new_venue_detail.image_link=request.form['image_link']
    new_venue_detail.seeking_talent=seeking_talent
    new_venue_detail.seeking_description=seeking_description
    #insert new venue records into the db
    db.session.add(new_venue_detail)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  artist_search_results = list(map({'id': Artist.id,'name':Artist.name,}, artists)) 
  response = {
    "count":len(artist_search_results),
    "data": artist_search_results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
    artist = Artist.query.get(artist_id)
    if artist:
    #get the current system time
      current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      new_shows_query_results = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
      new_shows_list = list(map({
            'venue_id' : Show.venue_id,
            'venue_name' : Show.Venue.name,
            'venue_image_link' : Show.Venue.image_link,
            'start_time' : Show.start_time        
      }, new_shows_query_results))
      artist["upcoming_shows"] = new_shows_list
      artist["upcoming_shows_count"] = len(new_shows_list)
      past_shows_results = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
      past_shows_list = list(map(Show.venue_details, past_shows_results))
      artist["past_shows"] = past_shows_list
      artist["past_shows_count"] = len(past_shows_list)
  except Exception as e:
    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  try:
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    artist_details = {
            'id':  artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venues,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link,
    }
    if artist:
      form.name.data = artist_details["name"]
      form.genres.data = artist_details["genres"]
      form.city.data = artist_details["city"]
      form.state.data = artist_details["state"]
      form.phone.data = artist_details["phone"]
      form.website_link.data = artist_details["website"]
      form.facebook_link.data = artist_details["facebook_link"]
      form.seeking_venue.data = artist_details["seeking_venue"]
      form.seeking_description.data = artist_details["seeking_description"]
      form.image_link.data = artist_details["image_link"]
      return render_template('forms/edit_artist.html', form=form, artist=artist)
  except Exception as e:
      return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
      artist = Artist.query.get(artist_id)
      if artist:
          if form.validate():
              seeking_venue = False
              seeking_description = ''
              if 'seeking_venue' in request.form:
                  seeking_venue = request.form['seeking_venue'] == 'y'
              if 'seeking_description' in request.form:
                  seeking_description = request.form['seeking_description']
              setattr(artist, 'name', request.form['name'])
              setattr(artist, 'genres', request.form.getlist('genres'))
              setattr(artist, 'city', request.form['city'])
              setattr(artist, 'state', request.form['state'])
              setattr(artist, 'phone', request.form['phone'])
              setattr(artist, 'website', request.form['website_link'])
              setattr(artist, 'facebook_link', request.form['facebook_link'])
              setattr(artist, 'image_link', request.form['image_link'])
              setattr(artist, 'seeking_description', seeking_description)
              setattr(artist, 'seeking_venue', seeking_venue)
              db.session.commit()
              return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:

      return render_template('errors/404.html'), 404

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    print(venue.name)
    if venue:
      venue_details = {
        'id' : venue.id,
        'name' : venue.name,
        'genres' : venue.genres,
        'address' : venue.address,
        'city' : venue.city,
        'state': venue.state,
        'phone' : venue.phone,
        'website' : venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent' : venue.seeking_talent,
        'seeking_description' : venue.seeking_description,
        'image-link' : venue.image_link
      }
      form.name.data = venue_details["name"]
      form.genres.data = venue_details["genres"]
      form.address.data = venue_details["address"]
      form.city.data = venue_details["city"]
      form.state.data = venue_details["state"]
      form.phone.data = venue_details["phone"]
      form.website_link.data = venue_details["website"]
      form.facebook_link.data = venue_details["facebook_link"]
      form.seeking_talent.data = venue_details["seeking_talent"]
      form.seeking_description.data = venue_details["seeking_description"]
      form.image_link.data = venue_details["image-link"]
      # TODO: populate form with values from venue with ID <venue_id>
      return render_template('forms/edit_venue.html', form=form, venue=venue)
  except Exception as e:
    return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    if venue:
        if form.validate():
            seeking_talent = False
            seeking_description = ''
            if 'seeking_talent' in request.form:
                seeking_talent = request.form['seeking_talent'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(venue, 'name', request.form['name'])
            setattr(venue, 'genres', request.form.getlist('genres'))
            setattr(venue, 'address', request.form['address'])
            setattr(venue, 'city', request.form['city'])
            setattr(venue, 'state', request.form['state'])
            setattr(venue, 'phone', request.form['phone'])
            setattr(venue, 'website', request.form['website_link'])
            setattr(venue, 'facebook_link', request.form['facebook_link'])
            setattr(venue, 'image_link', request.form['image_link'])
            setattr(venue, 'seeking_description', seeking_description)
            setattr(venue, 'seeking_talent', seeking_talent)
            db.session.commit()
            return redirect(url_for('show_venue', venue_id=venue_id))
  except Exception as e:
    return render_template('errors/404.html'), 404

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    seeking_venue = False
    seeking_description = ''
    if 'seeking_venue' in request.form:
      seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
      seeking_description = request.form['seeking_description']
    new_artist_details = Artist()
    new_artist_details.name=request.form['name'],
    new_artist_details.genres=request.form['genres'],
    new_artist_details.city=request.form['city'],
    new_artist_details.state= request.form['state'],
    new_artist_details.phone=request.form['phone'],
    new_artist_details.website=request.form['website_link'],
    new_artist_details.image_link=request.form['image_link'],
    new_artist_details.facebook_link=request.form['facebook_link'],
    new_artist_details.seeking_venue=seeking_venue,
    new_artist_details.seeking_description=seeking_description,
    db.session.add(new_artist_details)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed. ')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  try:
    data = []
    shows = Show.query.options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
    data = list(map(Show.detail, shows))
  except Exception as e:
      print("Error occurred")
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
    new_show_details = Show(
      venue_id=request.form['venue_id'],
      artist_id=request.form['artist_id'],
      start_time=request.form['start_time'],
    )
    db.session.add(new_show_details)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occured. Show could not be listed.')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

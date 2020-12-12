#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask_babel import Babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date, datetime, time
import babel
from babel.dates import format_datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database Done 

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    shows = db.relationship('Show', backref="Venue", lazy=True)
    
    
def __repr__(self):
    return f'<Venue {self.id} name: {self.name}>'


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
    shows = db.relationship('Show', backref="Artist", lazy=True)

def __repr__(self):
    return f'<Artist {self.id} name: {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate 

#Done  TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

def __repr__(self):
    return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  --------------------------------------------------------------~--

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  data=[]

  city_state = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for groubBy in city_state:
      venues_list = db.session.query(Venue.id, Venue.name).filter(Venue.city == groubBy[0]).filter(Venue.state == groubBy[1])
      groub={
        "city": groubBy[0],
        "state": groubBy[1],
        "venues": venues_list
      }
      data.append(groub)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
  search_venue = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  #response
  response={
    "count": search_venue.count(),
    "data": search_venue
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id  
  current_venue = Venue.query.filter_by(id=venue_id).first()
  venue_shows = Show.query.filter_by(venue_id=venue_id).all()
  past_show = []
  coming_show = []
  currentTime = datetime.now()

  for show_v in venue_shows:
    add = {
          "artistId": show_v.artist_id,
          "artistName": Artist.query.filter_by(id=show_v.artist_id).first().name,
          "artistImage": Artist.query.filter_by(id=show_v.artist_id).first().image_link,
          "start_time": str(show_v.start_time)
        }
    if show_v.start_time < currentTime:
      past_show.append(add)
    else:
      coming_show.append(add)

  data={
    "id": current_venue.id,
    "name": current_venue.name,
    "address": current_venue.address,
    "city": current_venue.city,
    "state": current_venue.state,
    "phone": current_venue.phone,
    "facebook_link": current_venue.facebook_link,
    "image_link": current_venue.image_link,
    "past_shows": past_show,
    "upcoming_shows": coming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(coming_show)
  }
  return render_template('pages/show_venue.html', venue=data)

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
        Venue_form = VenueForm()

        #create venue
        new_venue = Venue(name=Venue_form.name.data, city=Venue_form.city.data, state=Venue_form.state.data, address=Venue_form.address.data,
                      phone=Venue_form.phone.data,  facebook_link=Venue_form.facebook_link.data, image_link=Venue_form.image_link.data)

        # add a new venue 
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
        db.session.rollback()
        flash('An error occurred. Venue ' +request.form['name'] + ' error  unsuccessfully not listed!')
  finally:
        db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  try:
      deleteVenue = Venue.query.filter_by(id=venue_id).first()
      db.session.delete(deleteVenue)
      db.session.commit()
      flash('The Venue ' + deleteVenue.name + ' deleted')
  except:
      flash('An error occured the Venue ' + deleteVenue.name + ' was not deleted')
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  all_artists = Artist.query.all()
  for each in all_artists:
    add = {
        "id": each.id,
        "name": each.name
    }
    data.append(add)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
  search_artist = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  response={
    "count": search_artist.count(),
    "data": search_artist
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # TODO: replace with real venue data from the venues table, using venue_id
  current_artist = Artist.query.filter_by(id=artist_id).first()
  show_A = Show.query.filter_by(artist_id=artist_id).all()
  past_show = []
  coming_show = []
  current_time = datetime.now()

  # Filter the shows
  for show_a in show_A:
    data = {
          "venue_id": show_a.venue_id,
          "venue_name": show_a.Venue.name,
          "venue_image_link": show_a.Venue.image_link,
          "start_time": str(show_a.start_time)
        }
    if show_a.start_time < current_time:
      past_show.append(data)
    else:
      coming_show.append(data)

  data={
    "id": current_artist.id,
    "name": current_artist.name,
    "genres": current_artist.genres,
    "city": current_artist.city,
    "state": current_artist.state,
    "phone": current_artist.phone,
    "facebook_link": current_artist.facebook_link,
    "image_link": current_artist.image_link,
    "past_shows": past_show,
    "upcoming_shows": coming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(coming_show)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  artist = {
        "id": current_artist.id,
        "name": current_artist.name,
        "genres": current_artist.genres,
        "city": current_artist.city,
        "state": current_artist.state,
        "phone": current_artist.phone,
        "facebook_link": current_artist.facebook_link,
        "image_link": current_artist.image_link
    }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  try:
    artist_form = ArtistForm()
    edit_artist = Artist.query.filter_by(id=artist_id).first()
    edit_artist.name = artist_form.name.data
    edit_artist.name = artist_form.name.data
    edit_artist.phone = artist_form.phone.data
    edit_artist.state = artist_form.state.data
    edit_artist.city = artist_form.city.data
    edit_artist.genres = artist_form.genres.data
    edit_artist.image_link = artist_form.image_link.data
    edit_artist.facebook_link = artist_form.facebook_link.data
    
    db.session.commit()
    flash('The Artist ' + request.form['name'] + ' has been successfully updated!')
  except:
    db.session.rolback()
    flash('An Error has occured n Error has occured and the edit not submission')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  venue={
    "id": venue_form.id,
    "name": venue_form.name,
    "address": venue_form.address,
    "city": venue_form.city,
    "state": venue_form.state,
    "phone": venue_form.phone,
    "facebook_link": venue_form.facebook_link,
    "image_link": venue_form.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    venue_form = VenueForm()
    current_venue = Venue.query.filter_by(id=venue_id).first()
    current_venue.name = venue_form.name.data
    current_venue.city = venue_form.city.data
    current_venue.state = venue_form.state.data
    current_venue.address = venue_form.address.data
    current_venue.phone = venue_form.phone.data
    current_venue.facebook_link = venue_form.facebook_link.data
    current_venue.image_link = venue_form.image_link.data
    db.session.commit()
    flash('The Venue ' + request.form['name'] + ' has been successfully updated!')
  except:
    db.session.rollback()
    flash('An Error has occured and the edit not submission ')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist_form = ArtistForm()
    artist = Artist(name=artist_form.name.data, city=artist_form.city.data, state=artist_form.state.data, phone=artist_form.phone.data, genres=artist_form.genres.data, 
                    image_link=artist_form.image_link.data, facebook_link=artist_form.facebook_link.data)
    
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred the Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows_join = db.session.query(Show).join(Artist).join(Venue).all()

  for each in shows_join: 
      show= {
       "venue_id": each.venue_id,
       "venue_name": each.Venue.name,
       "artist_id": each.artist_id,
       "artist_name": each.Artist.name, 
       "artist_image_link": each.Artist.image_link,
       "start_time": str(each.start_time)
      }
      data.append(show)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show_form = ShowForm()
  try:
    new_show = Show(artist_id=show_form.artist_id.data, venue_id=show_form.venue_id.data,start_time=show_form.start_time.data)

    db.session.add(new_show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

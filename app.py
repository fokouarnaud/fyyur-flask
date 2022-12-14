#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
from re import A
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from models import setup_db, Show, Artist, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db= setup_db(app)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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

def num_upcoming_shows(venue):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    return {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > current_time).count()
    }


@app.route('/venues')
def venues():

    data = []
    city_state_items = Venue.query.with_entities(
        Venue.city, Venue.state).all()

    for city_state in city_state_items:
        state = city_state.state
        city = city_state.city
        city_state_venues = Venue.query.filter_by(
            state=state).filter_by(city=city).all()

        city_state_venues_map = list(
            map(num_upcoming_shows, city_state_venues))
        data.append({
            "city": city,
            "state": state,
            "venues": city_state_venues_map
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    tag = request.form.get('search_term', '')
    search_term = "%{}%".format(tag)
    venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
    count = Venue.query.filter(Venue.name.ilike(search_term)).count()

    venues_map = list(map(num_upcoming_shows, venues))
    response = {
        "count": count,
        "data": venues_map
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    upcoming_shows_data = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.start_time >= datetime.now()).all()

    upcoming_shows = list(map(map_shows_venue, upcoming_shows_data))

    past_shows_data = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    past_shows = list(map(map_shows_venue, past_shows_data))

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": json.loads(venue.genres),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


def map_shows_venue(show):
    return {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    body = {}   
    try:

        genres = json.dumps(request.form.getlist('genres'))
        dataForm = request.form.to_dict()

        venue = Venue(name=dataForm['name'],
                      city=dataForm['city'],
                      state=dataForm['state'],
                      address=dataForm['address'],
                      phone=dataForm['phone'],
                      image_link=dataForm['image_link'],
                      facebook_link=dataForm['facebook_link'],
                      genres=genres,
                      website=dataForm['website_link'],
                      seeking_description=dataForm['seeking_description'],
                      seeking_talent=True if request.form.get(
                          "seeking_talent") else False
                      )
        print(venue)
        db.session.add(venue)
        db.session.commit()

        body['id'] = venue.id
        body['name'] = venue.name

    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    else:

        flash('Venue ' + body['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    venue = Venue.query.get(venue_id)
    shows = Show.query.filter(Show.venue_id == venue.id).all()

    error = False
    body = {
        'success': False,
        'name': venue.name
    }

    try:
        for show in shows:
            db.session.delete(show)
        db.session.delete(venue)
        db.session.commit()
        body['success'] = True
        body['url_home'] = url_for('index')
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + body['name'] + ' was successfully removed!')
        return jsonify(body)


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    tag = request.form.get('search_term', '')
    search_term = "%{}%".format(tag)
    artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
    count = len(artists)
    response = {
        "count": count,
        "data": artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)

   

    upcoming_shows_data = Show.query.filter(
        Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()

    upcoming_shows = list(map(map_shows_artist, upcoming_shows_data))

   

    past_shows_data = Show.query.filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    past_shows = list(map(map_shows_artist, past_shows_data))

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": json.loads(artist.genres),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)


def map_shows_artist(show):
    return {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.genres.data = artist.genres
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.image_link = request.form.get('image_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website')
        artist.genres = json.dumps(request.form.getlist('genres'))
        artist.seeking_venue = request.form.get('seeking_venue')
        artist.seeking_description = request.form.get('seeking_description')
        artist.seeking_venue = True if artist.seeking_venue == 'y' else False

        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. could not be update.')
    else:

        flash('Artist Details Updated Successfully')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.genres.data = venue.genres
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.image_link = request.form.get('image_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website')
        venue.genres = json.dumps(request.form.getlist('genres'))
        venue.seeking_talent = request.form.get('seeking_talent')
        venue.seeking_description = request.form.get('seeking_description')
        venue.seeking_talent = True if venue.seeking_talent == 'y' else False

        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. could not be update.')
    else:

        flash('Artist Details Updated Successfully')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    body = {}
    try:

        genres = json.dumps(request.form.getlist('genres'))
        dataForm = request.form.to_dict()

        artist = Artist(name=dataForm['name'],
                        city=dataForm['city'],
                        state=dataForm['state'],
                        phone=dataForm['phone'],
                        image_link=dataForm['image_link'],
                        facebook_link=dataForm['facebook_link'],
                        genres=genres,
                        website=dataForm['website_link'],
                        seeking_description=dataForm['seeking_description'],
                        seeking_venue=True if request.form.get(
            "seeking_venue") else False
        )

        db.session.add(artist)
        db.session.commit()

        body['id'] = artist.id
        body['name'] = artist.name

    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()
    if error:

        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    else:

        flash('Artist ' + body['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    shows = Show.query.all()
    data = list(map(map_shows, shows))

    return render_template('pages/shows.html', shows=data)


def map_shows(show):
    return {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link":  show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False

    try:

        dataForm = request.form.to_dict()
        start_time = dataForm['start_time']

        artist = Artist.query.get(dataForm['artist_id'])
        show = Show(start_time=start_time)
        venue = Venue.query.get(dataForm['venue_id'])
        show.artist_id = artist.id
        show.venue_id = venue.id
        show.venue = venue

        artist.venues.append(show)
        db.session.commit()

    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

from app import db


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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String)
    website = db.Column(db.String)
    seeking_description = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    artists = db.relationship("Show", back_populates="venue")

    def __repr__(self):
        return f'''
      <Venue {self.id},
      {self.name} ,
      {self.city} ,
      {self.state} ,
      {self.address} ,
      {self.phone} ,
      {self.image_link} ,
      {self.facebook_link} ,
      {self.genres} ,
      {self.website} ,
      {self.seeking_description} ,
      {self.seeking_talent}
      >'''


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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    venues = db.relationship("Show", back_populates="artist")

    def __repr__(self):
        return f'''
      <Artist {self.id},
      {self.name} ,
      {self.city} ,
      {self.state} ,
      {self.phone} ,
      {self.image_link} ,
      {self.facebook_link} ,
      {self.genres} ,
      {self.website} ,
      {self.seeking_description} ,
      {self.seeking_venue}
      >'''

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    venue_id = db.Column(db.ForeignKey(
        'Venue.id'), primary_key=True)
    artist_id = db.Column(db.ForeignKey(
        'Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship("Venue", back_populates="artists")
    artist = db.relationship("Artist", back_populates="venues")

    def __repr__(self):
        return f'''
      <Show {self.venue_id},
      {self.artist_id} ,
      {self.start_time} ,
      {self.venue} ,
      {self.artist} 
      >'''

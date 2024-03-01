from flask import Flask, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
import json 
import time
import base64
from io import BytesIO
from datetime import datetime
from sqlalchemy import func

cur_dir = os.path.abspath(os.path.dirname(_file_))
app = Flask(_name_)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(cur_dir, "Music_Streaming.db")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Albums(db.Model): 
    tablename="albums"    
    album_id = db.Column(db.String, primary_key=True)
    album_name = db.Column(db.String(50), nullable=False,unique=True)
    album_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    image_blob=db.Column(db.BLOB,nullable=False,unique=True)
    album_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    artist = db.Column(db.String)
    songs_in = db.relationship("Songs",backref="album")

class Playlists(db.Model):
    tablename="playlists"
    playlist_id = db.Column(db.String, primary_key=True)
    playlist_name = db.Column(db.String(50), nullable=False)
    playlist_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    songs_in = db.relationship("Songs",secondary="playlist_songs",backref="song_playlists")

class Playlist_songs(db.Model):  #Secondary Table
    tablename="playlist_songs"
    song_id=db.Column(db.String,db.ForeignKey("songs.song_id"),primary_key=True,nullable=False)
    playlist_id=db.Column(db.String,db.ForeignKey("playlists.playlist_id"),primary_key=True,nullable=False)

class Songs(db.Model): 
    tablename="songs"
    song_id = db.Column(db.String, primary_key=True)
    song_name = db.Column(db.String(50), nullable=False,unique=True)
    album_id = db.Column(db.String, db.ForeignKey('albums.album_id'),nullable=False)
    duration=db.Column(db.Integer,nullable=False)
    genre=db.Column(db.String(50),nullable=False)
    lyrics = db.Column(db.String,nullable=False)
    song_views=db.Column(db.Integer,server_default=db.text('0'))
    liked=db.Column(db.Integer,server_default=db.text('0'))
    song_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    music_blob=db.Column(db.BLOB,nullable=False,unique=True)
    # song_img=db.Column(db.BLOB,nullable=False,unique=True)

class Users(db.Model):
    tablename="users"
    user_id = db.Column(db.String,primary_key = True)
    user_name = db.Column(db.String(50),nullable=False,unique=True)
    role= db.Column(db.String(50),nullable=False)
    password = db.Column(db.String,nullable=False)

class User_likes_ratings(db.Model):
    tablename="user_likes_ratings"
    user_id=db.Column(db.String,db.ForeignKey('users.user_id'),primary_key = True,nullable=False)
    song_id=db.Column(db.String,db.ForeignKey('songs.song_id'),primary_key=True,nullable=False)
    song_liked=db.Column(db.Integer,server_default=db.text('0'))
    song_rate=db.Column(db.Float,server_default=db.text('0'))

db.create_all()

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

cur_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(cur_dir, "Music_Streaming.db")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
def gen_uuid():
    return str(uuid.uuid4())

def decodeutf8(value):
    decoded_value = value.decode('utf-8')
    return decoded_value
app.jinja_env.filters['decodeutf8'] = decodeutf8


class Albums(db.Model): 
    _tablename_="albums"    
    album_id = db.Column(db.String, primary_key=True)
    album_name = db.Column(db.String(50), nullable=False,unique=True)
    album_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    image_blob=db.Column(db.BLOB,nullable=False,unique=True)
    album_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    artist = db.Column(db.String)
    songs_in = db.relationship("Songs",backref="album")

class Playlists(db.Model):
    _tablename_="playlists"
    playlist_id = db.Column(db.String, primary_key=True)
    playlist_name = db.Column(db.String(50), nullable=False)
    playlist_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    songs_in = db.relationship("Songs",secondary="playlist_songs",backref="song_playlists")

class Playlist_songs(db.Model):  #Secondary Table
    _tablename_="playlist_songs"
    song_id=db.Column(db.String,db.ForeignKey("songs.song_id"),primary_key=True,nullable=False)
    playlist_id=db.Column(db.String,db.ForeignKey("playlists.playlist_id"),primary_key=True,nullable=False)

class Songs(db.Model): 
    _tablename_="songs"
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
    _tablename_="users"
    user_id = db.Column(db.String,primary_key = True)
    user_name = db.Column(db.String(50),nullable=False,unique=True)
    role= db.Column(db.String(50),nullable=False)
    password = db.Column(db.String,nullable=False)

class User_likes_ratings(db.Model):
    _tablename_="user_likes_ratings"
    user_id=db.Column(db.String,db.ForeignKey('users.user_id'),primary_key = True,nullable=False)
    song_id=db.Column(db.String,db.ForeignKey('songs.song_id'),primary_key=True,nullable=False)
    song_liked=db.Column(db.Integer,server_default=db.text('0'))
    song_rate=db.Column(db.Float,server_default=db.text('0'))


# db.create_all()

# with app.app_context():
#     try:
#         # Insert into Users table
#         user1 =Users(user_id=gen_uuid(), user_name='gurudurohith@gmail.com', role='user', password=generate_password_hash("@Rohith2003",method='pbkdf2:sha256'))
#         db.session.add(user1)

#         # Insert into Albums table
#         album1 = Albums(album_id=gen_uuid(), album_name='Album 1', album_owner_id=user1.user_id)
#         db.session.add(album1)
        

#         # Insert into Songs table
#         song1 = Songs(song_id=gen_uuid(), song_name='Song 1', album=album1, duration=300, genre='Rock')
#         song2 = Songs(song_id=gen_uuid(), song_name='Song 2', album=album1, duration=300, genre='Pop')
#         song3 = Songs(song_id=gen_uuid(), song_name='Song 3', album=album1, duration=300, genre='Classical')
#         db.session.add_all([song1,song2,song3])
        


#         # Insert into Playlists table
#         playlist2 = Playlists(playlist_id=gen_uuid(), playlist_name='Playlist 2', playlist_owner_id=user1.user_id)
#         db.session.add_all([playlist1,playlist2])
        


#         # Insert into Playlist_songs table
#         playlist_song2 = Playlist_songs(song_id=song1.song_id, playlist_id=playlist2.playlist_id)
#         playlist_song3 = Playlist_songs(song_id=song2.song_id, playlist_id=playlist2.playlist_id)
#         playlist_song4 = Playlist_songs(song_id=song3.song_id, playlist_id=playlist1.playlist_id)
#         db.session.add_all([playlist_song1,playlist_song2,playlist_song3,playlist_song4])

#         # Commit the changes to the database
#         db.session.commit()
#     except:
#         db.session.rollback()



















# ALL API USED
@app.route('/rating/<string:song_id>',methods=['POST'])
def rate(song_id):
    rate_value = request.form['stars']
    username = request.cookies.get('username')
    user = Users.query.filter(Users.user_name == username).first()
    U_l_r = User_likes_ratings.query.filter(User_likes_ratings.user_id == user.user_id).first()
    if U_l_r:
        U_l_r.song_rate = rate_value
        db.session.commit()
        return redirect('/')
    else:
        U_l_r = User_likes_ratings(user_id=user.user_id,song_id=song_id,song_rate=rate_value)
        db.session.add(U_l_r)
        db.session.commit()
        return redirect('/')

@app.route('/save_changes/<string:song_id>',methods=['POST'])
def save_songs(song_id):
    if request.method == 'POST':
        song_name = request.form['song-name']
        lyrics = request.form['lyrics']
        duration = request.form['duration']
        song = Songs.query.filter(Songs.song_id == song_id).first()
        song.song_name = song_name
        song.lyrics = lyrics
        song.duration = duration
        db.session.commit()
        return redirect("/creator")
       
@app.route('/deletealbum/<string:album_id>')
def delet_album(album_id):
    album_c = Albums.query.filter(Albums.album_id == album_id)
    album = album_c.first()
    songs = Songs.query.filter(Songs.album_id == album.album_id).all()
    for song in songs:
        playlists = Playlist_songs.query.filter(Playlist_songs.song_id == song.song_id)
        if len(playlists.all()) != 0:
            playlists.delete()
        Songs.query.filter(Songs.song_id == song.song_id).delete()
    album_c.delete()
    db.session.commit()
    return "200"

@app.route('/delete_song/<string:song_id>')
def delete_song(song_id):
    playlists = Playlist_songs.query.filter(Playlist_songs.song_id == song_id)
    try:
        if len(playlists.all()) != 0:
            playlists.delete()
        Songs.query.filter(Songs.song_id == song_id).delete()
        db.session.commit()
        return "200"
    except:
        db.session.rollback()
        return "403"    

@app.route("/add_song_queue/<string:song_name>")
def add_song_queue(song_name):
    song = Songs.query.filter(Songs.song_name == song_name).first()
    album = Albums.query.filter(Albums.album_id == song.album_id).first()
    song.song_views += 1
    db.session.commit() 
    song_to_send =  dict()
    song_to_send['name'] = song_name
    song_to_send['lyrics'] = song.lyrics
    song_to_send['artist'] = album.artist
    song_to_send['duration'] = song.duration
    song_to_send['img'] = str(song.album.image_blob.decode('utf-8', 'ignore'))
    song_to_send['song'] = str(song.music_blob.decode('utf-8', 'ignore'))
    return json.dumps(song_to_send)

@app.route('/newplaylist/<string:playlist_name>')
def newplaylist(playlist_name):
    user = Users.query.filter(Users.user_name ==request.cookies.get("username")).first()
    playlist = Playlists(playlist_id=gen_uuid(), playlist_name=playlist_name, playlist_owner_id=user.user_id)
    try:
        db.session.add(playlist)
        db.session.commit()
    except:
        db.session.rollback()
        return "403"
    return "200"

@app.route('/addplaylist/<string:playlist_name>/<string:song_name>')
def playlist(playlist_name,song_name):
    playlist_id = Playlists.query.filter(Playlists.playlist_name == playlist_name).first().playlist_id
    song = Songs.query.filter(Songs.song_name == song_name).first()
    playlist_song = Playlist_songs(song_id=song.song_id, playlist_id=playlist_id)
    try:
        db.session.add(playlist_song)
        db.session.commit()
    except:
        db.session.rollback()
        return "403"
    return "200"

@app.route('/getnames',methods=['GET'])
def getname():
    trend = Songs.query.order_by(Songs.song_views.desc()).limit(4)
    songs = [[song.song_id, song.song_name] for song in Songs.query.all()]
    trend = [[song.song_id, song.song_name] for song in trend]
    albums = [[album.album_id, album.album_name] for album in Albums.query.all()]
    return json.dumps({'songs': songs, 'albums': albums,'trend':trend})

@app.route('/album_details/<string:album_name>',methods=['GET'])
def find_album(album_name):
    album = Albums.query.filter(Albums.album_name == album_name).first()
    songs = Songs.query.filter(Songs.album_id == album.album_id).all()
    songs_list = []
    for song in songs:
        song_to_send =  dict()
        song_to_send['name'] = song.song_name
        song_to_send['lyrics'] = song.lyrics
        song_to_send['artist'] = album.artist
        song_to_send['duration'] = song.duration
        song_to_send['img'] = str(song.album.image_blob.decode('utf-8', 'ignore'))
        song_to_send['song'] = str(song.music_blob.decode('utf-8', 'ignore'))
        songs_list.append(song_to_send)
    return json.dumps({'songs':songs_list})











# ALL ROUTES USED 
@app.route('/song/<string:song_id>',methods=['GET'])
def showsong(song_id):
    if request.method == 'GET':
        song = Songs.query.filter(Songs.song_id==song_id).first()
        user = Users.query.filter(Users.user_id == song.album.album_owner_id).first()
        return render_template('songs.html',song=song,username=user.user_name)

@app.route('/album/<string:album_id>',methods=['GET'])
def showalbum(album_id):
    if request.method == 'GET':
        album = Albums.query.filter(Albums.album_id==album_id).first()
        songs = Songs.query.filter(Songs.album_id == album_id).all()
        user = Users.query.filter(Users.user_id == album.album_owner_id).first()
        data = dict()
        data['name'] = album.album_name
        data['artist'] = user.user_name
        data['count'] = len(songs)
        data['songs'] = list()
        for song in songs:
            temp = dict()
            temp['name'] = song.song_name
            temp['duration'] = time.strftime("%M:%S", time.gmtime(song.duration))
            temp['genre'] = song.genre
            temp['views'] = song.song_views
            temp['author'] = song.album.artist
            data['songs'].append(temp)
        return render_template("album.html",username=request.cookies.get('username'),album=data,image_blob=album.image_blob)    


@app.route('/playlist/<string:playlist_id>')
def playlist1(playlist_id):
    plist = Playlist_songs.query.filter(Playlist_songs.playlist_id == playlist_id).all()
    plist_name = Playlists.query.filter(Playlists.playlist_id == playlist_id).first().playlist_name
    plist_owner = Users.query.filter(Users.user_id == Playlists.query.filter(Playlists.playlist_id == playlist_id).first().playlist_owner_id).first()
    data = dict()
    data['name'] = plist_name
    data['artist'] = plist_owner.user_name
    data['count'] = len(plist)
    data['songs'] = list()
    for i in plist:
        temp = dict()
        song_details = Songs.query.filter(Songs.song_id == i.song_id).all()
        for j in song_details:
            temp['name'] = j.song_name
            temp['duration'] = time.strftime("%M:%S", time.gmtime(j.duration))
            temp['genre'] = j.genre
            temp['views'] = j.song_views
            author = Users.query.filter(Users.user_id == Albums.query.filter(Albums.album_id == j.album_id).first().album_owner_id).first().user_name
            temp['author'] = author
            data['songs'].append(temp)
    return render_template("playlist.html",username=request.cookies.get('username'),album=data)    

@app.route('/admin/allcreator',methods=['GET'])
def allalbum():
    users = Users.query.filter(Users.role == 'creator')
    all_users_data = {'count': users.count(), 'users': list()}
    for user in users.all():
        user_data = {'name': user.user_name, 'albums': {'count': 0, 'album': list()}}
        albums = Albums.query.filter(Albums.album_owner_id == user.user_id).order_by(Albums.album_name.asc()).all()
        user_data['albums']['count'] = len(albums)
        for album in albums:
            songs = Songs.query.filter(Songs.album_id == album.album_id).order_by(Songs.song_name.asc()).all()
            album_data = { 'id':album.album_id,'name': album.album_name, 'songs': {'count':len(songs),'song':list()}}
            for song in songs:
                song_data = {
                    'name': song.song_name,
                    'views': song.song_views,
                    'duration': song.duration,
                    'genre': song.genre,
                    'liked': song.liked,
                    'lyrics': song.lyrics,
                    'id':song.song_id
                }
                album_data['songs']['song'].append(song_data)
            user_data['albums']['album'].append(album_data)
        all_users_data['users'].append(user_data)
    return render_template('admin_file.html',all_users_data = all_users_data,username=request.cookies.get('username'))

@app.route('/admin/view',methods=['GET'])
def admin_view():
    if request.method == 'GET':
        user_name = request.cookies.get("username")
        user = Users.query.filter(Users.user_name==user_name).first()
        if user == None or user.role != 'admin':
            return redirect("/admin")
        else:
            user = Users.query
            tu = user.filter(Users.role != "admin").count()
            tc = user.filter(Users.role == "creator").count()
            ts = Songs.query.count()
            ta = Albums.query.count()
            return render_template("admin.index.html",tu = tu,tc = tc,ts = ts,ta = ta,username = request.cookies.get("username"))
        
@app.route("/admin",methods=['GET','POST'])
@app.route("/admin/signin",methods=['GET','POST'])
def admin_signin():
    if request.method == 'GET':
        return render_template("admin.signin.html")
    else:
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name==user_name).first()
        if user == None:
            return redirect('/signin')
        if user.role == 'admin':
            if check_password_hash(user.password,password):
                response = make_response(redirect("/admin/view"))
                response.set_cookie("loggedIn", "1")
                response.set_cookie("role", "user")
                response.set_cookie("username", user_name)
                return response
            return render_template('admin.signin.html',flag=-3)
        else:
            return redirect('/signin')

@app.route("/uploadsongs/<string:album_name>",methods=['POST','GET'])
def songs(album_name):
    if request.method == 'GET':
        return render_template('upload.html', username=request.cookies.get("username"),upload='song',album_name=album_name)
    if request.method == 'POST':
        musicname = request.form['musicName']
        lyrics = request.form['Lyrics']
        genre = request.form['Genre']
        duration = request.form['Duration']
        music_blob = request.files['music']
        music_bytes_io = BytesIO(music_blob.read())
        data = base64.b64encode(music_bytes_io.getvalue())
        album = Albums.query.filter(Albums.album_name==album_name).first()
        song = Songs(song_id=gen_uuid(), song_name=musicname, album_id=album.album_id, duration=duration, genre=genre, music_blob = data,lyrics=lyrics)
        db.session.add(song)
        db.session.commit()
        return  render_template('redirect.html',href='/creator',data='Operation completed successfully;The song has been added to the album')

@app.route("/uploadalbum",methods=['POST','GET'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html', username=request.cookies.get("username"),upload='album')
    if request.method == 'POST':
        album_name = request.form['albumName']
        publisher = request.form['artist']
        image_blob = request.files['albumFile']
        image_bytes_io = BytesIO(image_blob.read())
        data = base64.b64encode(image_bytes_io.getvalue())
        user = Users.query.filter(Users.user_name==request.cookies.get("username")).first()
        album1 = Albums(album_id=gen_uuid(), album_name=album_name, album_owner_id=user.user_id,artist=publisher,image_blob=data)
        try:
            db.session.add(album1)
            db.session.commit()
        except:
            print("album didnt get added")
            db.session.rollback()
            redirect('/uploadalbum')
        return render_template('redirect.html',href='/creator',data='Operation completed successfully;The album has been added to the collection,Please add songs to your album')

@app.route("/creator")
def creator():
    user = Users.query.filter(Users.user_name==request.cookies.get("username")).first()
    if user.role == 'user':
        return render_template("creator.html",username=request.cookies.get("username"),registered = -1)
    albums = Albums.query.filter(Albums.album_owner_id==user.user_id).all() 
    if len(albums) == 0:
        return render_template("creator.html",username=request.cookies.get("username"),registered = 0)
    details = dict()
    details['songcount'] = 0
    details['popular'] = ""
    details['maxviews'] = 0
    details['totalviews'] = 0
    details['averagelikes'] = 0
    temp_albums = dict()
    temp_albums['count'] = len(albums)
    temp_albums['albums'] = list()
    for album in albums:
        temp_dict = dict()
        temp_dict['album_name'] = album.album_name
        temp_dict['songs'] = dict()
        temp_dict['songs']['song'] = list()
        songs = Songs.query.filter(Songs.album_id==album.album_id)
        temp_dict['songs']['count'] = songs.count()
        for song in songs:
            temp_dect_songs = dict()
            temp_dect_songs['lyrics'] = song.lyrics
            temp_dect_songs['duration'] = song.duration

            temp_dect_songs['id'] = song.song_id
            temp_dect_songs['songname'] = song.song_name
            temp_dect_songs['liked'] = song.liked
            temp_dect_songs['views'] = song.song_views
            if details["maxviews"]<=song.song_views:
                details['maxviews'] = song.song_views
                details['popular'] = song.song_name
            details['totalviews'] += song.song_views
            details['songcount'] += 1
            details['averagelikes']+=song.liked
            temp_dict['songs']['song'].append(temp_dect_songs)
        temp_albums['albums'].append(temp_dict)
    if details['songcount'] > 0:
        details['averagelikes'] /= details['songcount']
    return render_template("creator.html",username=request.cookies.get("username"),registered = 1,details=details,albums=temp_albums)

@app.route("/change_role",methods=['POST'])
def change():
    user = Users.query.filter(Users.user_name==request.cookies.get("username")).first()
    user.role = 'creator'
    db.session.commit()
    return redirect("/creator")

@app.route("/logout", methods=['GET'])
def logout():
    response = make_response(redirect("/"))
    response.set_cookie("loggedIn", "0")
    response.set_cookie("role", "none")
    response.set_cookie("username", "none")
    return response

@app.route("/signin",methods=['GET','POST'])
def signin():
    if request.method == 'GET':
        return render_template("signin.html")
    else:
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name==user_name).first()
        if user == None:
            return render_template('signin.html',flag=-2)
        if check_password_hash(user.password,password):
            response = make_response(redirect("/"))
            response.set_cookie("loggedIn", "1")
            response.set_cookie("role", "user")
            response.set_cookie("username", user_name)
            return response
        else:
            return render_template('signin.html',flag=-3)

@app.route("/signup",methods=['POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name==user_name).first()
        if user == None:
            with app.app_context():    
                try:
                    user1 = Users(user_id=gen_uuid(), user_name=user_name, role='user', password=generate_password_hash(password))
                    db.session.add(user1)
                    db.session.commit()
                except:
                    db.session.rollback()
                    return render_template("signin.html",flag = -1)
            return render_template("signin.html",flag=1)
        else:
            return render_template("signin.html",flag=0)

@app.route("/",methods=['GET'])
@app.route("/index",methods=['GET'])
def index():
    user = Users.query.filter(Users.user_name == request.cookies.get('username')).first()
    songs = Songs.query.order_by(Songs.song_views.desc()).limit(4)
    albums = db.session.query(Albums).join(Songs,Albums.album_id == Songs.album_id).group_by(Albums.album_name).order_by(func.sum(Songs.song_views)).limit(4)
    release_a = Albums.query.order_by(Albums.album_date).limit(2)
    release_s = Songs.query.order_by(Songs.song_date).limit(2)
    top_genre1 = Songs.query.filter(Songs.genre == 'ROCK').order_by(Songs.song_views.desc()).limit(10)
    top_genre2 = Songs.query.filter(Songs.genre == 'POP').order_by(Songs.song_views.desc()).limit(10)
    top_genre3 = Songs.query.filter(Songs.genre == 'ROMANCE').order_by(Songs.song_views.desc()).limit(10)
    top_genre4 = Songs.query.filter(Songs.genre == 'ELECTRO').order_by(Songs.song_views.desc()).limit(10)
    top_genre5 = Songs.query.filter(Songs.genre == 'HIP-HOP').order_by(Songs.song_views.desc()).limit(10)
    top_genre6 = Songs.query.filter(Songs.genre == 'SAD').order_by(Songs.song_views.desc()).limit(10)   
    new_releases = Albums.query.order_by(Albums.album_date).limit(6)
    if user == None:
        return render_template("index.html", username=request.cookies.get("username"),
                               songs=songs,
                               albums=albums,
                               release_a=release_a,
                               release_s=release_s,
                               top_genre1=top_genre1,
                               top_genre2=top_genre2,
                               top_genre3=top_genre3,
                               top_genre4=top_genre4,
                               top_genre5=top_genre5,
                               top_genre6=top_genre6,
                               new_releases = new_releases
                               )
    else:
        playlists = Playlists.query.filter(Playlists.playlist_owner_id == user.user_id).all()
        return render_template("index.html", username=request.cookies.get("username"),
                               songs=songs,
                               albums=albums,
                               release_a=release_a,
                               release_s=release_s,
                               top_genre1=top_genre1,
                               top_genre2=top_genre2,
                               top_genre3=top_genre3,
                               top_genre4=top_genre4,
                               top_genre5=top_genre5,
                               top_genre6=top_genre6,
                               new_releases = new_releases,
                               playlists=playlists)


def main():
    app.run("localhost", debug=True)

if __name__ == "__main__":
    main()
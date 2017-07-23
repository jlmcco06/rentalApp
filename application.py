from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ShopOwner, Piece, Department
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from werkzeug.utils import secure_filename
import os

#Create client for us in login session
CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']

#Allowed file extensions for image uploads
ALLOWED_EXTENTIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

#create file path for uploads folder
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///shoppieces.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/home')
def showHome():
	return render_template('main.html')

@app.route('/departments')
def showDepartments():
	departments = session.query(Department.name).all()
	return render_template('departmentsindex.html', departments=departments)

@app.route('/department/<string:dept_name>')
def showDept(dept_name):
	department = session.query(Department).filter_by(name=dept_name).one()
	inventory = session.query(Piece).filter_by(department=dept_name).all()
	return render_template('department.html', department=department, inventory=inventory)

@app.route('/department/json/<string:dept_name>')
def showDeptJSON(dept_name):
	department = session.query(Department).filter_by(name=dept_name).one()
	inventory = session.query(Piece).filter_by(department=dept_name).all()
	return jsonify(deptInventory= [item.serialize for item in inventory])

@app.route('/shops')
def showShops():
	shops = session.query(ShopOwner).all()
	return render_template('shopsindex.html', shops=shops)

@app.route('/shops/json')
def showShopsJSON():
	shops = session.query(ShopOwner).all()
	return jsonify(allShops=[shop.serialize for shop in shops])

@app.route('/pieces')
def showPieces():
	pieces = session.query(Piece).all()
	return render_template('piecesindex.html', pieces=pieces)

@app.route('/pieces/json')
def showPiecesJSON():
	pieces = session.query(Piece).all()
	return jsonify(allPieces=[piece.serialize for piece in pieces])

@app.route('/shops/<int:shop_id>')
def shopPage(shop_id):
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	inventory = session.query(Piece).filter_by(shop_id=shop_id).all()
	#Only show editable shop page if signed in as shop owner
	if 'username' not in login_session or login_session['username'] != shop.username:
		return render_template('public_shoppage.html', shop=shop, inventory=inventory)
	return render_template('shoppage.html', shop=shop, inventory=inventory)

@app.route('/shops/json/<int:shop_id>')
def shopPageJSON(shop_id):
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	return jsonify(shopInfo=shop.serialize)

@app.route('/pieces/<int:piece_id>')
def piecePage(piece_id):
	piece = session.query(Piece).filter_by(id=piece_id).one()
	shop_id = piece.shop_id
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	#only show editable piece page if user is signed in as shop owner
	if 'username' not in login_session or login_session['username'] != shop.username:
		return render_template('public_piecepage.html', shop=shop, piece=piece)
	return render_template('piecepage.html', shop=shop, piece=piece)

@app.route('/pieces/json/<int:piece_id>')
def piecePageJSON(piece_id):
	piece = session.query(Piece).filter_by(id=piece_id).one()
	return jsonify(pieceInfo = piece.serialize)

def allowed(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

@app.route('/newshop', methods=['GET', 'POST'])
def newShop():
	#Re-soute user to login page if not siged-in.
	if 'username' not in login_session:
		flash('Please login to add a new shop')
		return redirect(url_for('showLogin'))
	if request.method == 'GET':
			return render_template('newshop.html')
	if request.method == 'POST':
		#create new shop object with form informaion
		shop = ShopOwner(name=request.form['shop_name'],
		 	description=request.form['description'], username=login_session['username'], email=request.form['email'])
		session.add(shop)
		session.commit()
		flash('%s has been created!'%request.form['shop_name'])
		name = request.form['shop_name']
		new_id = session.query(ShopOwner).filter_by(name=name).one()
		return redirect(url_for('shopPage', shop_id=new_id.id))

@app.route('/editshop/<int:shop_id>', methods=['GET', 'POST'])
def editShop(shop_id):
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	#Re-route to login page if user not sign-in as shop owner.
	if login_session['username'] != shop.username:
		flash("You must login as this shop's owner in order to edit profile information.")
		return redirect(url_for('showLogin'))
	if request.method == 'GET':
		return render_template('editshop.html', shop=shop)
	if request.form['shop_name'] != shop.name:
		dbnames = session.query(ShopOwner.name).all()
		for name in dbnames:
			if name.name == request.form['shop_name']:
				flash("Username is already in use. Please choose another.")
				return render_template('editshop.html', shop=shop)
	shop.name = request.form['shop_name']
	shop.description = request.form['description']
	shop.email = request.form['email']
	session.commit()
	flash("Shop has been updated")
	return redirect(url_for('shopPage', shop_id=shop_id))

@app.route('/editpiece/<int:piece_id>', methods=['GET', 'POST'])
def editPiece(piece_id):
	piece = session.query(Piece).filter_by(id=piece_id).one()
	shop_id = piece.shop_id
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	#Re-route to login page if user not signed-in as shop owner
	if login_session['username'] != shop.username:
		flash("You must login as this shop's owner in order to edit profile information.")
		return redirect(url_for('showLogin'))
	if request.method == 'GET':
		return render_template('editpiece.html', piece=piece)
	#If user doesn't indicate new department, default to current department
	if 'department' in request.form:
		piece.department = request.form['department']
	# If user doesn't upload a photo, use stock image 'noimage'
	if 'image' not in request.files:
		piece.image = 'noimage.jpg'
	image = request.files['image']
	if image.filename == '':
		piece.image = 'noimage.jpg'
	#if image is present and an allowed file type, add it to the uploads folder and updated database with path
	if image and allowed(image.filename):
		piece.image = 'uploads/' + image.filename
		image.save(os.path.join(UPLOAD_FOLDER, image.filename))
	piece.name = request.form['piece_name']
	piece.quantity = request.form['quantity']
	piece.description = request.form['description']
	session.commit()
	print piece.name, piece.department, piece.image
	flash("Piece profile has been updated")
	return redirect(url_for('piecePage', piece_id=piece_id))

@app.route('/createaccount', methods=['GET', 'POST'])
def newAccount():
	return render_template('create_account.html')

@app.route('/shops/<int:shop_id>/newpiece', methods=['GET', 'POST'])
def newPiece(shop_id):
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	if 'username' not in login_session:
		flash('You must be logged-in as the shopowner to add a piece.')
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		item = Piece(name=request.form['piece_name'], quantity=request.form['quantity'],
			description=request.form['description'], department=request.form['department'], shop_id=shop.id)
		session.add(item)
		session.commit()
		# Add image to uploads folder and file path to database 
		if 'image' not in request.files:
			item.image = 'noimage.jpg'
		image = request.files['image']
		if image.filename == '':
			item.image = 'noimage.jpg'
		if image and allowed(image.filename):
			item.image = 'uploads/' + image.filename
			image.save(os.path.join(UPLOAD_FOLDER, image.filename))	
		flash("Piece profile has been created")
		return redirect(url_for('shopPage', shop_id=shop_id))
	return render_template('newpiece.html', shop=shop)

@app.route('/deleteshop/<int:shop_id>', methods=['GET', 'POST'])
def deleteShop(shop_id):
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	if login_session['username'] != shop.username:
		flash("You must login as this shop's owner in order to edit profile information.")
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(shop)
		session.commit()
		print "shop deleted"
		flash('%s has been closed' % shop.name)
		return redirect(url_for('showShops'))
	return render_template('deleteshop.html', shop=shop)

@app.route('/deletepiece/<int:piece_id>', methods=['GET', 'POST'])
def deletePiece(piece_id):
	piece = session.query(Piece).filter_by(id=piece_id).one()
	shop_id = piece.shop_id
	shop = session.query(ShopOwner).filter_by(id=shop_id).one()
	if login_session['username'] != shop.username:
		flash("You must login as this shop's owner in order to edit profile information.")
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(piece)
		session.commit()
		print "piece deleted"
		flash('%s has been removed' % piece.name)
		return redirect(url_for('shopPage', shop_id=shop_id))
	return render_template('deletepiece.html', piece=piece)

@app.route('/login', methods=['GET', 'POST'])
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	#error message if states do not match
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	auth = request.data
	#Send credentials to facebook to retrieve access token
	app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
	app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
	url = 'https://graph.facebook.com/v2.8/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'% (app_id, app_secret, auth)
	h = httplib2.Http()
	token = h.request(url, 'GET')[1]
	token = json.loads(token)
	token = token['access_token']
	# add access token to URL for facebook access user info retrieval
	url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
	# request user info from facebook
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)
	# Create login-session with facebook user information
	login_session['provider'] = 'facebook'
	login_session['username'] = data["name"]
	login_session['email'] = data["email"]
	login_session['facebook_id'] = data["id"]
	login_session['access_token'] = token

	#Get picture
	url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data["data"]["url"]

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data
	try:
		#	Exchange authorization code for credentials
		oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	#send error message if unable to obtain credentials	
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to obtain credentials.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	#if credentials are obtained, send request to google for access token authentication  
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
	#So access token is valid, but is it the correct one for user? Let's check here:
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps('Token user id does not match given user.'), 401)
		response.headers['Content-Type'] = 'application/json'
		print "token ids do not match"
		return response
	#Is user already logged in?
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	#Store credentials
	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()
	login_session['provider'] = "google"
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	login_session['gplus_id'] = stored_gplus_id
	login_session['credentials'] = stored_credentials

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

@app.route('/myshop')
def userShop():
	if 'username' in login_session:
		try:
			user = login_session['username']
			shop = session.query(ShopOwner).filter_by(username=user).one()
			print user
			print shop
			return redirect(url_for('shopPage', shop_id=shop.id))
		except:
			flash('Your account is not assocaited with any shops')
			return redirect(url_for('showShops'))
	flash('Your account is not assocaited with any shops')
	return redirect(url_for('showShops'))

@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	access_token = login_session['access_token']
	url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
	#send information to facebook to terminate session
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	return "you have been logged out"

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
	print "Login-sesh:"
	print login_session
	if 'provider' in login_session:
		print login_session
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['gplus_id']
			del login_session['credentials']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		flash ("You've been logged out")
		print ' ending Login-sesh:'
		print login_session
		return redirect(url_for('showDepartments'))
	else:
		flash('You actually not logged in anyway...')
		return redirect(url_for('showDepartments'))

@app.route('/createaccount')
def createAccount():
	return render_template('createacct.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
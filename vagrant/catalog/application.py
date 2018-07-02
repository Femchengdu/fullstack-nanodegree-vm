from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

# Import modules for database support
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SkillItem, User


# Imports for the secret login
from flask import session as login_session
import random, string


# Import modules for flow control
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.client import FlowExchangeError
# I think these once will do the trick
import google.oauth2.credentials
import google_auth_oauthlib.flow
import httplib2
import json
from flask import make_response
import requests




	
# Connect to the database and create the database session
engine = create_engine('sqlite:///categoryskillwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def show_fullstack_catalog():
    fs_skills = session.query(Category).all()
    fs_items = session.query(SkillItem).all()
    """ List all catalog categories and first five catelog items """
    return render_template('skills_preview.html', fs_skills = fs_skills, fs_items = fs_items, user_state = login_session)


@app.route('/catalog/<category>/')
def show_fullstack_catalog_items(category):
	""" Show all items for a skill """
	# Search for skills where the category == category
	category =  session.query(Category).filter_by(name = category).one()
	fs_items = session.query(SkillItem).filter_by(category_id = category.id)
	return render_template('skill_items.html', items = fs_items, user_state = login_session)


@app.route('/catalog/<category>/<skill_item>')
def show_fullstack_catalog_item(category, skill_item):
	""" Show detail for a skill item"""
	fs_item =  session.query(SkillItem).filter_by(name = skill_item).one()
	fs_item_desc = fs_item.description
	# Pass the creator object here for display on the page.
	creator = get_user_info(fs_item.user_id)
	#print 'The creator name is %s ' % creator.name
	if 'user_id' in login_session and (login_session['user_id'] == creator.id):
		print 'The login sesssion id is: %d' % login_session['user_id']
		print 'The skill creator is logged in! you may edit or delete this item.'
		return render_template('skill_item.html', item = fs_item, creator_obj = creator, user_state = login_session)
	else:
		print 'You are not the skill creator you are viewing the public page'
		return render_template('public_skill_item.html', item = fs_item, creator_obj = creator, user_state = login_session)

@app.route('/catalog/new', methods=['GET', 'POST'])
def new_fullstack_catalog_item():
	""" Create a skill item"""
	# Check to see if the user is logged in
	if 'username' not in login_session:
		# return the user to the home page where the login link resides
		return redirect('/')
	# Find all category items
	cat_all = session.query(Category).all()
	# Make an options dictionary of arrays from all the cattegories
	options_arr = list(map(lambda x: [x.id, x.name], cat_all))
	if request.method == 'POST':
		new_item = SkillItem(name = request.form['title'], description = request.form['description'], user_id = login_session['user_id'], category_id = request.form['category'])
		session.add(new_item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('new_skill_item.html', categories = options_arr, user_state = login_session)

@app.route('/catalog/<fs_item>/edit', methods=['GET', 'POST'])
def edit_fullstack_catalog_item(fs_item):
	# Check to see if the user is logged in
	""" Edit a skill item"""
	item =  session.query(SkillItem).filter_by(name = fs_item).one()
	#if 'user_id' not in login_session:
	if 'user_id' not in login_session or (login_session['user_id'] != item.user_id):	
		# return the user to the home page and maybe flash a message saying you don't have permission
		return redirect('/')
	# Continue if user passes verification	
	cat_all = session.query(Category).all()
	options_arr = list(map(lambda x: [x.id, x.name], cat_all))
	if request.method == 'POST':
		item.name = request.form['name']
		item.description = request.form['description']
		item.category_id = request.form['category']
		session.add(item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('edit_skill_item.html', skill_item = item, options = options_arr, user_state = login_session)


@app.route('/catalog/<fs_item>/delete', methods=['GET', 'POST'])
def delete_fullstack_catalog_item(fs_item):
	# Check to see if the user is logged in
	
	""" Delete a skill item"""
	item =  session.query(SkillItem).filter_by(name = fs_item).one()
	#if 'user_id' not in login_session:
	if 'user_id' not in login_session or (login_session['user_id'] != item.user_id):	
		# return the user to the home page and maybe flash a message saying you don't have permission
		return redirect('/')
	# If user passes the verification
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('delete_skill_item.html', item=item, user_state = login_session)

# Try out an idea, what the heck
@app.route('/login_link')
def login_link():
	# Create state
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	# Set state in the login_session
	login_session['state'] = state
	# create request url
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secrets.json',
    scopes=['openid', 'email'],
    redirect_uri='http://localhost:8000/gconnect')
	# set the state in the request
	authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
	# redirect to the url with state as parameter included
	return redirect(authorization_url)


@app.route('/gconnect')
def gconnect():
	# What do these lines of code do here? Set up the flow object for exchange of code to token
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secrets.json',
    scopes=['openid', 'email'],
    redirect_uri='http://localhost:8000/gconnect')
    authorization_response = request.args.get("code", "")
    
    #print authorization_response[0]
    #print "The access token is %s" % 
    login_session['access_token'] = flow.fetch_token(code=authorization_response)['access_token']
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': login_session['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Create a user profile
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    if get_user_id(login_session['email']) != None:
    	login_session['user_id'] = get_user_id(login_session['email'])
    	print 'Setting user id from the datbase'
    else:
    	login_session['user_id'] = create_user(login_session)
    	print 'Creating a new user and setting user id from the database'



    # render a template
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output


# Method to confirm if a user is logged in

#Try disconnecting from the server
@app.route('/gdisconnect')
def gdisconnect():
	# Refactor so it does not break the code if  the user isn't logged in (keyError: 'access_token')
	if login_session['access_token']:
		print 'The access token is %s' % login_session['access_token']
		print 'The username is: %s' % login_session['username']
		disconnect_url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
		# Make the http call
		http_obj = httplib2.Http()
		req_result = http_obj.request(disconnect_url, 'GET')[0]
		print 'The request reslut is %s' % req_result
		if req_result['status'] == '200':
			del login_session['user_id']
			del login_session['access_token']
			del login_session['username']
			del login_session['email']
			del login_session['picture']
			response = make_response(json.dumps('You have successfully disconnected.'), 200)
			response.headers['Content-Type'] = 'application/json'
			return response
		else:
			response = make_response(json.dumps('Failed to disconnected.'), 400)
			response.headers['Content-Type'] = 'application/json'
			return response



# Code for the local permissions sysemem

def get_user_id(login_email):
	""" Returns the logged in users user id if they are in the users database"""
	try:
		user = session.query(User).filter_by(email = login_email).one()
		return user.id
	except:
		return None


def get_user_info(user_id):
	""" This returns the user object from the database"""
	user = session.query(User).filter_by(id = user_id).one()
	return user


def create_user(login_session):
	"""Create a new user from the login session details"""
	new_user = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
	session.add(new_user)
	session.commit()
	# Query the database for the user just created
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id


if __name__ == '__main__':
	# Add the super secret
	app.secret_key = 'chengdu_ruby_python'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
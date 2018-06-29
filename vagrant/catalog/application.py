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
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']


# New login path with token
@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output

	
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
	return render_template('skills_preview.html', fs_skills = fs_skills, fs_items = fs_items)


@app.route('/catalog/<category>/')
def show_fullstack_catalog_items(category):
	""" Show all items for a skill """
	# Search for skills where the category == category
	fs_items = session.query(SkillItem).all()
	return render_template('skill_items.html', items = fs_items)


@app.route('/catalog/<category>/<skill_item>')
def show_fullstack_catalog_item(category, skill_item):
	""" Show detail for a skill item"""
	fs_item =  session.query(SkillItem).filter_by(name = skill_item).one()
	fs_item_desc = fs_item.description
	return render_template('skill_item.html', item = fs_item_desc)

@app.route('/catalog/new', methods=['GET', 'POST'])
def new_fullstack_catalog_item():
	""" Create a skill item"""
	# Find all category items
	cat_all = session.query(Category).all()
	options_arr = list(map(lambda x: [x.id, x.name], cat_all))
	if request.method == 'POST':
		# User_id 1 hard coded until I impliment the authorization functionality
		new_item = SkillItem(name = request.form['title'], description = request.form['description'], user_id = 1, category_id = request.form['category'])
		session.add(new_item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('new_skill_item.html', categories = options_arr)

@app.route('/catalog/<fs_item>/edit', methods=['GET', 'POST'])
def edit_fullstack_catalog_item(fs_item):
	""" Edit a skill item"""
	item =  session.query(SkillItem).filter_by(name = fs_item).one()
	cat_all = session.query(Category).all()
	options_arr = list(map(lambda x: [x.id, x.name], cat_all))
	if request.method == 'POST':
		item.name = request.form['name']
		item.description = request.form['description']
		item.category_id = request.form['category']
		session.add(item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('edit_skill_item.html', skill_item = item, options = options_arr)


@app.route('/catalog/<fs_item>/delete', methods=['GET', 'POST'])
def delete_fullstack_catalog_item(fs_item):
	""" Delete a skill item"""
	item =  session.query(SkillItem).filter_by(name = fs_item).one()
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		return redirect(url_for('show_fullstack_catalog'))
	return render_template('delete_skill_item.html', item=item)


if __name__ == '__main__':
	# Add the super secret
	app.secret_key = 'chengdu_ruby_python'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
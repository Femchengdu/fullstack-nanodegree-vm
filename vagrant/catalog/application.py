from flask import Flask, render_template, request, redirect, url_for, jsonify


# Import modules for database support
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SkillItem, User


# Imports for the CSRF and login
from flask import session as login_session
import random
import string


# Import modules for flow control
# Google docs and udacity
import google.oauth2.credentials
import google_auth_oauthlib.flow
import httplib2
import json
from flask import make_response
import requests

# To disable ssl check during development
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Connect to the database and create the database session
engine = create_engine('sqlite:///categoryskillwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog/')
def show_fullstack_catalog():
    """ List all catalog categories and first five catelog items """
    # Solve connect thread issue
    session = DBSession()
    fs_categories = session.query(Category).all()
    fs_items = session.query(SkillItem).limit(5)
    return render_template(
        'skills_preview.html',
        categories=fs_categories,
        fs_items=fs_items,
        user_state=login_session)


@app.route('/catalog/<category>/')
def show_fullstack_catalog_items(category):
    """ Show all items for a category """
    # Solve connect thread issue
    session = DBSession()
    category = session.query(Category).filter_by(name=category).one()
    fs_categories = session.query(Category).all()
    fs_items = session.query(SkillItem).filter_by(category_id=category.id)
    return render_template(
        'skill_items.html',
        items=fs_items,
        user_state=login_session,
        item_category=category.name,
        categories=fs_categories
        )


@app.route('/catalog/<category>/<skill_item>')
def show_fullstack_catalog_item(category, skill_item):
    """ Show detail for a skill item"""
    session = DBSession()
    fs_item = session.query(SkillItem).filter_by(name=skill_item).one()
    fs_item_desc = fs_item.description
    fs_categories = session.query(Category).all()
    # Pass the creator object here for display on the page.
    creator = get_user_info(fs_item.user_id)
    if 'user_id' in login_session and (login_session['user_id'] == creator.id):
        return render_template(
            'skill_item.html',
            item=fs_item,
            creator_obj=creator,
            user_state=login_session,
            categories=fs_categories
            )
    else:
        return render_template(
            'public_skill_item.html',
            item=fs_item,
            creator_obj=creator,
            user_state=login_session,
            categories=fs_categories
            )


@app.route('/catalog/new', methods=['GET', 'POST'])
def new_fullstack_catalog_item():
    """ Create a skill item"""
    # Solve connect thread issue
    session = DBSession()
    # Check to see if the user is logged in
    if 'username' not in login_session:
        # return the user to the home page where the login link resides
        return redirect('/')
    # Find all category items
    cat_all = session.query(Category).all()
    # Make an options dictionary of arrays from all the cattegories
    options_arr = list(map(lambda x: [x.id, x.name], cat_all))
    if request.method == 'POST':
        new_item = SkillItem(
            name=request.form['title'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            category_id=request.form['category']
            )
        session.add(new_item)
        session.commit()
        return redirect(url_for('show_fullstack_catalog'))
    return render_template(
        'new_skill_item.html',
        options=options_arr,
        user_state=login_session,
        categories=cat_all
        )


@app.route('/catalog/<fs_item>/edit', methods=['GET', 'POST'])
def edit_fullstack_catalog_item(fs_item):
    """ Edit a skill item"""
    # Solve connect thread issue
    session = DBSession()
    item = session.query(SkillItem).filter_by(name=fs_item).one()
    # Check to see if the user is logged in.
    if 'user_id' not in login_session or (
            login_session['user_id'] != item.user_id):
        # return the user to the home page.
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
    return render_template(
        'edit_skill_item.html',
        skill_item=item,
        options=options_arr,
        user_state=login_session,
        categories=cat_all)


@app.route('/catalog/<fs_item>/delete', methods=['GET', 'POST'])
def delete_fullstack_catalog_item(fs_item):
    """ Delete a skill item"""
    # Solve connect thread issue
    session = DBSession()
    item = session.query(SkillItem).filter_by(name=fs_item).one()
    cat_all = session.query(Category).all()
    # Check to see if the user is logged in
    if 'user_id' not in login_session or (
            login_session['user_id'] != item.user_id):
        # return the user to the home page.
        return redirect('/')
    # If user passes the verification
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_fullstack_catalog'))
    return render_template(
        'delete_skill_item.html',
        item=item,
        user_state=login_session,
        categories=cat_all)


# Use a Login route instead of Javascript :-) don't know enough javascript yet.
@app.route('/login_link')
def login_link():
    # Create state
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    # Set state in the login_session
    login_session['state'] = state
    # create request url
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['openid', 'email'],
        redirect_uri='http://localhost:8000/gconnect')
    # set the state in the request
    authorization_url, state = flow.authorization_url(
        access_type='offline', state=state, include_granted_scopes='true')
    # redirect to the url with state as parameter included
    return redirect(authorization_url)


@app.route('/gconnect')
def gconnect():
    """Callback route from google after authorization/authentication"""
    # Solve connect thread issue
    session = DBSession()
    # Check to see if the state token match
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "Everything matches here thanks"
    # Set the state variable for use in the flow object
    state2 = login_session['state']
    # Set up the flow object for exchange of access code to token
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['openid', 'email'],
        redirect_uri='http://localhost:8000/gconnect',
        state=state2)
    # Capure the url of the callback request from google
    authorization_response = request.url
    # Change to match google docs
    flow.fetch_token(authorization_response=authorization_response)
    # set the credentials from the flow into a variable
    # which has the following keys I only use of of them though
    # (token, refresh_token, token_uri, client_id, client_secret and scopes)
    credentials = flow.credentials
    # Get the access token as per the google docs example
    login_session['access_token'] = credentials.token
    # Hybrid into udacity method
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': login_session['access_token'], 'alt': 'json'}
    # Use the access toke to request the users data
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # Create a user profile
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    if get_user_id(login_session['email']) is not None:
        login_session['user_id'] = get_user_id(login_session['email'])
        print 'Setting user id from the datbase'
    else:
        login_session['user_id'] = create_user(login_session)
        print 'Creating a new user and setting user id from the database'
    print "done!"
    return redirect(url_for('show_fullstack_catalog'))


# Disconnecting from the server
@app.route('/gdisconnect')
def gdisconnect():
    """This method enables the user to logout and revoke the access token"""
    if login_session['access_token']:
        # Construct the URL to revoke the access token
        disconnect_url = '''
        https://accounts.google.com/o/oauth2/revoke?token=%s
        ''' % login_session['access_token']
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
            # Maybe throw in a flash message here more user friendly
            return redirect(url_for('show_fullstack_catalog'))
        else:
            response = make_response(json.dumps(
                'Failed to disconnected.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response


# Code for the local permissions sysemem
def get_user_id(login_email):
    """Returns the logged in users user id if they are in the users database"""
    try:
        user = session.query(User).filter_by(email=login_email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    """ This returns the user object from the database"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def create_user(login_session):
    """Create a new user from the login session details"""
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    # Query the database for the user just created
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Two JSON endpoints are listed below with their supporting methods
@app.route('/catalog/<category>/<skill_item>/json/')
def api_item(category, skill_item):
    # Solve connect thread issue
    session = DBSession()
    return get_skill_item(skill_item)


# Get items by category
@app.route('/catalog/<category>/json/')
def api_category(category):
    # Solve connect thread issue
    session = DBSession()
    return get_category_items(category)


# Get a skill item
def get_skill_item(item_name):
    """Method to get and serialize the skill item"""
    session = DBSession()
    skill = session.query(SkillItem).filter_by(
        name=item_name.replace('-', ' ')).one()
    return jsonify(skill.serialize)


# Get a category and item
def get_category_items(category):
    """Method to serialize the result category and skill."""
    session = DBSession()
    category_item = session.query(Category).filter_by(
        name=category.replace('-', ' ')).one()
    skill_items = session.query(SkillItem).filter_by(
        category_id=category_item.id).all()
    return jsonify(
        category=[category_item.serialize],
        skills=[item.serialize for item in skill_items])


if __name__ == '__main__':
    # Add the super secret
    app.secret_key = 'chengdu_ruby_python'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

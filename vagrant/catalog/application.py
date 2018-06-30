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
    # Set things up for the login link
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secrets.json',
    scopes=['openid', 'email'],
    redirect_uri='http://localhost:8000/gconnect')
    #flow.redirect_uri = 'http://localhost:8000/gconnect'
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    #return '<a href="%s">link text</a>' % authorization_url
    fs_skills = session.query(Category).all()
    fs_items = session.query(SkillItem).all()
    """ List all catalog categories and first five catelog items """
    return render_template('skills_preview.html', fs_skills = fs_skills, fs_items = fs_items, login_link = authorization_url)


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


@app.route('/gconnect')
def gconnect():
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

    # reder a template
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


if __name__ == '__main__':
	# Add the super secret
	app.secret_key = 'chengdu_ruby_python'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
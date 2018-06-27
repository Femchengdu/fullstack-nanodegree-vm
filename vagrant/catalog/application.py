from flask import Flask
from flask import render_template
app = Flask(__name__)

# Import modules for database support
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SkillItem, User

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
	fs_item =  {'name':'Ruby on Rails','description':'Web framework from Ruby', 'category':'Framework','id':'2'}
	fs_item_desc = fs_item['description']
	return render_template('skill_item.html', item = fs_item_desc)

@app.route('/catalog/<user>/<fs_skill>/<fs_item>/new')
def new_fullstack_catalog_item(user, fs_item, fs_skill):
	""" Create a skill item"""
	return render_template('new_skill_item.html', category = fs_skill, user = user)

@app.route('/catalog/<user>/<fs_skill>/<fs_item>/edit')
def edit_fullstack_catalog_item(user, fs_skill, fs_item):
	""" Edit a skill item"""
	fs_item =  {'name':'CSS','description':'Styled with css','category' :'Frontend'}
	return render_template('edit_skill_item.html', category = fs_skill, fs_item = fs_item)


@app.route('/catalog/<user>/<fs_skill>/<fs_item>/delete')
def delete_fullstack_catalog_item(user, fs_skill, fs_item):
	""" Delete a skill item"""
	return render_template('delete_skill_item.html', category = fs_skill, user = user)


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
from flask import Flask
from flask import render_template
app = Flask(__name__)



@app.route('/')
@app.route('/catalog')
def show_fullstack_catalog():
	fs_skills = [{'name': 'Back End', 'id': '1'}, {'name':'Front End', 'id':'2'}, {'name':'APIs', 'id':'3'}, {'name':'Frameworks', 'id':'4'}]
	fs_items = [ {'name':'Python', 'description':'Object oriented with lots of libraries','category' :'Back End', 'id':'1'}, {'name':'Ruby on Rails','description':'Web framework from Ruby', 'category':'Framework','id':'2'},{'name':'Flask', 'description':'Web framework with python', 'category':'Framework','id':'3'},{'name':'CSS', 'description':'Frontend styles', 'category':'Front End','id':'4'},{'name':'Ruby', 'description':'Object oriented programing language', 'category':'Back End','id':'5'} ]
	""" List all catalog categories and first five catelog items """
	return render_template('skills_preview.html', fs_skills = fs_skills, fs_items = fs_items)


@app.route('/catalog/category/fs_skill/')
def show_fullstack_catalog_items():
	""" Show all items for a skill """
	fs_items = [{'name':'Ruby on Rails','description':'Web framework from Ruby', 'category':'Framework','id':'2'},{'name':'Flask', 'description':'Web framework with python', 'category':'Framework','id':'3'}]
	return render_template('skill_items.html', items = fs_items)


@app.route('/catalog/<fs_skill>/<fs_item>')
def show_fullstack_catalog_item(fs_skill, fs_item):
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
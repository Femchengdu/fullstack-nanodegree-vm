from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, SkillItem, User

engine = create_engine('sqlite:///categoryskillwithusers.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
User1 = User(name="chengdu_ruby_python", email="femiajayi705@gmail.com")
session.add(User1)
session.commit()

print 'Added User 1'
# Add 5 Core categories
category1 = Category(name="Programming")

session.add(category1)
session.commit()

print 'Added Category 1'
category2 = Category(name="Developer Tools")

session.add(category2)
session.commit()
print 'Added Category 2'
category3 = Category(name="Backend")

session.add(category3)
session.commit()
print 'Added Category 3'

category4 = Category(name="Frontend")

session.add(category4)
session.commit()
print 'Added Category 4'
category5 = Category(name="Linux Server")

session.add(category5)
session.commit()
print 'Added Category5'
skillItem1 = SkillItem(
    user_id=1,
    name="JavaScript",
    description="Frontend JavaScript functionality",
    category=category4)
session.add(skillItem1)
session.commit()

print 'Added Skill Item to the Database'

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    @property
    def serialize(self):
        """This returns a category in a serialzed format"""
        return {
                'id': self.id,
                'name': self.name
                }


class SkillItem(Base):
    __tablename__ = 'skill_item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """This will return skill item data in a serialized format"""
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'category': self.category.name,
                'creator': self.user.name
                }


engine = create_engine('sqlite:///categoryskillwithusers.db')


Base.metadata.create_all(engine)

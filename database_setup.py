from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False,unique=True)



class Item(Base):
    __tablename__ = 'item'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    price = Column(Integer)
    description = Column(String(1000))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'category'     : self.category_id,
           'description'  : self.description,
           'user'         : self.user_id
       }
 

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.create_all(engine)

import os 
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class ShopOwner(Base):
	__tablename__= 'shop'

	id = Column( Integer, primary_key=True)
	name = Column( String(100), nullable=False)
	description = Column( String(500))
	email = Column( String(100))
	username = Column( String(100))
	#Serialize DB info for json use
	@property
	def serialize(self):
			return{

			'id' : self.id,
			'name' : self.name,
			'description' : self.description,
			'email' : self.email,
			'username' : self.username

			}

class Piece(Base):
	__tablename__ = 'piece'

	id = Column(Integer, primary_key=True)
	name = Column(String(300), nullable=False)
	quantity = Column(Integer, nullable = False)
	description = Column(String(500))
	department = Column(String(300), nullable=False)
	image = Column(String)
	shop_id = Column(Integer, ForeignKey('shop.id'))
	shop = relationship(ShopOwner) 
	#Serialize DB info for json use
	@property
	def serialize(self):
		return{

			'id' : self.id,
			'name' : self.name,
			'quantity' : self.quantity,
			'description' : self.description,
			'department' : self.department,
			'image' : self.image,
			'shop_id' : self.shop_id
		}

class Department(Base):
	__tablename__ = 'dept'

	name = Column( String(100), nullable=False, primary_key=True)
	piece_match = Column(String(300), ForeignKey('piece.department'))
	match = relationship(Piece)
	#Serialize DB info for json use
	@property
	def serialize(self):
	   return {
	   	'name' : self.name,
	   	'piece_match' : self.piece_match
	   }


engine = create_engine('sqlite:///shoppieces.db')
Base.metadata.create_all(engine)
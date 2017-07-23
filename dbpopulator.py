import os 
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, ShopOwner, Piece, Department

engine = create_engine('sqlite:///shoppieces.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Add categories to database 

seating = Department(name= 'Seating')
session.add(seating)

tables = Department(name= 'Tables')
session.add(tables)

storage = Department(name= 'Storage')
session.add(storage)

textiles = Department(name= 'Textiles')
session.add(textiles)

art = Department(name= 'Art')
session.add(art)

props = Department(name= 'Props')
session.add(props)

lighting = Department(name= 'Lighting')
session.add(lighting)
session.commit()

#add example shops and pieces

shop1 = ShopOwner(
	description="We're two friends with too much stuff for our home, but when we can't fit you benefit!\r\nWe have an eclectic assortment of mostly mid-century stuff.", 
	email= "Mike@betsuhome.com", 
	name= "Betsu", 
	username= "Joshua Mccollum")
session.add(shop1)

shop2 = ShopOwner(
	description= "Trash-cat Lifestyle brand.",
	email= "chirpo@gato.com", 
	name= "Chirpo's", 
	username= "Josh Mccollum")
session.add(shop2)

piece1= Piece(
	department= "Art", 
	description= "Tapestry/wall hanging is both easy on the eyes and soft to the touch. ", 
	image= "uploads/il_fullxfull.1242998895_fduq.jpg", 
	name= "South American Tapestry", 
	quantity= 1, 
	shop_id= 1)
session.add(piece1)

piece2 = Piece(
	department= "Props", 
	description= "Mid-century champagne glasses.",
	image= "uploads/il_fullxfull.1262276557_pfe9.jpg",
	name= "Champagne glasses",
	quantity= 5, 
	shop_id= 1)
session.add(piece2)

piece3 = Piece(
	department= "Lighting", 
	description= "Cool hanging lamp", 
	image= "uploads/il_fullxfull.1118518046_q1yk.jpg", 
	name= "Hanging lamp", 
	quantity= 1, 
	shop_id= 1)
session.add(piece3)

piece4 = Piece( 
	department= "Lighting", 
	description= "Cool hanging lamp", 
	image= "uploads/il_fullxfull.1118518046_q1yk.jpg", 
	name= "Hanging lamp",
	quantity= 1, 
	shop_id= 1)
session.add(piece4)

piece5 = Piece( 
	department= "Seating", 
	description= "Orange velour chair with brass casters. ", 
	image= "uploads/il_fullxfull.1143960526_d5ba.jpg", 
	name= "Orange Chair",
	quantity= 1, 
	shop_id= 1)
session.add(piece5)

piece6 = Piece(
	department= "Seating",
	description= "Mesh cylinder for sitting.",
	image= "uploads/images-1.jpeg",
	name= "Cylindrical Chair ", 
	quantity= 1, 
	shop_id= 2)
session.add(piece6)

piece7= Piece( 
	department= "Seating", 
	description= "Large cube for sitting or sleeping.",
	image= "uploads/Unknown.jpeg",
	name= "Cube chair",
	quantity= 1, 
	shop_id= 2)
session.add(piece7)

piece8= Piece( 
	department= "Storage",
	description= "Enclosed unit with vent. Great for storing unwanted guests, or yourself when you need some alone time. ", 
	image= "uploads/images.jpeg", 
	name= "Isolation chamber", 
	quantity= 1, 
	shop_id= 2)
session.add(piece8)

piece9 = Piece( 
	department= "Art", 
	description= "Vintage print of IBM game. This is a collector's dream, never framed.", 
	image= "uploads/Unknown.png", 
	name= "Vintage Alley-Cat print",
	quantity= 1,
	shop_id= 2)
session.add(piece9)

session.commit()
print "Departments and test data Added!"
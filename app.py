from flask import Flask, render_template,jsonify,redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
import scrape_mars
import config 
import logging # imported for logging
from datetime import datetime

# create logger with 'mars_application'
logger = logging.getLogger('mars_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('mars.log')
fh.setLevel(logging.DEBUG)
# add the handlers to the logger
logger.addHandler(fh)

# app=Flask(__name__, )
app = Flask(__name__, template_folder='templates')
conn = 'mongodb://localhost:27017'
mongo = MongoClient(conn)
# mongo = PyMongo(app)
@app.route("/")
def index():
		try:
			logger.info("invoked default route at : "+ str(datetime.now()))
			mars = mongo.db.mars.find_one()
			# except e as exception:
		except Exception as ex:
			logger.info(ex)
			# print("exception hi")
		return render_template("index.html", mars=mars)
	

@app.route("/scrape")
def mars_scrape():
	try:
		logger.info("invoked new scrape route at : "+ str(datetime.now()))
		mars = mongo.db.mars
		mars_data = scrape_mars.scrape()
		mars.update(
			{},
			mars_data,
			upsert = True
			)
	except Exception as ex:
			logger.info(ex)	
	return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
	app.run(debug = config.debug)
	app.config['TEMPLATES_AUTO_RELOAD'] = True 
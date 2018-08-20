from flask import Flask, render_template,jsonify,redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
import scrape_mars

# app=Flask(__name__, )
app = Flask(__name__, template_folder='templates')
conn = 'mongodb://localhost:27017'
mongo = MongoClient(conn)
# mongo = PyMongo(app)
@app.route("/")
def index():
	mars = mongo.db.mars.find_one()
	return render_template("index.html", mars=mars)

@app.route("/scrape")
def mars_scrape():
	mars = mongo.db.mars
	mars_data = scrape_mars.scrape()
	mars.update(
		{},
		mars_data,
		upsert = True
		)
	return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
	app.run(debug = True)
	app.config['TEMPLATES_AUTO_RELOAD'] = True 
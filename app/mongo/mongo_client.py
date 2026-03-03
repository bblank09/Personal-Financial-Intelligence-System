from pymongo import MongoClient
from flask import g, current_app

def init_mongo(app):
    app.config['MONGO_CLIENT'] = MongoClient(app.config['MONGO_URI'])

def get_db():
    if 'mongo_db' not in g:
        client = current_app.config['MONGO_CLIENT']
        g.mongo_db = client.get_default_database()
    return g.mongo_db

def get_collection(name):
    db = get_db()
    return db[name]

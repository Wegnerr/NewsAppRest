from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo


app = Flask(__name__)
api = Api(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)
parser = reqparse.RequestParser()
parser.add_argument('text')


class Articles(Resource):
    def get(self):
        artics = mongo.db.artics.find({})
        articles = []
        for art in artics:
            articles.append(art["text"])
        return articles

    def post(self):
        args = parser.parse_args()
        id = mongo.db.artics.count() + 1
        mongo.db.artics.insert({"id": id, "text": args['text']})
        return 200


class Categories(Resource):
    def get(self):
        pass


class Publishers(Resource):
    def get(self):
        pass


class Feed(Resource):
    def get(self):
        pass


class Picked(Resource):
    def get(self):
        pass


class Blocked(Resource):
    def get(self):
        pass


class Users(Resource):
    def get(self):
        users = mongo.db.users.find({})
        return users

    def post(self, u_name, u_pick):
        pass

api.add_resource(Articles, '/articles')
api.add_resource(Users, '/users')
api.add_resource(Categories, '/users')
api.add_resource(Feed, '/users')
api.add_resource(Picked, '/users')
api.add_resource(Blocked, '/users')


if __name__ == '__main__':
    app.run(debug=True)

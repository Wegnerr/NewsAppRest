from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo


app = Flask(__name__)
api = Api(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)
parser = reqparse.RequestParser()
parser.add_argument('text')
parser.add_argument('category')
parser.add_argument('u_name')
parser.add_argument('art_sn')


def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(404)
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj


class Articles(Resource):
    def get(self):
        artics = mongo.db.artics.find({})
        articles = []
        for art in artics:
            print(art)
            articles.append(art["text"])
        return get_paginated_list(articles, '/articles',
                                  start=request.args.get('start', 1),
                                  limit=request.args.get('limit', 5))

    def post(self):
        args = parser.parse_args()
        sn = mongo.db.artics.count() + 1
        print(args)
        mongo.db.artics.insert_one(
            {"sn": sn, "text": args['text'], "category": args['category']})
        return 200


class Article(Resource):

    def get(self, art_sn):
        print(art_sn)
        art = None
        for a in mongo.db.artics.find({"sn": int(art_sn)}):
            art = a
        if art is None:
            return 500

        return art["text"]

    def delete(self, art_sn):
        count = mongo.db.artics.remove({"sn": int(art_sn)})
        if count == 1:
            return 200
        else:
            return 500

    def patch(self, art_sn):
        args = parser.parse_args()
        new = {"text": args['text']}
        query = {"sn": int(art_sn)}
        try:
            mongo.db.artics.update_one(query, {"$set": new})
        except:
            return 500
        return 200


class Categories(Resource):
    def get(self):
        arts = mongo.db.artics.find()
        cat = []
        for c in arts:
            print(c)
            print(c['category'])
            if c['category'] not in cat:
                cat.append(c['category'])
        return cat


class Category(Resource):
    def get(self, cat_sn):
        print(cat_sn)
        res = []
        arts = mongo.db.artics.find({"category": cat_sn})
        for a in arts:
            res.append(a['text'])
        return res


class Feed(Resource):
    def get(self, u_sn):
        us = mongo.db.user.find({"sn": int(u_sn)})
        u = [x for x in us]
        res = []
        for c in u[0]["cats"]:
            arts = mongo.db.artics.find({"category": c})
            for a in arts:
                print(a)
                res.append(a["text"])
        return res


class Users(Resource):

    def get(self):
        users = mongo.db.user.find({})
        res = []
        for u in users:
            res.append({"id": u['sn'], "name": u['name']})
        return res

    def post(self):
        args = parser.parse_args()
        sn = mongo.db.user.count() + 1
        mongo.db.user.insert_one(
            {"sn": sn, "name": args['u_name'], "cats": [args['category']], "saved": []})
        return 200


class User(Resource):
    def get(self, u_sn):
        user = mongo.db.user.find({"sn": int(u_sn)})
        for u in user:
            return u['name']

    def patch(self, u_sn):
        args = parser.parse_args()
        new = {"name": args['u_name']}
        query = {"sn": int(u_sn)}
        try:
            mongo.db.user.update_one(query, {"$set": new})
        except:
            return 500
        return 200


class Saved(Resource):
    def get(self, u_sn):
        us = mongo.db.user.find({"sn": int(u_sn)})
        u = [x for x in us]
        res = []
        for c in u[0]["saved"]:
            res.append(c)
        return res

    def patch(self, u_sn):
        args = parser.parse_args()
        query = {"sn": int(u_sn)}
        us = mongo.db.user.find(query)
        u = [x for x in us]
        lists = u[0]["saved"]
        lists.append(args["art_sn"])
        new = {"saved": lists}
        try:
            mongo.db.user.update_one(query, {"$set": new})
        except:
            return 500
        return 200


class Save(Resource):
    def get(self, u_sn, a_sn):
        art = None
        for a in mongo.db.artics.find({"sn": int(a_sn)}):
            art = a
        if art is None:
            return 500

        return art["text"]

    def delete(self, u_sn, a_sn):
        query = {"sn": int(u_sn)}
        us = mongo.db.user.find(query)
        u = [x for x in us]
        lists = u[0]["saved"]
        try:
            lists.remove(a_sn)
            new = {"saved": lists}
            mongo.db.user.update_one(query, {"$set": new})
        except:
            return 500
        return 200


api.add_resource(Articles, '/articles')
api.add_resource(Article, '/articles/<art_sn>')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<u_sn>')
api.add_resource(Feed, '/users/<u_sn>/feed')
api.add_resource(Saved, '/users/<u_sn>/saved')
api.add_resource(Save, '/users/<u_sn>/saved/<a_sn>')
api.add_resource(Categories, '/categories')
api.add_resource(Category, '/categories/<cat_sn>')

if __name__ == '__main__':
    app.run(debug=True)

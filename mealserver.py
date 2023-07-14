import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

NINJA_KEY = 'mmfE72G8/8Hm65WI1MsV0Q==7WiscYr4hdkOfyNh'  # api key


class Dish:
    def __init__(self, json_dish, ID, name):
        self.name = name
        self.ID = ID
        self.cal = 0
        self.size = 0
        self.sodium = 0
        self.sugar = 0
        for dish in json_dish:
            self.cal += dish['calories']
            self.size += dish['serving_size_g']
            self.sodium += dish['sodium_mg']
            self.sugar += dish['sugar_g']

    def __eq__(self, other) -> bool:
        return (
                self.__class__ == other.__class__ and
                self.name == other.name
        )

    def encode(self):
        return self.__dict__


class Meal:
    def __init__(self, name, ID, appetizer, main_dish, dessert):
        self.name = name
        self.ID = ID
        self.appetizer = appetizer
        self.main_dish = main_dish
        self.dessert = dessert
        self.cal = (col.dishes[appetizer].cal + col.dishes[main_dish].cal + col.dishes[dessert].cal)
        self.sugar = (col.dishes[appetizer].sugar + col.dishes[main_dish].sugar + col.dishes[dessert].sugar)
        self.sodium = (col.dishes[appetizer].sodium + col.dishes[main_dish].sodium + col.dishes[dessert].sodium)

    def __eq__(self, other) -> bool:
        return (
                self.__class__ == other.__class__ and
                self.name == other.name
        )

    def encode(self):
        return self.__dict__


class DishCollection:
    def __init__(self):
        self.opNum = 0
        self.dishes = {}  # Dishes in the

    def insert_dish(self, json_dish, name):
        # This function SHOULD CHECK if word already exists and if so return error.
        # Currently, it lets the same word exist with different keys
        dish = Dish(json_dish, self.opNum + 1, name)
        if dish in self.dishes.values():  # word already exists
            return -2  # key = 0 indicates cannot be inserted
        self.opNum += 1
        key = self.opNum
        self.dishes[key] = dish
        return key

    def del_dish(self, key):
        if key in self.dishes.keys():  # the key exists in collection
            dish = self.dishes[key]
            del self.dishes[key]
            return True, dish
        else:
            return False, None  # the key does not exist in the collection

    def find_dish(self, key):
        if key in self.dishes.keys():  # the key exists in collection
            dish = self.dishes[key]
            return True, dish
        else:
            return False, None  # the key does not exist in the collection

    def find_dish_string(self, key):
        for _, dish in self.dishes.items():
            if dish.name == key:
                return True, dish
        return False, None  # the key does not exist in the collection

    def del_dish_string(self, key):
        for ID, dish in self.dishes.items():
            if dish.name == key:
                del self.dishes[ID]
                return True, dish
        return False, None  # the key does not exist in the collection

    def collection_size(self):
        return len(self.dishes)

    # retrieveAll returns all the dictionary containing all words
    def retrieve_all_dishes(self):
        return self.dishes


class MealCollection:
    def __init__(self):
        self.opNum = 0
        self.meals = {}  # Dishes in the

    def insert_meal(self, json_meal, name):
        if not (json_meal['appetizer'] in col.dishes and json_meal['main'] in col.dishes and
                json_meal['dessert'] in col.dishes):
            return -5
        meal = Meal(name, self.opNum + 1, json_meal['appetizer'], json_meal['main'], json_meal['dessert'])
        if meal in self.meals.values():  # word already exists
            return -2  # key = 0 indicates cannot be inserted
        self.opNum += 1
        key = self.opNum
        self.meals[key] = meal
        return key

    def del_meal(self, key):
        if key in self.meals.keys():  # the key exists in collection
            meal = self.meals[key]
            del self.meals[key]
            return True, meal
        else:
            return False, None  # the key does not exist in the collection

    def find_meal(self, key):
        if key in self.meals.keys():  # the key exists in collection
            meal = self.meals[key]
            return True, meal
        else:
            return False, None  # the key does not exist in the collection

    def find_meal_string(self, key):
        for _, meal in self.meals.items():
            if meal.name == key:
                return True, meal
        return False, None  # the key does not exist in the collection

    def del_meal_string(self, key):
        for ID, meal in self.meals.items():
            if meal.name == key:
                del self.meals[ID]
                return True, meal
        return False, None  # the key does not exist in the collection

    # retrieveAll returns all the dictionary containing all words
    def retrieve_all_meals(self):
        return self.meals

    def update_meal(self, json_meal, name, meal_ID):
        if not (json_meal['appetizer'] in col.dishes and json_meal['main'] in col.dishes and
                json_meal['dessert'] in col.dishes):
            return -5
        meal = Meal(name, meal_ID, json_meal['appetizer'], json_meal['main'], json_meal['dessert'])
        self.meals[meal_ID] = meal
        return meal_ID


app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API

col = DishCollection()
meal_col = MealCollection()


class Dishes(Resource):
    global col

    def post(self):
        # get argument being passed in query string
        if not request.is_json:
            return 0, 415
        parser = reqparse.RequestParser()  # initialize parse
        parser.add_argument('name', type=str)
        args = parser.parse_args()  # parse arguments into a dictionary structure
        dish_name = args['name']
        if not bool(dish_name):  # if there is no name
            return -1, 400
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
        response = requests.get(api_url, headers={'X-Api-Key': NINJA_KEY})
        if response.status_code == requests.codes.ok:
            if not (response.json()):
                return -3, 400
            key = col.insert_dish(response.json(), name=dish_name)
        else:
            return -4, 400
        if key == -2:  # word already exists
            return key, 400
        return key, 201

    @staticmethod
    def handle_error(err):
        message = err.data.get('message', None)
        if message:
            return '-1', 400, {'Content-Type': 'text/plain'}

    # GET returns all the words in the collection in json
    def get(self):
        # return jsonify(col.retrieveAllWords())
        # flask will automatically jsonify a dictionary so the above line is not needed
        dishes_json = {k: dish.encode() for k, dish in col.retrieve_all_dishes().items()}
        return dishes_json, 200

    def delete(self):
        return -1, 400


class DishID(Resource):
    global col

    def get(self, key):
        (b, dish) = col.find_dish(key)
        if b:
            return dish.encode(), 200
        else:
            return -5, 404

    def delete(self, key):
        b, dish = col.del_dish(key)
        if b:
            return dish.ID, 200
        else:
            return -5, 404


class DishString(Resource):
    global col

    def get(self, key):
        (b, dish) = col.find_dish_string(key)
        if b:
            return dish.encode(), 200
        else:
            return -5, 404

    def delete(self, key):
        b, dish = col.del_dish_string(key)
        if b:
            return dish.ID, 200
        else:
            return -5, 404


class MealID(Resource):
    global meal_col

    def get(self, key):
        (b, meal) = meal_col.find_meal(key)
        if b:
            return meal.encode(), 200
        else:
            return -5, 404

    def delete(self, key):
        b, meal = meal_col.del_meal(key)
        if b:
            return meal.ID, 200
        else:
            return -5, 404

    def put(self, key):
        if not request.is_json:
            return 0, 415
        parser = reqparse.RequestParser()  # initialize parse
        parser.add_argument('name', type=str)
        parser.add_argument('appetizer', type=int)
        parser.add_argument('main', type=int)
        parser.add_argument('dessert', type=int)
        args = parser.parse_args()  # parse arguments into a dictionary structure
        meal_name = args['name']
        appetizer = args['appetizer']
        main_dish = args['main']
        dessert = args['dessert']
        if not (bool(meal_name) and bool(appetizer) and bool(main_dish) and bool(
                dessert)):  # if there is no name/appetizer/main/dessert
            return -1, 400
        key = meal_col.update_meal(json_meal=args, name=meal_name, meal_ID=key)
        if key == -2:  # meal already exists
            return key, 400
        if key == -5:
            return key, 404
        return key, 200


class MealString(Resource):
    global meal_col

    def get(self, key):
        (b, meal) = meal_col.find_meal_string(key)
        if b:
            return meal.encode(), 200
        else:
            return -5, 404

    def delete(self, key):
        b, meal = meal_col.del_meal_string(key)
        if b:
            return meal.ID, 200
        else:
            return -5, 404


class Meals(Resource):
    global meal_col

    def post(self):
        # get argument being passed in query string
        if not request.is_json:
            return 0, 415
        parser = reqparse.RequestParser()  # initialize parse
        parser.add_argument('name', type=str)
        parser.add_argument('appetizer', type=int)
        parser.add_argument('main', type=int)
        parser.add_argument('dessert', type=int)
        args = parser.parse_args()  # parse arguments into a dictionary structure
        meal_name = args['name']
        appetizer = args['appetizer']
        main_dish = args['main']
        dessert = args['dessert']
        if not (bool(meal_name) and bool(appetizer) and bool(main_dish) and bool(
                dessert)):  # if there is no name/appetizer/main/dessert
            return -1, 400
        key = meal_col.insert_meal(json_meal=args, name=meal_name)
        if key == -2:  # meal already exists
            return key, 400
        if key == -5:
            return key, 404
        return key, 201

    @staticmethod
    def handle_error(err):
        message = err.data.get('message', None)
        if message:
            return '-1', 400, {'Content-Type': 'text/plain'}

    # GET returns all the words in the collection in json
    def get(self):
        # return jsonify(col.retrieveAllWords())
        # flask will automatically jsonify a dictionary so the above line is not needed
        meals_json = {k: meal.encode() for k, meal in meal_col.retrieve_all_meals().items()}
        return meals_json, 200

    def delete(self):
        return -1, 400


api.add_resource(Dishes, '/dishes')
api.add_resource(DishID, '/dishes/<int:key>')
api.add_resource(DishString, '/dishes/<string:key>')
api.add_resource(Meals, '/meals')
api.add_resource(MealID, '/meals/<int:key>')
api.add_resource(MealString, '/meals/<string:key>')

if __name__ == '__main__':
    # create collection dictionary and keys list
    print("running rest-word-svr-v1.py")
    # run Flask app.   default part is 5000
    app.run(host='0.0.0.0', port=8000, debug=True)

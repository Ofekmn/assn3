import requests
import json

orange = 'orange'
spaghetti = 'spaghetti'
apple_pie = 'apple pie'

delicious = 'delicious'

meals_resource = '/meals'
dishes_resource = '/dishes'

dishes_col = {}
meal_col = {}

base_url = 'http://localhost:8000'


def test_dish_creation():
    dishes_list = {orange, spaghetti, apple_pie}
    for dish_name in dishes_list:
        response = requests.post(base_url + dishes_resource, json={"name": dish_name})
        dish_id = int(response.text)
        assert response.status_code == 201
        assert dish_id not in dishes_col
        dishes_col[dish_name] = dish_id


def test_get_dishes_by_id():
    orange_id = dishes_col[orange]
    response = requests.get(f'{base_url}{dishes_resource}/{orange_id}')
    sodium = response.json()['sodium']
    assert response.status_code == 200
    assert 0.9 <= sodium <= 1.1


def test_get_dishes():
    response = requests.get(f'{base_url}{dishes_resource}')
    dishes_json = response.json()
    count = 0
    for dish_json in dishes_json:
        count += 1
        assert is_json(dish_json) is True
    assert count == 3
    assert response.status_code == 200


def test_post_non_existent_dish():
    response = requests.post(base_url + dishes_resource, json={"name": 'blah'})
    response_status = response.status_code
    assert response_status == 400 or response_status == 404 or response_status == 422
    assert response.json() == -3


def test_post_dish_already_in_server():
    response = requests.post(base_url + dishes_resource, json={"name": orange})
    response_status = response.status_code
    assert response_status == 400 or response_status == 404 or response_status == 422
    assert response.json() == -2


def test_meal_creation():
    request_json = {'name': delicious, 'appetizer': dishes_col[orange],
                    'main': dishes_col[spaghetti], 'dessert': dishes_col[apple_pie]}
    response = requests.post(base_url + meals_resource, json=request_json)
    meal_col[delicious] = response.json()
    assert response.json() > 0
    assert response.status_code == 201


def test_get_meals():
    response = requests.get(f'{base_url}{meals_resource}')
    dish = response.json()[str(meal_col[delicious])]
    # for dish in response.json():
    assert 400 <= dish['cal'] <= 500
    assert len(response.json()) == 1
    assert response.status_code == 200


def test_post_meal_already_in_server():
    request_json = {'name': delicious, 'appetizer': dishes_col[orange],
                    'main': dishes_col[spaghetti], 'dessert': dishes_col[apple_pie]}
    response = requests.post(base_url + meals_resource, json=request_json)
    response_status = response.status_code
    assert response_status == 400 or response_status == 422
    assert response.json() == -2


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

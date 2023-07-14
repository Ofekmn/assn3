import requests

base_url = 'http://localhost:8000'
dishes_resource = '/dishes'


def execute_queries(file_name):
    file = open(file_name)
    dish_names = file.read().splitlines()
    for dish_name in dish_names:
        response = requests.post(base_url + dishes_resource, json={"name": dish_name})
        dish_id = int(response.text)
        get_by_id_response = requests.get(f'{base_url}{dishes_resource}/{dish_id}')
        dish = get_by_id_response.json()
        if get_by_id_response.status_code != requests.codes.ok:
            print("ERROR")
        else:
            print(f"{dish_name} contains {dish['cal']} calories, {dish ['sodium']} mgs of sodium, and {dish['sugar']} grams of sugar")
    file.close()

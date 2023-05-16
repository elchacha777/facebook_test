import csv

def get_cities(file_path):
    city_list = []
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            city = row['city']
            state_name = row['state_name']
            if 'St.' in city:
                city = city.replace('St.', 'Saint')
            city_list.append(f'{city}, {state_name}')
    # print(city_list)
    return city_list


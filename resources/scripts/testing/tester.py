import pandas as pd
import requests


csv_file_path = 'csv_file.csv'
data = pd.read_csv(csv_file_path)


for index, row in data.iterrows():
    application_name = row['Application Name']
    category = row['Category']

    url = 'http://localhost:8000/posts/'
    params = {
        'platform': 'mastodon',
        'limit': 100,
        'token': 'TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs',
    }

    payload = {
        'applicationName': application_name,
        'category': category
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, params=params, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Success: {response.json()}")
        else:
            print(f"Error {response.status_code}: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {application_name}: {e}")

import pandas as pd
import requests
import json


def process_requests(csv_file_path):
    data = pd.read_csv(csv_file_path)
    responses = []

    for index, row in data.iterrows():
        application_name = row['Application Name']
        category = row['Category']

        url = 'http://127.0.0.1:8000/posts/'
        params = {
            'platform': 'mastodon',
            'token': 'TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs'
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

            response_text = response.text
            if response.status_code == 200:
                print(f"Success: {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'status': 'Success',
                    'response': response.json()
                })
            else:
                print(f"Error {response.status_code} for {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'status': f"Error {response.status_code}",
                    'response': response_text
                })

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {application_name}: {e}")
            responses.append({
                'application_name': application_name,
                'category': category,
                'status': 'Failed',
                'error': str(e)
            })

    output_file = 'responses.json'
    with open(output_file, 'w') as f:
        json.dump(responses, f, indent=4)

    print(f"Responses saved to {output_file}")


def main():
    csv_file_path = 'ai_applications.csv'
    process_requests(csv_file_path)


if __name__ == '__main__':
    main()

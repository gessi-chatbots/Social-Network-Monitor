import pandas as pd
import requests
import json
import time


def process_requests(csv_file_path):
    data = pd.read_csv(csv_file_path)
    responses = []

    base_url = 'http://127.0.0.1:8000/posts/'

    mastodon_token = 'TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs'
    reddit_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzI2MDM3NDY3LjAxODQ2MiwiaWF0IjoxNzI1OTUxMDY3LjAxODQ2MSwianRpIjoiNEVuaW9QeTdpanRaMThaVElsc2NIVVdTLXlTVEVBIiwiY2lkIjoiYl9BLWZzTHdxRmtMMzcydkdGR1ZFdyIsImxpZCI6InQyX2R2cmJjN2k4dyIsImFpZCI6InQyX2R2cmJjN2k4dyIsImxjYSI6MTY4NzM2MDEzNTU2Mywic2NwIjoiZUp5S1Z0SlNpZ1VFQUFEX193TnpBU2MiLCJmbG8iOjl9.W0_8CkX381LfKl0bO0nGprR_3-Om07eTufXhrY3070QOsrQx-QHSkTK6CH2Dvlysdrmil3W1XGjv5u-FqpTSfpAR6q3ywHjLx9AFkWA3XNK25AjpCcTP7YWMoEBCv_JlrcWhi_TLOgv74sjmQDiHbT4OfpHwn0Z3dhHn1yRarIeKWY1AMXm-F6PU_9VdFcxBU82Ki6LoV3eaiGrcm5zEDuEFdCLmcN-MyFPxWwPRVORlKnzZ5BkaX-teLPUDfBmOAb144Dcnp2ha7s_STfxFnA4Q6ocskUG_xz6G_QLd5h5TBeLqeGnwWweCP4DHNoch_6tL0Nei47slMIITJEfqYg'

    for index, row in data.iterrows():
        application_name = row['Application Name']
        category = row['Category']

        # Payload to be sent with requests
        payload = {
            'applicationName': application_name,
            'category': category
        }

        headers = {
            'Content-Type': 'application/json'
        }

        # Mastodon request
        mastodon_params = {
            'platform': 'mastodon',
            'token': mastodon_token
        }

        try:
            mastodon_response = requests.post(base_url, params=mastodon_params, json=payload, headers=headers)
            mastodon_response_text = mastodon_response.text
            if mastodon_response.status_code == 200:
                print(f"Mastodon Success: {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'platform': 'mastodon',
                    'status': 'Success',
                    'response': mastodon_response.json()
                })
            else:
                print(f"Mastodon Error {mastodon_response.status_code} for {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'platform': 'mastodon',
                    'status': f"Error {mastodon_response.status_code}",
                    'response': mastodon_response_text
                })
        except requests.exceptions.RequestException as e:
            print(f"Mastodon request failed for {application_name}: {e}")
            responses.append({
                'application_name': application_name,
                'category': category,
                'platform': 'mastodon',
                'status': 'Failed',
                'error': str(e)
            })

        # Add a delay between Mastodon and Reddit requests
        time.sleep(5)

        # Reddit request
        reddit_params = {
            'platform': 'reddit',
            'token': reddit_token
        }

        try:
            reddit_response = requests.post(base_url, params=reddit_params, json=payload, headers=headers)
            reddit_response_text = reddit_response.text
            if reddit_response.status_code == 200:
                print(f"Reddit Success: {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'platform': 'reddit',
                    'status': 'Success',
                    'response': reddit_response.json()
                })
            else:
                print(f"Reddit Error {reddit_response.status_code} for {application_name}")
                responses.append({
                    'application_name': application_name,
                    'category': category,
                    'platform': 'reddit',
                    'status': f"Error {reddit_response.status_code}",
                    'response': reddit_response_text
                })
        except requests.exceptions.RequestException as e:
            print(f"Reddit request failed for {application_name}: {e}")
            responses.append({
                'application_name': application_name,
                'category': category,
                'platform': 'reddit',
                'status': 'Failed',
                'error': str(e)
            })

        time.sleep(2)

    output_file = 'platform_responses.json'
    with open(output_file, 'w') as f:
        json.dump(responses, f, indent=4)

    print(f"Responses saved to {output_file}")


def main():
    csv_file_path = 'ai_applications.csv'
    process_requests(csv_file_path)


if __name__ == '__main__':
    main()

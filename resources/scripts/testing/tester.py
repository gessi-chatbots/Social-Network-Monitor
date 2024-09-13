import pandas as pd
import requests
import time


def send_mastodon_request(base_url, payload, headers, mastodon_token, application_name, category):
    mastodon_params = {
        'platform': 'mastodon',
        'token': mastodon_token
    }

    try:
        mastodon_response = requests.post(base_url, params=mastodon_params, json=payload, headers=headers)
        mastodon_response_text = mastodon_response.text
        if mastodon_response.status_code == 200:
            print(f"Mastodon Success: {application_name}")
            return {
                'application_name': application_name,
                'category': category,
                'platform': 'mastodon',
                'status': 'Success',
                'response': mastodon_response.json()
            }
        else:
            print(f"Mastodon Error {mastodon_response.status_code} for {application_name}")
            return {
                'application_name': application_name,
                'category': category,
                'platform': 'mastodon',
                'status': f"Error {mastodon_response.status_code}",
                'response': mastodon_response_text
            }
    except requests.exceptions.RequestException as e:
        print(f"Mastodon request failed for {application_name}: {e}")
        return {
            'application_name': application_name,
            'category': category,
            'platform': 'mastodon',
            'status': 'Failed',
            'error': str(e)
        }


def send_reddit_request(base_url, payload, headers, reddit_token, application_name, category):
    reddit_params = {
        'platform': 'reddit',
        'token': reddit_token
    }

    try:
        reddit_response = requests.post(base_url, params=reddit_params, json=payload, headers=headers)
        reddit_response_text = reddit_response.text
        if reddit_response.status_code == 200:
            print(f"Reddit Success: {application_name}")
            return {
                'application_name': application_name,
                'category': category,
                'platform': 'reddit',
                'status': 'Success',
                'response': reddit_response.json()
            }
        else:
            print(f"Reddit Error {reddit_response.status_code} for {application_name}")
            return {
                'application_name': application_name,
                'category': category,
                'platform': 'reddit',
                'status': f"Error {reddit_response.status_code}",
                'response': reddit_response_text
            }
    except requests.exceptions.RequestException as e:
        print(f"Reddit request failed for {application_name}: {e}")
        return {
            'application_name': application_name,
            'category': category,
            'platform': 'reddit',
            'status': 'Failed',
            'error': str(e)
        }


def process_requests(csv_file_path):
    data = pd.read_csv(csv_file_path)
    responses = []

    base_url = 'http://127.0.0.1:8000/posts/'

    mastodon_token = 'TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs'
    reddit_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzI2MDM3NDY3LjAxODQ2MiwiaWF0IjoxNzI1OTUxMDY3LjAxODQ2MSwianRpIjoiNEVuaW9QeTdpanRaMThaVElsc2NIVVdTLXlTVEVBIiwiY2lkIjoiYl9BLWZzTHdxRmtMMzcydkdGR1ZFdyIsImxpZCI6InQyX2R2cmJjN2k4dyIsImFpZCI6InQyX2R2cmJjN2k4dyIsImxjYSI6MTY4NzM2MDEzNTU2Mywic2NwIjoiZUp5S1Z0SlNpZ1VFQUFEX193TnpBU2MiLCJmbG8iOjl9.W0_8CkX381LfKl0bO0nGprR_3-Om07eTufXhrY3070QOsrQx-QHSkTK6CH2Dvlysdrmil3W1XGjv5u-FqpTSfpAR6q3ywHjLx9AFkWA3XNK25AjpCcTP7YWMoEBCv_JlrcWhi_TLOgv74sjmQDiHbT4OfpHwn0Z3dhHn1yRarIeKWY1AMXm-F6PU_9VdFcxBU82Ki6LoV3eaiGrcm5zEDuEFdCLmcN-MyFPxWwPRVORlKnzZ5BkaX-teLPUDfBmOAb144Dcnp2ha7s_STfxFnA4Q6ocskUG_xz6G_QLd5h5TBeLqeGnwWweCP4DHNoch_6tL0Nei47slMIITJEfqYg'

    for index, row in data.iterrows():
        application_name = row['Application Name']
        category = row['Category']

        name_variants = [
            application_name,
            application_name.lower(),
            application_name.title(),
            f"#{application_name}"
        ]

        for variant in name_variants:
            payload = {
                'applicationName': variant,
                'category': category
            }

            headers = {
                'Content-Type': 'application/json'
            }

            mastodon_response = send_mastodon_request(base_url, payload, headers, mastodon_token, variant, category)
            responses.append(mastodon_response)

            # time.sleep(2)

            # reddit_response = send_reddit_request(base_url, payload, headers, reddit_token, variant, category)
            # responses.append(reddit_response)

            time.sleep(2)


def main():
    csv_file_path = 'ai_applications.csv'
    process_requests(csv_file_path)


if __name__ == '__main__':
    main()

import requests

def fetch_reddit_posts(subreddit):
    endpoint = f'https://www.reddit.com/r/{subreddit}/new.json'
    headers = {'User-Agent': 'YourAppName'}
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception('Error fetching posts from Reddit')
    return response.json()['data']['children']

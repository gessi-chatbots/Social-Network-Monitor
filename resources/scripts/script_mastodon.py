import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

queries = [
    "AI software", "AI tool", "AI platform", "AI application", "AI software",
    "AI-powered app", "AI product", "AI technology", "AI service", "AI solution",
    "AI analytics", "AI assistant", "AI chatbot", "AI model", "AI system",
    "AI framework", "AI SDK", "AI library", "AI API", "AI development",
    "AI research", "AI innovation"
]

base_url = "https://socialnetworkmonitoring.onrender.com/posts/"
params = {
    "platform": "mastodon",
    "limit": 100,
    "token": "TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs",
    "from": "2024-06-01",
    "to": "2024-06-20"
}

for query in queries:
    params["q"] = query
    response = requests.get(base_url, params=params)
    data = response.json()
    posts = data.get('Posts', [])
    print(f"Query: {query}")
    print(f"Number of posts: {len(posts)}")
    if posts:
        total_length = sum(len(post.get('content', '')) for post in posts)
        avg_length = total_length / len(posts)
        print(f"Average content length: {avg_length}")
    print("------")

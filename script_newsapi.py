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
    "platform": "newsapi",
    "limit": 100,
    "token": "43eff07fdeec4ec985dd9acead442c79",
    "from": "2024-06-01",
    "to": "2024-06-20"
}

for query in queries:
    params["q"] = query
    response = requests.get(base_url, params=params)
    data = response.json()
    articles = data.get('Posts', [])
    print(f"Query: {query}")
    print(f"Number of articles: {len(articles)}")
    if articles:
        total_length = sum(len(article.get('content', '')) for article in articles)
        avg_length = total_length / len(articles)
        print(f"Average content length: {avg_length}")
    print("------")

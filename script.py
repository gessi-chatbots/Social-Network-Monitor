import requests

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
    "token": "TIH_Dvl6-L0F0LvkP634kD48vN0w5dA1mPS3x4zQKJs",
    "from": "2024-06-01",
    "to": "2024-06-19"
}

for query in queries:
    params["q"] = query
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanza una excepción si la respuesta no tiene status 200
        data = response.json()
        print(f"Query: {query}")
        print(f"Number of posts: {len(data.get('Posts', []))}")
        for post in data.get("Posts", []):
            print(f"Content length: {len(post.get('content', ''))}")
            print(f"Post: {post}")
        print("------")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for query '{query}': {e}")

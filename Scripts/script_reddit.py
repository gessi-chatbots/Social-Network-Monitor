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
    "platform": "reddit",
    "limit": 100,
    "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzE4OTMwNDAzLjEyNjcxLCJpYXQiOjE3MTg4NDQwMDMuMTI2NzEsImp0aSI6ImVrN2JzNHhvRVFyanlaY0lKY0xDRnZNeFZXU3IzQSIsImNpZCI6InlyVDB4UThtTHVFU0RTbnJtbHRJU0EiLCJsaWQiOiJ0Ml9udGoyeWF4bCIsImFpZCI6InQyX250ajJ5YXhsIiwibGNhIjoxNjUzODQ4MDc4MDAwLCJzY3AiOiJlSnlLVnRKU2lnVUVBQURfX3dOekFTYyIsImZsbyI6OX0.SpMUqWRxcRYxmgvXOpi0j7PoSXZCaNkf5bTuR9Z6dV6AOeKrLidwTW4ld5qwVRUwf3k54r1YymN4UW3C0AvpRwIFmz9CpdNKDDvTyJsIXx-R-cDk7B4fr2uQauE5RRbJEWWMLS0HD-TIhXyXVtI7PyN1OpF4CGPOyb-TInidY3Zu62M9YUtGptgaRj0frBmcpt7MRRvjX09nJiltxrvYUZjE9J_1e40plRZSqWlu94MRlJ_3mGgAArOW8xTznkSaSoQsdUXrxOZeKj0G1FQBTf_y33WnZmzyQT8qVETid1I3Ve_4rR6TqULHpQnEo_VU3yRMGPE2P_Mk3AgU6rlWIg",
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
        total_length = sum(len(post.get('selftext', '') or post.get('title', '')) for post in posts)
        avg_length = total_length / len(posts)
        print(f"Average content length: {avg_length}")
    print("------")

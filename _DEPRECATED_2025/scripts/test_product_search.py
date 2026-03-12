import requests

def test_search(query):
    print(f"Searching for '{query}'...")
    try:
        response = requests.get(f'http://localhost:8000/productos/?search={query}')
        data = response.json()
        print(f"Found {len(data)} results.")
        for p in data[:3]:
            print(f"- {p['nombre']} (ID: {p['id']})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("Surgibac")
    test_search("Cofia")
    test_search("NonExistentProduct")

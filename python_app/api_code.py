import requests

def get_cat_fact():
    url = "https://meowfacts.herokuapp.com/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the response is bad
        data = response.json()
        
        fact = data.get("data", ["No fact found"])[0]
        print("Cat Fact:", fact)
    
    except requests.exceptions.RequestException as e:
        print("Error fetching data from API:", e)

if __name__ == "__main__":
    get_cat_fact()

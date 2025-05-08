import requests

def get_pokemon_data():
    url = 'https://pokemmoprices.com/api/v2/items/table?names=true'
    return requests.get(url)

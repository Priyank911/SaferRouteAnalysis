from flask import Flask, request, jsonify,render_template
import requests
import math

app = Flask(__name__)

AZURE_MAPS_KEY = 'EFfSwSvslsiSQ4NZuFLYN8BY5mc3KVgqCUV0yehE9uRJngU0PVpvJQQJ99AHACYeBjFmFs5tAAAgAZMP6Xlf'

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/shops_nearby', methods=['GET'])
def shops_nearby():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    
    url = f"https://atlas.microsoft.com/search/poi/json?subscription-key={AZURE_MAPS_KEY}&api-version=1.0&query=shop&limit=100&lat={lat}&lon={lon}&radius=3000"
    response = requests.get(url)
    data = response.json()
    
    shops = []
    for result in data['results']:
        shops.append({
            'name': result['poi']['name'],
            'lat': result['position']['lat'],
            'lon': result['position']['lon'],
            'category': result['poi']['categories'][0] if 'categories' in result['poi'] else 'Unknown'
        })
    

    safe_zone_score = calculate_safe_zone_score(shops)
    safer_zone = 1 if safe_zone_score >= 70 else 0
    
    return jsonify({'shops': shops, 'safe_zone': safer_zone})

def calculate_safe_zone_score(shops):
    if len(shops) > 50:
        return 80  
    elif len(shops) > 20:
        return 70
    elif len(shops) > 5:
        return 60
    else:
        return 50  

if __name__ == '__main__':
    app.run(debug=True)

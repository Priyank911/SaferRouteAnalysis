from flask import Flask, request, jsonify, render_template
from geopy.geocoders import Nominatim
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  

@app.route('/')
def home():
    return render_template('index.html')

geolocator = Nominatim(user_agent="safety_zone_locator")

shop_data = {
    'name': ['Shop A', 'Shop B', 'Shop C', 'Shop D', 'Shop E'],
    'lat': [28.7041, 28.7045, 28.7050, 28.7035, 22.29479619433163],
    'lon': [77.1025, 77.1030, 77.1040, 77.1015, 73.39059381499291],
    'open_hours': [10, 9, 12, 8, 10]  
}

df = pd.DataFrame(shop_data)
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)


gdf['safe_zone'] = [1, 1, 0, 1, 0]

X = gdf[['lat', 'lon', 'open_hours']]
y = gdf['safe_zone']


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

@app.route('/safer_zone', methods=['GET'])
def safer_zone():
   
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({'error': 'Please provide both latitude and longitude.'}), 400

    user_location = Point(lon, lat)


    gdf['distance'] = gdf['geometry'].distance(user_location)
    nearby_shops = gdf[gdf['distance'] <= 0.01]  

    if nearby_shops.empty:
        return jsonify({
            'location': {'lat': lat, 'lon': lon},
            'message': 'No nearby shops found within 3 km radius.',
            'nearby_shops': []
        })


    X_nearby = nearby_shops[['lat', 'lon', 'open_hours']]
    X_nearby_scaled = scaler.transform(X_nearby)
    nearby_shops['predicted_safe_zone'] = model.predict(X_nearby_scaled)


    response = {
        'location': {'lat': lat, 'lon': lon},
        'nearby_shops': nearby_shops[['name', 'lat', 'lon', 'predicted_safe_zone']].to_dict(orient='records')
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

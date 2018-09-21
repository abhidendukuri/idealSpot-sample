from flask import Flask, jsonify, request
from os import environ 
import requests

# Configure the Flask app
app = Flask(__name__)

# Import API key from environment
api_key = environ.get('API_KEY_YELP')

# url paths
categories_url = "https://api.yelp.com/v3/categories?"
business_search_url = "https://api.yelp.com/v3/businesses/search?"
business_detail_url = "https://api.yelp.com/v3/businesses/"

# url parameters
# locale - query only the restaurants found in the US
locale = "locale=en_US"

# 1. /yelp/categories
@app.route("/yelp/categories")
def list_categories():

    # create list of categories to be displayed
    categories = []

    # Create the response that takes in the following
    #   # URL + Parameters - the only parameter is the locale so we append that to the url
    #   # headers - we need the API key in order to make calls to the Yelp Fusion API
    resp = requests.get(
        categories_url + locale, 
        headers = {'Authorization': "Bearer " + api_key}
    )
    
    # we need to get the name of each category so we iterate through the created dictionary
    for c in range(len(resp.json()['categories'])):
        
        # add each category to the categories list created earlier
        categories.append(resp.json()['categories'][c]['alias'])
    
    # return the list of categories
    return jsonify(data = categories)

# 2. /yelp/businesses/search/
@app.route("/yelp/businesses/search")
def business_search():

    # extract query parameters from URL
    # latitude and longitude are both required parameters
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    
    # radius is also a required parameter with a given default value of 1600 meters (roughly 1 mile)
    radius = request.args.get('radius', default = 1600)

    # categories is an optional parameter and how we utilize it will be shown below
    categories = request.args.get('categories')
    
    # if we have no category, we can shorten the url to have the other required parameters
    if categories == '':
        resp = requests.get(
            
            # the end of the url is a parameter limit=10 which displays only 10 business listings
            "%slatitude=%s&longitude=%s&radius=%s&limit=10" % 
                (business_search_url, latitude, longitude, radius),
            headers = {'Authorization': "Bearer " + api_key}
        )
    
    # otherwise, if a category is listed, we can change the url to include this query parameter
    else:
        resp = requests.get(

            # the end of the url is a parameter limit=10 which displays only 10 business listings
            "%slatitude=%s&longitude=%s&radius=%s&categories=%s&limit=10" % 
                (business_search_url, latitude, longitude, radius, categories),
            headers = {'Authorization': "Bearer " + api_key}
        )

    # Create new list for output
    bus_info = []

    # Iterate through each business
    for b in range(len(resp.json()['businesses'])):
        
        # Store the business details in a new dict variable bus_details
        bus_details = resp.json()['businesses'][b]

        # Using dictionary comprehension, extract id, name, and coordinates
        temp = {k:v for (k,v) in bus_details.items() if k =='id' or k == 'name' or k == 'coordinates'}
        
        # Copy these dictionaries into the created list
        bus_info.append(temp.copy())
    
    # return the list of businesses
    return jsonify(data = bus_info)

# 3. /yelp/businesses/details/<string:id>
@app.route("/yelp/businesses/details/<string:id>", methods=['GET'])
def list_business_details(id):
    
    # Create the response that takes in the following
    #   # URL + Parameters - the only parameter is the id of the location in the Yelp Fusion API
    #   # headers - we need the API key in order to make calls to the Yelp Fusion API
    resp = requests.get(
        business_detail_url + id, 
        headers = {'Authorization': "Bearer " + api_key}
    )

    # return the full response under a 'data' key
    return jsonify(data = resp.json())


if __name__ == '__main__':
    app.run()

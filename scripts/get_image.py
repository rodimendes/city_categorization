import oauthlib
import requests_oauthlib
import io
from PIL import Image
import requests
import os


CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
X_API_KEY = os.environ.get('X_API_KEY')

# set up credentials
client = oauthlib.oauth2.BackendApplicationClient(client_id=CLIENT_ID)
oauth = requests_oauthlib.OAuth2Session(client=client)

# get an authentication token
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                        client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def get_rect(lat, lon, pop):
    if pop > 10000000:
        increase = 0.06
    else:
        increase = 0.04
    upper_left_corner = [lon - increase, lat + increase]
    lower_right_corner = [lon + increase, lat - increase]
    box_coord = upper_left_corner + lower_right_corner
    return box_coord

def get_city_info(city):
    ###############################
    ## Looking data for the city ##
    ###############################

    # city = input('What city are we going to? ==> ') # For terminal use purposes
    api_url = f'https://api.api-ninjas.com/v1/city?name={city}'
    response = requests.get(api_url, headers={'X-Api-Key': X_API_KEY})
    if response.status_code == requests.codes.ok:
        city_info = response.json()
        lat_lon = (city_info[0]['latitude'], city_info[0]['longitude'])
        population = city_info[0]['population']
        coordinates = get_rect(lat=lat_lon[0], lon=lat_lon[1], pop=population)
        #print(f"Searching for {city_info[0]['name']}. Its population is about {population:,.2f}")
    else:
        print("Error:", response.status_code, response.text)

    return city_info, coordinates


def get_satellite_image(city):
    evalscript = """
    //VERSION=3

    function setup() {
    return {
        input: ["B02", "B03", "B04"],
        output: { bands: 3 }
    };
    }

    function evaluatePixel(sample) {
    return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
    }
    """

    ###########################################################
    ## Looking for the image with the least amount of clouds ##
    ###########################################################
    cloud_coverage = 2
    size = 0
    info, coordinates = get_city_info(city=city)
    while size < 100:
        json_request = {
        "input": {
            "bounds": {
            "bbox": coordinates,
            "properties": {
                "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [
            {
                "dataFilter": {
                "maxCloudCoverage": cloud_coverage
                },
                "type": "sentinel-2-l2a"
            }
            ]
        },
        "output": {
            "width": 2496,
            "height": 2496,
            "responses": [
            {
                "identifier": "default",
                "format": {
                "type": "image/tiff"
                }
            }
            ]
        },
            "evalscript": evalscript
        }
        url_request = 'https://services.sentinel-hub.com/api/v1/process'
        headers_request = {
            "Authorization" : "Bearer %s" %token['access_token']
        }

        #Send the request
        response = oauth.request("POST", url_request, headers=headers_request, json=json_request)
        # creating a image object (main image)
        city_image = Image.open(io.BytesIO(response.content))
        # save a image using extension
        city_image = city_image.save(f"{city}.tiff")
        # identifying if the image was gathered from its size
        size = os.stat(f'{city}.tiff').st_size/1000
        cloud_coverage += 2

    return response.content

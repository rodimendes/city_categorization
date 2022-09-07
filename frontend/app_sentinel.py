import oauthlib
import requests_oauthlib
import io
from PIL import Image
import requests
import os
import streamlit as st
import pandas as pd

##############################################
## Setting page configurations on Streamlit ##
##############################################
st.set_page_config(
            page_title="City Categorization",
            page_icon="🌎",
            layout="centered", # wide
            initial_sidebar_state="auto") # collapsed


CSS = """
h1, h2 {
    text-align: center;
}
h4 {
    text-align: center;
}
h6 {
    text-align: center;
    font-size: 16px;
    font-weight: 100;
}
p {
    text-align: center;
}
"""
st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

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

    ###############################
    ## Looking data for the city ##
    ###############################

    # city = input('What city are we going to? ==> ') # For terminal use purposes
    api_url = f'https://api.api-ninjas.com/v1/city?name={city}'
    response = requests.get(api_url, headers={'X-Api-Key': X_API_KEY})
    if response.status_code == requests.codes.ok:
        response = response.json()
        lat_lon = (response[0]['latitude'], response[0]['longitude'])
        population = response[0]['population']
        coordinates = get_rect(lat=lat_lon[0], lon=lat_lon[1], pop=population)
        #print(f"Searching for {response[0]['name']}. Its population is about {population:,.2f}")
    else:
        print("Error:", response.status_code, response.text)

    ###########################################################
    ## Looking for the image with the least amount of clouds ##
    ###########################################################
    columns[0].write(f"Searching for **{response[0]['name']}** 🗺. Its population is about **{population:,.2f}**")
    columns[0].write('Working to find the best image...')
    columns[0].write('🔎 🌍')

    cloud_coverage = 2
    size = 0
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

    columns[0].success('The search is over! 🎯 🏆')

    return response.content

###############
## Main code ##
###############

st.markdown("""# City Categorization
## A pilot project to assist territorial planning actions 🗺
###### made with 😀 by **Francisco Garcia**, **Pedro Chaves** and **Rodrigo Pinto** in 🇵🇹""")

#Columns
columns = st.columns(2)

uploaded_file = columns[0].file_uploader("Choose a file")
if uploaded_file is not None:
    columns[1].image(uploaded_file, caption=str(uploaded_file.name).capitalize())


columns[0].write('#### OR')

city = columns[0].text_input('City name 🌎')
if columns[0].button('Click me to find the city satellite image'):
    city_image = get_satellite_image(city=city)
    city_image = Image.open(io.BytesIO(city_image))
    print(f'Outside function - {type(city_image)}')
    image = Image.open(f'{city}.tiff')
    columns[1].image(image, caption=city.capitalize())

############################################
## Access the model e get processed image ##
############################################
# if st.button('Click me to process the image and see the result'):
#     st.image('New_Test.tif', caption='Cape Town')

# fill those informations before run
#CLIENT_ID = "<YOUR CLIENT ID FROM SENTINEL HUB>"
#CLIENT_SECRET = "<YOUR CLIENT SECRET FROM SENTINEL HUB>"
#X_API_KEY = "<YOUR API KEY FROM API-NINJAS>"

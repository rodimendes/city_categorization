from PIL import Image
import streamlit as st
from city_categorization.main import image_load
from scripts.get_image import get_city_info
from city_categorization import main
import numpy as np

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

st.markdown("""# City Categorization
## A pilot project to assist territorial planning actions 🗺
###### made with 😀 by **Francisco Garcia**, **Pedro Chaves** and **Rodrigo Pinto** in 🇵🇹""")

#Columns
columns = st.columns(2)

###############
## Main code ##
###############

uploaded_file = columns[0].file_uploader("Choose a file")
if uploaded_file is not None:
    columns[1].image(uploaded_file, caption=str(uploaded_file.name).capitalize())

columns[0].write('#### OR')

city = columns[0].text_input('City name 🌎')
if columns[0].button('Click me to find the city satellite image'):
    city_info, coords = get_city_info(city=city)
    columns[0].write(f"Searching for **{city_info[0]['name']}** 🗺. Its population is about **{city_info[0]['population']:,.2f}**")
    columns[0].write('Working to find the best image...')
    columns[0].write('🔎 🌍')
    city_image = image_load(city=city)
    image = Image.open(f'{city}.tiff')
    columns[1].image(image, caption=city.capitalize())
    columns[0].success('The search is over! 🎯 🏆')

    final_df, final_image = main.final_outputs(city)
    processed_image = Image.fromarray(final_image.astype(np.uint8))
    processed_image.save(f'{city}_categorized.tiff')
    new_columns = st.columns(2)
    new_columns[0].dataframe(final_df)
    new_columns[1].image(final_image, caption='Processed Image')


############################################
## Access the model e get processed image ##
############################################
# if st.button('Click me to process the image and see the result'):
#     st.image('New_Test.tif', caption='Cape Town')


#city = str(uploaded_file.name).split('.')[0]
    #city_info, coords = get_city_info(city=city) # TOKEN EXPIRED
    #final_df, final_image = main.final_outputs(city)

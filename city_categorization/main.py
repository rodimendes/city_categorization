from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from scripts.formulas import (get_image, blockshaped, unblockshaped,
                              get_array_pictures, get_picture_arrays,
                              pred_to_array, categories_df,
                              categories_to_image, save_tif)

import os
from scripts.get_image import get_satellite_image
from PIL import Image
import io

# Define some Parameters
LOCAL_DATA_PATH = os.environ.get("LOCAL_DATA_PATH")
CITY = os.environ.get('CITY')
LOCAL_MODEL_PATH = os.environ.get('LOCAL_MODEL_PATH')
DATA_TYPE = os.environ.get('DATA_TYPE')
LOAD_FILE = f"{CITY}{DATA_TYPE}"
PIXELS = int(os.environ.get('PIXELS'))


# Load Image (from local data for now)
def image_load(city):
    if os.environ.get('DATA_SOURCE') == 'local':
        im = get_image(os.path.join(LOCAL_DATA_PATH, 'raw', LOAD_FILE))
        #print(f"Loaded {LOAD_FILE} with shape {im.size}")
    else:
        city_image = get_satellite_image(city)
        im = Image.open(io.BytesIO(city_image))
        #print(f"Loaded {LOAD_FILE} with shape {im.size} from satellite!! 🎯")
    return im

# Convert Data to Arrays
def make_array(city):
    im = image_load(city=city)
    print(im.size)
    X = get_array_pictures(im, PIXELS)
    print(f"Generated a {type(X)} with {X.shape} shape")
    return X

# Load Model - > We will call it from the cloud after
def model_load():
    if os.environ.get('MODEL_SOURCE') == 'local':
        model = load_model(os.path.join(LOCAL_MODEL_PATH, 'augmented_model'))
        print(f'loaded model {model}')
    else:
        pass
    return model

# Preprocess
def preprocess(city):
    X = make_array(city=city)
    X_preprocessed = preprocess_input(X)
    print(f"Preprocessed X")
    return X_preprocessed

# Predict
def predict(city):
    model = model_load()
    X_preprocessed = preprocess(city=city)
    y_pred = model.predict(X_preprocessed)
    print(f"We predicted with shape {y_pred.shape}")
    return y_pred

# Create a Categorical Variable (Pipeline)
def y_cat_make(city):
    y_pred = predict(city=city)
    y_pred_cat = pred_to_array(y_pred)
    print(f"We reshaped y with shape {y_pred_cat.shape}")
    return y_pred_cat

# Create a Dataframe
def prediction_df():
    y_pred_cat = y_cat_make()
    prediction_df = categories_df(y_pred_cat)
    print(prediction_df)
    return prediction_df

# Map Array to RGB Palette
def rgb_image(city):
    im = image_load(city=city)
    y_pred_cat = y_cat_make(city=city)
    RGB_image = categories_to_image(y_pred_cat, im)
    print(f"Generated a final image with {RGB_image.shape} ")
    return RGB_image

def final_outputs(city):
    im = image_load(city=city)
    y_pred_cat = y_cat_make(city=city)
    prediction_df = categories_df(y_pred_cat)
    RGB_image = categories_to_image(y_pred_cat, im)
    print(f'''
          Process finished, we produced:
          {prediction_df}
          and an image with {RGB_image.shape}
          ''')
    return prediction_df, RGB_image



# if __name__ == '__main__':
#     image_load()
#     make_array()
#     model_load()
#     preprocess()
#     predict()
#     y_cat_make()
#     prediction_df()
#     rgb_image()
#     final_outputs()

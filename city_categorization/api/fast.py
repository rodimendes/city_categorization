from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.applications.resnet50 import preprocess_input
from scripts.formulas import (get_image, blockshaped, unblockshaped,
                              get_array_pictures, get_picture_arrays,
                              pred_to_array, categories_df,
                              categories_to_image, save_tif)



app = FastAPI()

# app.state.model = load_model()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/predict")
def predict(X):
    model = load_model()


# define a root `/` endpoint
@app.get("/")
def index():
    return {'greeting': 'Hello'}

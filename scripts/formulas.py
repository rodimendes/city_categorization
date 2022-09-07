from PIL import Image
import numpy as np
import pandas as pd
import rasterio
from rasterio.plot import reshape_as_raster

# Function to open Image
def get_image(path):
    im = Image.open(path)
    return im


# Function to Reshape Individual Bands into Smaller Pictures
def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    assert h % nrows == 0, f"{h} rows is not evenly divisible by {nrows}"
    assert w % ncols == 0, f"{w} cols is not evenly divisible by {ncols}"
    return (arr.reshape(h // nrows, nrows, -1,
                        ncols).swapaxes(1, 2).reshape(-1, nrows, ncols))


# Function to Reshape  Smaller Pictures into Individual Bands
def unblockshaped(arr, h, w):
    """
    Return an array of shape (h, w) where
    h * w = arr.size

    If arr is of shape (n, nrows, ncols), n sublocks of shape (nrows, ncols),
    then the returned array preserves the "physical" layout of the sublocks.
    """
    n, nrows, ncols = arr.shape
    return (arr.reshape(h // nrows, -1, nrows,
                        ncols).swapaxes(1, 2).reshape(h, w))


# Function to extract small pictures from satellite image
def get_array_pictures(image, pixels):
    im_array = np.array(image)
    band_dictionary = {}
    for band in range(im_array.shape[2]):
        band_dictionary["band{0}".format(band)] = blockshaped(
            im_array[:, :, band], pixels, pixels)

    concate_list = [band_dictionary[key] for key in band_dictionary]

    X = np.stack(concate_list, axis=im_array.shape[2])

    return X


# Function to reubuild image from small images (based on original size)
def get_picture_arrays(array, x_shape, y_shape):
    band_dictionary = {}
    for band in range(array.shape[3]):
        band_dictionary["band{0}".format(band)] = unblockshaped(
            array[:, :, :, band], x_shape, y_shape)

    concate_list = [band_dictionary[key] for key in band_dictionary]

    X_rebuilt_array = np.stack(concate_list, axis=2)
    X_rebuilt = Image.fromarray(X_rebuilt_array)

    return X_rebuilt


# Function to Convert Output Into Categories
def pred_to_array(y_pred):
    y_pred_cat = np.argmax(y_pred, axis=1)
    y_pred_cat_reduced = pd.Series(y_pred_cat).map(lambda x: 0 if x == 1 else (
        1 if x == 0 or x == 2 or x == 5 or x == 6 else (2 if x == 3 else (
            3 if x == 4 else (4 if x == 7 else 5))))).to_numpy()
    return y_pred_cat_reduced


# Function to Create Dataframe with Distributions
def categories_df(y_pred_cat):

    classes = {
        'Forest': 0,
        'Green': 1,
        'Highway': 2,
        'Industrial': 3,
        'Residential': 4,
        'Water': 5
    }
    classes_swap = dict([(value, key) for key, value in classes.items()])

    # Create Pandas Series
    classes_series = pd.Series(classes_swap, index=[0, 1, 2, 3, 4, 5])
    count_series = pd.Series(y_pred_cat).value_counts().map(
        lambda x: round(x * 0.4096, 2))
    percentage_series = pd.Series(y_pred_cat).value_counts(
        normalize=True).map(lambda x: round(x * 100, 2))

    #Creating a dictionary by passing Series objects as values
    frame = {
        'Category': classes_series,
        'Area in Km2': count_series,
        'Percentage': percentage_series
    }
    #Creating DataFrame by passing Dictionary
    df = pd.DataFrame(frame)
    df = df.set_index('Category').sort_values(by='Percentage', ascending=False)

    #return the dataframe
    return df


# Function to Convert Results into an Image
def categories_to_image(y_pred_cat, im):

    rgb_map = {
        0: (55, 86, 35),  # 'Forest'
        1: (69, 204, 108),  # 'Green'
        2: (105, 110, 106),  # 'Highway'
        3: (255, 183, 94),  # 'Industrial'
        4: (255, 232, 154),  # 'Residential'
        5: (0, 43, 191)  # 'Water'
    }

    R, G, B = np.vectorize(rgb_map.get)(y_pred_cat)
    R_arr = np.tile(R[:, np.newaxis, np.newaxis], (1, 64, 64))
    G_arr = np.tile(G[:, np.newaxis, np.newaxis], (1, 64, 64))
    B_arr = np.tile(B[:, np.newaxis, np.newaxis], (1, 64, 64))

    R_rebuilt = unblockshaped(R_arr, im.size[1], im.size[0])
    G_rebuilt = unblockshaped(G_arr, im.size[1], im.size[0])
    B_rebuilt = unblockshaped(B_arr, im.size[1], im.size[0])

    RGB_image = np.stack([R_rebuilt, G_rebuilt, B_rebuilt], axis=2)

    return RGB_image


# Function to Save Output and Geo-Raster
def save_tif(path_satellite, path_oputput):
    # 'Load image as Dataset'
    geodataset = rasterio.open(path_satellite)

    # Reshape Bands for RGB
    raster = reshape_as_raster(RGB_image)

    # Save output
    with rasterio.open(
            path_oputput,
            'w',
            driver='GTiff',
            height=geodataset.height,
            width=geodataset.width,
            count=3,
            dtype='uint8',
            crs=geodataset.crs,
            transform=geodataset.transform,
    ) as dst:
        dst.write(raster)

    return None

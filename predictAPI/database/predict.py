from database.db import *
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError
from itsdangerous import URLSafeTimedSerializer
import json
import sqlite3

from annoy import AnnoyIndex
import tensorflow as tf
import tensorflow_hub as hub

import numpy as np

from rembg import remove
from PIL import Image

dims = 1024
n_nearest_neighbors = 15

global menModel
global womenModel

pathAnnMen = "/home/demir/Desktop/BitirmeProjesi/getData/data/menAI/test0.ann"
tMen = AnnoyIndex(dims, metric='angular')
tMen.load(pathAnnMen)

pathAnnWomen = "/home/demir/Desktop/BitirmeProjesi/getData/data/womenAI/test0.ann"
tWomen = AnnoyIndex(dims, metric='angular')
tWomen.load(pathAnnWomen)


def load_img(path):


    inputt = Image.open(path)
    output = remove(inputt)

    new_image = Image.new("RGBA", output.size, "WHITE")
    new_image.paste(output, mask=output)

    new_image.save(path, optimize=True, quality=90)


    # Reads the image file and returns data type of string
    img = tf.io.read_file(path)

    # Decodes the image to W x H x 3 shape tensor with type of uint8
    img = tf.io.decode_jpeg(img, channels=3)

    # Resize the image to 224 x 244 x 3 shape tensor
    img = tf.image.resize_with_pad(img, 512, 512)

    # Converts the data type of uint8 to float32 by adding a new axis
    # This makes the img 1 x 224 x 224 x 3 tensor with the data type of float32
    # This is required for the mobilenet model we are using
    img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]

    return img


def get_image_feature_vectors(filenamee):

    module_handle = "https://tfhub.dev/google/imagenet/inception_v1/feature_vector/5"
  
    module = hub.load(module_handle)

    img = load_img(filenamee)

    # Calculate the image feature vector of the img
    features = module(img)   
  
    # Remove single-dimensional entries from the 'features' array
    feature_set = np.squeeze(features)  

    return feature_set


def predict_model(gender:int, image_path: str, user_id:int):

	try:

		cursor.execute(
			'SELECT user_premium, user_search_count FROM tbl_users WHERE user_id=%s and user_isdeleted=0 and user_confirmed=1', (user_id, ))
		userSn = cursor.fetchone()
		user_premium = userSn[0]
		user_search_count = userSn[1]

		if int(user_premium)!=1:

			if int(user_search_count)<=0:

				return JSONResponse(content="Deneme sürümü için geçerli 20 ürün arama hakkınızı bitirdiniz. Lütfen hesabınızı premium sürüme yükseltiniz", status_code=404)

			else:

				cursor.execute(
					'update tbl_users set user_search_count=user_search_count-1 where user_id=%s',
					(user_id,))
				conn.commit()

	except:

		return JSONResponse(content="Hatalı Kullanıcı", status_code=404)

	try:

		products = []

		products.append({

			"ArananUrun":image_path

			})

		feature_set = get_image_feature_vectors(image_path)

		if gender==0:

			conA= sqlite3.connect("/home/demir/Desktop/BitirmeProjesi/getData/data/menAI/men0.db")
			curA = conA.cursor()
			t = tMen 

		else:
	        
			conA= sqlite3.connect("/home/demir/Desktop/BitirmeProjesi/getData/data/womenAI/women0.db")
			curA = conA.cursor()
			t = tWomen

		nearest_neighbors = t.get_nns_by_vector(feature_set,n_nearest_neighbors, search_k=-1, include_distances=False)


		imgList = []

		for j in nearest_neighbors:

			imgList.append(j+1)

		imgListFinal = []

		for i in imgList:

			curA.execute("SELECT pr_no FROM Product WHERE pr_id=?;",[str(i)])

			row = curA.fetchone()

			imgListFinal.append(row)


		imagessList = []
		pr_id = []

		for img in imgListFinal:

			cursor.execute(
				'SELECT pr_id, img_url FROM tbl_product_images WHERE img_id=%s', (img,))
			image = cursor.fetchall()

			flag = None

			for j in pr_id:

				try:

					if str(j)==str(image[0][0]):
	                        
						flag = False
						break

				except:

					flag=False

					continue

			if flag==None:

				try:

					pr_id.append(image[0][0])
					imagessList.append([image[0][0], image[0][1]])

				except:

					continue

		if len(imagessList)!=0:

			for counter, i in enumerate(imagessList):

				cursor.execute(
					'SELECT pr_name, pr_url, pr_price from tbl_product WHERE pr_id=%s', (i[0],))
				prod = cursor.fetchall()

				namee=prod[0][0]

				imagessList[counter].append([namee, prod[0][1], prod[0][2]])
				
				products.append({

					"pr_id": imagessList[counter][0],
					"pr_name": imagessList[counter][2][0],
					"pr_url": imagessList[counter][2][1],
					"pr_price": imagessList[counter][2][2],
					"img_url": imagessList[counter][1]

					})

		print(products)

	except:

		return JSONResponse(content="Hatalı resim yükleme", status_code=404)
			

	return JSONResponse(content=products, status_code=200)
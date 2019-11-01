from flask import request
from flask import current_app as app
from app.util import *

import json
import random
import requests

@app.route('/')
def index():
    return 'Nothing to see here, try going to /api/v1/best_image or /api/v1/random_image'

@app.route('/api/v1/best_image')
def best_image():
    face_ids = remove_jpg_extension(json.loads(request.args.get('face_ids')))
    faces = set(face_ids) & set(get_uploaded_faces())
    if len(faces) == 0:
        return { 'message': 'You sure those faces are valid?' }, 400
    valid_faces = get_valid_faces(faces)
    if len(valid_faces) == 0:
        return { 'message': 'Uh oh, looks like the face_ids have expired! We have to do 2 things!' \
                 '1. Go to "faces/uploaded_faces" and move all the images to "faces/local_faces"' \
                 '2. In your terminal enter "flask shell" and then "from app.util import *" and then "upload_images" to reupload them' }, 400

    groups = get_groups(valid_faces)
    if len(groups) == 0:
        return { 'message': 'No similar groups were found in the images!' }, 200

    best_image = get_best_image(groups)
    best_image_data = get_face_data(best_image)
    return { 'filename': best_image + '.jpg', 'metadata': best_image_data }, 200

@app.route('/api/v1/random_image')
def random_image():
    a = dt.now()
    num = request.args.get('num')
    if not num.isdigit():
        return { 'message': 'Please input a number!!!' }, 400
    num = int(num)

    # only max of 1000 faces allowed
    if num > 1000:
        num = 1000

    uploaded_faces = get_uploaded_faces()
    if len(uploaded_faces) < num:
        return { 'message': 'Uh oh, you either picked too large of a number or the faces have not been uploaded yet!' }, 400
    faces = random.sample(uploaded_faces, num)

    valid_faces = get_valid_faces(faces)
    if len(valid_faces) == 0:
        return { 'message': 'Uh oh, looks like the face_ids have expired! We have to do 2 things!' \
                 '1. Go to "faces/uploaded_faces" and move all the images to "faces/local_faces"' \
                 '2. In your terminal enter "flask shell" and then "from app.util import *" and then "upload_images" to reupload them' }, 400

    groups = get_groups(valid_faces)
    if len(groups) == 0:
        return { 'message': 'No similar groups were found in the images!' }, 200

    best_image = get_best_image(groups)
    best_image_data = get_face_data(best_image)
    return { 'filename': best_image + '.jpg', 'metadata': best_image_data }, 200


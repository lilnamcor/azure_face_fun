from flask import current_app as app
from app.secrets import API_KEY_1, FACE_UPLOAD_URL, FACE_GROUP_URL
from app.models import db, Face

from datetime import datetime as dt
import requests
import os
import json
import time
from PIL import Image
from resizeimage import resizeimage

# uploads all images and renames them to returned faceID
def upload_images():
    # just in case if dir is deleted (also github does not allow empty directories)
    if not os.path.isdir('faces/uploaded_faces'):
        os.mkdir('faces/uploaded_faces')

    local_faces = get_local_faces()
    for face in local_faces:
        local_face_path = 'faces/local_faces/' + face
        resize_image(local_face_path)
        image = open(local_face_path, 'rb').read()

        headers = get_headers('application/octet-stream')

        params = {
            'returnFaceId': True,
            'returnFaceLandmarks': True,
            'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
        }

        resp = requests.post(FACE_UPLOAD_URL, params=params, headers=headers, data=image)
        try:
            resp = json.loads(resp.text)[0]
            face_id = resp.pop('faceId')
            faceRectangle = resp['faceRectangle']
            size = faceRectangle['width'] * faceRectangle['height']
            add_face(face_id, size, json.dumps(resp), dt.now())

            os.rename(local_face_path, 'faces/uploaded_faces/' + face_id + '.jpg') # rename to match the face_id
        except:
            # some prints to help understand why an error occurred
            print(resp.status_code)
            print(resp.text)

            # moved to bad folder so we do not try to upload again
            # seems like azure API can't determine if its a face
            os.rename(local_face_path, 'faces/bad_faces/' + face)
        time.sleep(3) # I'm rate limited to 20 actions per minute :(

# standardize all image sizes, this seems to be standard size in all face datasets
def resize_image(image, w=640, h=480):
    f = open(image, 'rb')
    img = Image.open(f)
    width, height = img.size
    if width != w or height != h:
        img = resizeimage.resize_cover(img, [w, h])
        img.save(image, img.format)
    f.close()

def get_face_data(face):
    return json.loads(Face.query.filter(Face.face_id == face).first().face_data)

# All images are 640 x 480 so just grab the biggest size
def get_best_image(groups):
    biggest_group = get_biggest_group(groups)
    faces = Face.query.filter(Face.face_id.in_(biggest_group)).all()
    max_size = 0
    best_face = None
    for face in faces:
        if face.size > max_size:
            max_size = face.size
            best_face = face.face_id
    return best_face

def get_groups(faces):
    headers = get_headers('application/json')
    data = { 'faceIds': faces}

    resp = requests.post(FACE_GROUP_URL, headers=headers, json=data)
    return json.loads(resp.text).get('groups', [])

def get_biggest_group(groups):
    index = 0
    max_size = 0
    for i, group in enumerate(groups):
        length = len(group)
        if length > max_size:
            max_size = length
            index = i
    return groups[index]

def get_local_faces():
    return os.listdir('faces/local_faces')

def get_uploaded_faces():
    faces = Face.query.all()
    return list(map(lambda x: x.face_id, faces))

def get_valid_faces(faces):
    face_models = Face.query.filter(Face.face_id.in_(faces)).all()
    valid_faces = []
    for face in face_models:
        if (dt.now() - face.created_at).days < 1: # 1 day
            valid_faces.append(face.face_id)
    return valid_faces

def get_headers(content_type):
    return {
        'Content-Type': content_type,
        'Ocp-Apim-Subscription-Key': API_KEY_1
    }

def remove_jpg_extension(faces):
    return list(map(lambda face: face[0: -4] if face[-4: len(face)] == '.jpg' else face, faces))

def add_face(face_id, size, face_data, created_at):
    db.session.add(Face(face_id=face_id, size=size, face_data=face_data, created_at=created_at))
    db.session.commit()

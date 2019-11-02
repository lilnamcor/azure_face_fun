import unittest
import json
from datetime import datetime as dt
from datetime import timedelta
from PIL import Image
from shutil import copyfile
import os

from app import create_app
from app.models import db, Face
from app.util import *

class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app = create_app('sqlite:////tmp/test.db')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        ctx = app.app_context()
        ctx.push()
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()


###############
#### tests ####
###############

    def test_app(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), 'Nothing to see here, try going to /api/v1/best_image or /api/v1/random_image')

    def test_get_biggest_group(self):
        groups = [[1, 2, 3], [1, 2], [1, 2, 3, 4, 5], [1, 2, 3, 4]]
        self.assertEqual(get_biggest_group(groups), [1, 2, 3, 4, 5])

    def test_get_best_image(self):
        groups = [['1', '2'], ['1'], ['1', '2', '3']]
        add_face('1', 4, json.dumps({'data': 444 }), dt.now())
        add_face('2', 2, json.dumps({'data': 222 }), dt.now())
        add_face('3', 3, json.dumps({'data': 333 }), dt.now())
        self.assertEqual(get_best_image(groups), '1')

    def test_get_face_data(self):
        add_face('123', 456, json.dumps({'data': 789 }), dt.now())
        self.assertEqual(get_face_data('123'), {'data': 789})

    def test_get_uploaded_faces(self):
        add_face('1', 4, json.dumps({'data': 444 }), dt.now())
        add_face('2', 2, json.dumps({'data': 222 }), dt.now())
        add_face('3', 3, json.dumps({'data': 333 }), dt.now())
        self.assertEqual(get_uploaded_faces(), ['1', '2', '3'])

    def test_get_valid_faces(self):
        add_face('1', 4, json.dumps({'data': 444 }), dt.now() - timedelta(hours=25))
        add_face('2', 2, json.dumps({'data': 222 }), dt.now() - timedelta(hours=23))
        add_face('3', 3, json.dumps({'data': 333 }), dt.now() - timedelta(hours=22))
        self.assertEqual(len(get_valid_faces(['1', '2', '3'])), 2)

    def test_remove_jpg_extension(self):
        jpg = ['test.jpg']
        no_jpg = ['hello']
        self.assertEqual(remove_jpg_extension(jpg), ['test'])
        self.assertEqual(remove_jpg_extension(no_jpg), ['hello'])

    def test_resize_image(self):
        copyfile('app/tests/test.jpg', 'app/tests/test1.jpg')
        img = Image.open('app/tests/test1.jpg')
        self.assertEqual(img.size, (1280, 960))

        resize_image('app/tests/test1.jpg')
        img = Image.open('app/tests/test1.jpg')
        self.assertEqual(img.size, (640, 480))
        os.remove('app/tests/test1.jpg') # image is downsized and cannot upsize it, so delete and copy again
        copyfile('app/tests/test.jpg', 'app/tests/test1.jpg')

        resize_image('app/tests/test1.jpg', 1280, 960)
        img = Image.open('app/tests/test1.jpg')
        self.assertEqual(img.size, (1280, 960))

        os.remove('app/tests/test1.jpg')

if __name__ == "__main__":
    unittest.main()

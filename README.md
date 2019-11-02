Face Fun
==================

### To get started first
    $ pip install flask
    # pip install python-resize-image

### To upload faces (face_id only last 24 hours in Azure) make sure the faces are in local_faces
    $ flask shell
    $ >>> from app.util import upload_images
    $ >>> upload_images()

This takes around 30 minutes to run. It is on the free tier and its rate limited to 20 requests
a minute

### To run the server
    $ flask run

### To get best image from a random number of images go to
    $ http://127.0.0.1:5000/api/v1/random_image?num=30

### To get best image from a list of images simply pass them to best_image
    $ http://127.0.0.1:5000/api/v1/best_image?face_ids=["face_id1","face_id2",...]

### To run tests first download nose2 then go to the base project directory
    $ pip install nose2
    $ nose2

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import threading
import camera_function

cred = credentials.Certificate('/home/pi/servicekey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'em25-c1a70.appspot.com'})

camera_upload_thread = threading.Thread(target=camera_function.camera_upload)
save_image_thread = threading.Thread(target=camera_function.save_image)

camera_upload_thread.start()
save_image_thread.start()
# -*- coding: utf-8 -*-

import io
import config_t
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
import google.cloud.exceptions


import os
import PIL
from PIL import Image
import rawpy
import imageio

init = False
# import google.cloud.storage

# from google.cloud import pubsub
# client = pubsub.Client('my-project-vision-api')

# google app credentials
GAC = config_t.g_cred
client = vision.Client.from_service_account_json(GAC)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_t.g_cred
client_safe = vision.ImageAnnotatorClient()

# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()


def convert_raw(filename):
    print 'convert_raw'
    save_filename = filename + '_temp_del_.jpg'

    if not os.path.isfile(save_filename):

        with rawpy.imread(filename) as raw:
            rgb = raw.postprocess()

        f = io.BytesIO()
        f.write(rgb)


        print 'convert', save_filename
        imageio.imwrite(save_filename, rgb)

    img_jpg = Image.open(save_filename)

    return img_jpg


def file_selector_jpg (filename):
    #print 'selector'
    '''returns Image object for jpg and RAW'''

    if  filename.lower().endswith(('.jpg', '.jpeg')):
        try:
            img_jpg = Image.open(filename)
        except:
               print 'Can''t open '+ filename
               return None

    if  filename.lower().endswith(('.cr2', '.arw')):
        img_jpg = convert_raw(filename)

    return img_jpg


# Instantiates a client
def detect_label(local_filename, its_hash):
    '''

    :param local_filename_n_hash:
    :return:
    '''
    global client



    GAC = config_t.g_cred
    client = vision.Client.from_service_account_json(GAC)

    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GAC

    # img = Image.open(local_filename)
    # width, height = img.size


    try:
        img = file_selector_jpg(local_filename)

    except:
        print 'Error opening file' + local_filename
        return [[u'none', u'0.0', its_hash]]

    # check file size
    file_size = img.size
    #print file_size

    #print 'resize'

    if file_size > config_t.file_max_size:
        basewidth = config_t.file_resize_value
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        # print 'Picture is too big, skip'
        # return [[u'none', u'0.0', its_hash]]

    # Loads the image into memory
    # with io.open(local_filename, 'rb') as image_file:

    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='JPEG')
    content = imgByteArr.getvalue()

    image = client.image(content=content)

    # Performs label detection on the image file
    try:
        print 'detect label'
        labels = image.detect_labels()

        #detect_safe_search_uri(local_filename+'_temp_del_.jpg')

    except:
        print 'Error with labeling: ', local_filename
        return [[u'none', u'0.0', its_hash]]

    output = []
    if len(labels)==0:
        output.append(['Unknown stuff', str(1.0), its_hash])

    else:
        for label in labels:
            #print label.description.encode('utf-8'), str(label.score), its_hash
            output.append([label.description.encode('utf-8'), str(label.score), its_hash])

    return output


def detect_landmark_uri(uri, hash):
    """Detects unsafe features in the file located in Google Cloud Storage or
        on the Web."""
    global init
    global client_safe

    if not init:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_t.g_cred

        client = vision.ImageAnnotatorClient()
        init = True
        print 'init true'



    #with io.open(uri, 'rb') as image_file:
    #    content = image_file.read()

    img = file_selector_jpg(uri)
    if img is None:
        print 'Can''t open, skip ' +uri
        return [('', '', '')]

    # check file size
    file_size = img.size
    #print file_size



    if file_size > config_t.file_max_size:
        #print 'resize'
        basewidth = config_t.file_resize_value
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        #print 'resized'



    imgByteArr = io.BytesIO()
    try:
        img.save(imgByteArr, format='JPEG')
    except:
        print 'Issue with img save'
        return [('', '', '')]

    content = imgByteArr.getvalue()
    image = types.Image(content=content)

    try:
        response = client.landmark_detection(image=image)

    except google.cloud.exceptions.GoogleCloudError as e:
        print 'Error with detection '+ uri + str(e)
        return [('','','')]

    safe = response.safe_search_annotation

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    #print('Safe search:')

    landmarks = response.landmark_annotations
    print('Landmarks:')

    for landmark in landmarks:
        print(landmark.description)
        for location in landmark.locations:
            lat_lng = location.lat_lng
            print 'Latitude'.format(lat_lng.latitude)
            print 'Longitude'.format(lat_lng.longitude)

    #print('adult: {}'.format(likelihood_name[safe.adult]))
    return [('adult', 'adult: ' + likelihood_name[safe.adult], hash),
            ('medical', 'medical: ' + likelihood_name[safe.medical], hash),
            ('spoofed', 'spoofed: ' + likelihood_name[safe.spoof], hash),
            ('violence', 'violence: ' + likelihood_name[safe.violence], hash) ]

def detect_safe_search_uri(uri, hash):
    """Detects unsafe features in the file located in Google Cloud Storage or
        on the Web."""
    global init
    global client_safe

    if not init:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_t.g_cred

        #client_safe = vision.ImageAnnotatorClient()
        init = True
        print 'init true'



    #with io.open(uri, 'rb') as image_file:
    #    content = image_file.read()

    img = file_selector_jpg(uri)
    if img is None:
        print 'Can''t open, skip ' +uri
        return [('', '', '')]

    # check file size
    file_size = img.size
    #print file_size



    if file_size > config_t.file_max_size:
        #print 'resize'
        basewidth = config_t.file_resize_value
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        #print 'resized'



    imgByteArr = io.BytesIO()
    try:
        img.save(imgByteArr, format='JPEG')
    except:
        print 'Issue with img save'
        return [('', '', '')]

    content = imgByteArr.getvalue()
    image = types.Image(content=content)

    try:
        response = client_safe.safe_search_detection(image=image)

    except google.cloud.exceptions.GoogleCloudError as e:
        print 'Error with detection '+ uri + str(e)
        return [('','','')]

    safe = response.safe_search_annotation

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    #print('Safe search:')

    #print('adult: {}'.format(likelihood_name[safe.adult]))
    return [('adult', 'adult: ' + likelihood_name[safe.adult], hash),
            ('medical', 'medical: ' + likelihood_name[safe.medical], hash),
            ('spoofed', 'spoofed: ' + likelihood_name[safe.spoof], hash),
            ('violence', 'violence: ' + likelihood_name[safe.violence], hash) ]

    #print('medical: {}'.format(likelihood_name[safe.medical]))
    #print('spoofed: {}'.format(likelihood_name[safe.spoof]))
    #print('violence: {}'.format(likelihood_name[safe.violence]))


if __name__ == '__main__':
    #files = ['hello.jpg', '/media/home/hello.jpg']
    #print files[1][:-len(files[0])-1]
    #print ''
    print detect_landmark_uri(u'/home/egorium/Dropbox/Vision API/imgs/2017-08-03 15-28-08.JPG', '111')
    #print detect_label('/home/egorium/Dropbox/Vision API/imgs/2017-01-28 16-56-34.JPG','111')


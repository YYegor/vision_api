# -*- coding: utf-8 -*-

DEBUG = True

user = 'python'
password = '2017python!'
host = '127.0.0.1'
database = 'vision_api'

#google  credentials JSON path
g_cred = 'My Project - vision API-41fd43e01d03.json'
#GOOGLE_APPLICATION_CREDENTIALS='My Project - vision API-41fd43e01d03.json'

#test_path_01 = u'E:\YandexDisk\Фотокамера\TEST'
#test_path_02 = u'E:\\YandexDisk\\Фотокамера\\2015\\01'

#path_amster = u'E:\\YandexDisk\\Фотокамера\\201603 Amsterdam'
#path_full = u'E:\\YandexDisk\\Фотокамера'
path_root_cut = u'/media/egorium/Новый том/YandexDisk/'
path_full_master = u'/media/egorium/Новый том/YandexDisk/Fotos/Archive/2016/2016_11 Paris'

#tags to include
tags_show = ['EXIF ISOSpeedRatings' ,'EXIF LensModel', 'EXIF FocalLengthIn35mmFilm', 'EXIF ExposureTime', 'EXIF DateTimeOriginal', 'EXIF Model', 'Image Make', 'Image Model', 'GPS GPSLongitude', 'GPS GPSLatitude', 'GPS GPSLongitudeRef', 'GPS GPSLatitudeRef']
tags_raw_show = ['EXIF:ISO', 'EXIF:LensModel', 'EXIF:FocalLength', 'EXIF:ExposureTime', 'EXIF:CreateDate', 'EXIF:Model', 'EXIF:Make']

# suffix  for raw to jpg conversion
jpg_raw_suffix = '_temp_del_.jpg'

# labeling error avoiding
file_max_size = 5000000
file_resize_value = 1000
file_thumb_value = 200


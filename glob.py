# -*- coding: utf-8 -*-

import fnmatch
import os
import exifread
import hashlib
import config_t
import ConfigParser

import exiftool


def convert_meta_exif(metadata_exifread):
    '''converts json metadata into my format of exif'''
    tags = {}

    for key, value in metadata_exifread.iteritems():
        if key.find('EXIF')>=0:
            if key == 'EXIF:ExposureTime':
                value_s = 1.0 / float (value)
                value = '1/'+str(int(value_s))
            try:
                exif_index = config_t.tags_raw_show.index(key)

            except:
                #nothing
                continue

            tags[config_t.tags_show[exif_index]]  = value

    return tags




def read_exif_from_raw(fio):
    '''reads metadata from RAW'''

    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(fio)

    #print metadata["SourceFile"], metadata["EXIF:DateTimeOriginal"]
    return convert_meta_exif(metadata)



#return tags from folder
def get_tags_from_txt (foldername, hash):
    #foldername = '/media/egorium/Новый том/YandexDisk/Fotos/2017_01_05 Cross-studio'



    def get_config():
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        try:
            config.read(foldername + "/vision_tags.txt")
            return config
        except Exception, e:
            print e
            return None

    if get_config() is not None:
        c = get_config()
    else:
        return [('', '', hash), ('', '', hash)]

    gps_country = ''
    gps_city = ''

    try:
        gps_country = c.get('meta', 'GPS Country')
    except:
        print 'Can''t read GPS Country or not found for '+foldername

    try:
        gps_city = c.get('meta', 'GPS City')
    except:
        print 'Can''t read GPS city or not found for '+foldername

    return [('GPS Country', gps_country, hash), ('GPS City', gps_city, hash)]



# Open image file for reading (binary mode)
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Return Exif tags


def get_file_list(root_path):
    '''

    :param root_path:
    :return: filename, path, hash, exifs
    '''
    folder_data = []
    exifs = []
    tags_show = config_t.tags_show



    for root, dirnames, filenames in os.walk(root_path):

        for filename in filenames:
            if filename.endswith(('.cr2', '.ARW', '.arw', '.CR2')):
                print 'RAW:  ', filename

                db_full_path = os.path.join(root, filename)
                db_filename = filename
                db_hash = md5(os.path.join(root, filename))

                folder_data.append([db_filename, db_full_path, db_hash])
                print 'RAW', filename
                tags = read_exif_from_raw ( db_full_path )

                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote') and tag in tags_show:
                        print "RAW  Key: %s, value %s" % (tag, tags[tag])
                        exifs.append([str(tag), u''+str(tags[tag]), str(db_hash)])


        for filename in fnmatch.filter(filenames, '*.jp*g'):

            print filename
            if filename.endswith('.ARW_temp_del_.jpg'):
                print '.ARW_temp_del_.jpg found, skip'
                continue

            db_full_path = os.path.join(root, filename)
            db_filename = filename
            db_hash = md5(os.path.join(root, filename))

            folder_data.append([db_filename, db_full_path, db_hash])

            #print os.path.join(root, filename), db_hash

            f = open(os.path.join(root, filename), 'rb')

            tags = exifread.process_file(f)
            for tag in tags.keys():
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote') and tag in tags_show:
                    #print "Key: %s, value %s" % (tag, tags[tag])
                    exifs.append([str(tag), u''+str(tags[tag]), str(db_hash)])
            f.close()

    #print folder_data
    return folder_data, exifs

if __name__=='__main__':
    #print get_tags_from_txt ('/media/egorium/Новый том/YandexDisk/Fotos/2017_01_05 Cross-studio')
    print get_file_list(u'/media/egorium/Новый том/YandexDisk/Fotos/2017_01_05 Cross-studio/Export')
    #read_exif_raw(u'/home/egorium/Dropbox/Vision API/imgs/4Z8A3224.CR2')
    #convert_raw (u'/home/egorium/Dropbox/Vision API/imgs/4Z8A3224.CR2')
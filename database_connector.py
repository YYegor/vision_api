# -*- coding: utf-8 -*-

import mysql.connector
import config_t
import glob
import MySQLdb
import labeling

import PIL
from PIL import Image

import io

cnx = mysql.connector


def init_db():
    '''init db and update cnx'''
    global cnx
    cnx = mysql.connector.connect(user=config_t.user, password=config_t.password, host=config_t.host,
                                  database=config_t.database)


def add_location_from_gps():
    import geo_tags

    global cnx

    if cnx is None: init_db()

    cursor = cnx.cursor()

    sql = ''' SELECT DISTINCT hash FROM vision_api.tags where tag like 'GPS%' and type = 'exif'; '''
    cursor.execute(sql)

    # get all hash for gps tags
    hashs = [item[0] for item in cursor.fetchall()]
    print len(hashs)

    # get hash of already  coded
    sql = ''' SELECT DISTINCT hash FROM vision_api.tags where tag like 'GPS%' and type = 'meta'; '''
    cursor.execute(sql)
    hashs_geocoded = [item[0] for item in cursor.fetchall()]

    print len(hashs_geocoded)

    for index,  h in enumerate(hashs):

        sql = '''SELECT tag, tag_value FROM vision_api.tags where tag like 'GPS%%' and hash = '%s' and type = 'exif';''' % str(h)
        cursor.execute(sql)
        tags_set = cursor.fetchall()

        lat = tags_set[0][1]
        lat_ref = tags_set[1][1]
        long = tags_set[2][1]
        long_ref = tags_set[3][1]


        print lat, lat_ref, long, long_ref

        #if index < 8000 and h not in hashs_geocoded:
        if h not in hashs_geocoded:
            country = u''
            city = u''
            country, city = geo_tags.get_geo_data(geo_tags.convert_to_degrees(lat, lat_ref), geo_tags.convert_to_degrees(long, long_ref))
            print country, city

            if country <> '' or country is not None:
                sql_insert = u'''CALL insert_gps_location ('%s', "%s", '%s');''' % ('GPS Country', country, h)
                print sql_insert
                try:
                    cursor.execute(sql_insert)
                    cnx.commit()
                    print 'commit country', country

                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    print(e)
                    print 'continue'
                    continue


            if city <> '' or city is not None:
                sql_insert = u'''CALL insert_gps_location ('%s', "%s", '%s');''' % ('GPS City', city, h)
                print sql_insert
                try:
                    cursor.execute(sql_insert)
                    cnx.commit()
                    print 'commit city', city

                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    print(e)
                    print 'continue'
                    continue



def remove_duplicates_db():
    '''remove duplicates by hash'''
    global cnx
    cursor = cnx.cursor()

    sql_remove_identicals = """CALL remove_identical_from_files()"""
    if config_t.DEBUG:
        print sql_remove_identicals

    cursor.execute(sql_remove_identicals)
    try:
        cnx.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print e




def insert_files_db(folder_data):
    global cnx
    cursor = cnx.cursor()

    if config_t.DEBUG:
        print folder_data

    all_hashs = get_all_hash_files()

    for row in folder_data:

        if (row[2],) in all_hashs:
            if config_t.DEBUG:
                print 'SKIP hash for ', row[2]
            continue

        if config_t.DEBUG:
            print 'Calling insert_thumbnail'

        try:
            insert_thumbnail(row[1], row[2])
        except:
            print 'Error while inserting thumbnail'

        sql_string = """CALL insert_file_data('%s', '%s', '%s')""" % (row[0], row[1], row[2])

        try:
            if config_t.DEBUG:
                print sql_string.replace('\\', '\\\\')

            cursor.execute(sql_string.replace('\\', '\\\\'))

        except mysql.connector.Error as err:

            print("Something went wrong while insert_file_data: {}".format(err))
            return


        #insert tag with folder
        #folder_data.append([db_filename, db_full_path, db_hash])
        #print config_t.path_full_master, row[1][len(config_t.path_full_master):]
        #row[len(config_t.path_root_cut):-len(row0) - 1]
        sql_string = """CALL insert_meta_folder_data('%s', '%s')""" % (row[1][len(config_t.path_root_cut):-len(row[0]) ], row[2])

        try:

            cursor.execute(sql_string)

        except mysql.connector.Error as err:

            print("Something went wrong while insert folder meta data: {}".format(err))
            return

    try:
        cnx.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print e

    return



def insert_exif(exifs_data):
    global cnx
    cursor = cnx.cursor()

    for row in exifs_data:

        sql_string = """CALL insert_exif_tag ('%s', '%s', '%s')""" % (row[0], row[1], row[2])
        print sql_string
        try:
            cursor.execute(sql_string.replace('\\', '\\\\'))

        except MySQLdb.InternalError as error:
            code, message = error.args
            print ">>>>>>>>>>>>>", code, message

    try:
        cnx.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print e


def insert_label(label_data):
    '''
    label_data = str(label.description), str(label.score), its_hash
    type = meta

    :param label_data:
    :return:
    '''

    cnx = mysql.connector.connect(user=config_t.user, password=config_t.password, host=config_t.host,
                                  database=config_t.database)

    cursor = cnx.cursor()


    for row in label_data:

        if row[0] == 'none':
            print 'SKIP'
            continue


        sql_string = """CALL insert_label_data ("%s", "%s", "%s")""" % (str(row[1]), str(row[0]), str(row[2]))

        if config_t.DEBUG:
                print sql_string

        try:

            cursor.execute(sql_string)

        except MySQLdb.InternalError as error:
            code, message = error.args
            print ">>>>>>>>>>>>>", code, message

    try:
        cnx.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print e


def insert_meta(meta_data):
    '''
    meta_data = tag, tag_value, its_hash
    type = meta

    :param label_data:
    :return:
    '''


    cnx = mysql.connector.connect(user=config_t.user, password=config_t.password, host=config_t.host,
                                  database=config_t.database)

    cursor = cnx.cursor()

    for row in meta_data:

        if row[1] == '':
            #print 'SKIP if empty'
            continue


        sql_string = """CALL insert_meta_tag ("%s", "%s", "%s")""" % (str(row[0]), str(row[1]), str(row[2]))

        if config_t.DEBUG:
                print sql_string

        try:

            cursor.execute(sql_string)

        except MySQLdb.InternalError as error:
            code, message = error.args
            print ">>>>>>>>>>>>>", code, message

    try:
        cnx.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print e


def insert_thumbnail(local_filename, hash):
    global cnx
    cursor = cnx.cursor()
    #try:
    img = labeling.file_selector_jpg(local_filename)
    # except:
    #         print 'Error opening file' + local_filename
    #         return None

    basewidth = config_t.file_thumb_value
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)

    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='JPEG')
    content = imgByteArr.getvalue()

    sql_string = """CALL insert_thumb (%s, %s)"""
    args = (content, hash)
    cursor.execute(sql_string, args)
    cnx.commit()


def get_all_hash_files():
    global cnx
    cursor = cnx.cursor()
    sql_string = """SELECT hash from files"""
    cursor.execute(sql_string)
    hashs = cursor.fetchall()
    return hashs


def get_all_hash_labels():
    global cnx
    cursor = cnx.cursor()
    sql_string = """SELECT DISTINCT hash from tags where type='label' """
    cursor.execute(sql_string)
    hashs = cursor.fetchall()
    return hashs



def get_all_unlabelled():
    '''get all rows where there are no tags with 'label' type
    :return:
    filename, path, hash
    '''

    global cnx

    cursor = cnx.cursor()

    cursor.callproc('''get_unlabelled''')
    cnx.commit()

    for result in cursor.stored_results():
        res = result.fetchall()

    return res


def get_all_unlabelled_adult():
    '''get all rows where there are no tags with 'label' type
    :return:
    filename, path, hash
    '''

    global cnx

    cursor = cnx.cursor()

    cursor.callproc('''get_unlabelled_adult''')
    cnx.commit()

    for result in cursor.stored_results():
        res = result.fetchall()

    return res



def get_freq_labels():
    global cnx

    cursor = cnx.cursor()

    cursor.callproc('''get_frequent_labels''')
    cnx.commit()

    for result in cursor.stored_results():
        res = result.fetchall()

    return res



if __name__ == '__main__':
    init_db()
    print get_all_unlabelled()

    # row0 = u'DSC05692-3.jpg'
    # row = u'/media/egorium/Новый том/YandexDisk/Fotos/2017_01_05 Cross-studio/Export/DSC05692-3.jpg'
    # print row[len(config_t.path_root_cut):-len(row0)]
    # exit()
    # #print get_freq_labels()
    # #"E:\\YandexDisk\\\xd0\xa4\xd0\xbe\xd1\x82\xd0\xbe\xd0\xba\xd0\xb0\xd0\xbc\xd0\xb5\xd1\x80\xd0\xb0\\SELL\\2017-01-01 00-18-58.JPG"
    # insert_thumbnail('E:\\YandexDisk\\Фотокамера\\SELL\\2017-01-01 00-18-58.JPG'.decode('utf-8'), '312655c626e12c19e27cd82f77e55fa2')
    #
    # exit()
    #add_location_from_gps()


    # folder_data, exifs_data = glob.get_file_list(config_t.path_amster)
    #
    # # print 'before call', folder_data
    #
    # # insert files and hash into db
    # insert_files_db(folder_data)
    #
    # # insert exifs
    # insert_exif(exifs_data)
    #
    # # remove identical hash records
    # remove_duplicates_db()

    # for index, files in enumerate(folder_data):
    #     print round(100.0 * index / len(folder_data))
    #     insert_labels(labeling.detect_label(files[1], files[2]))

    cnx.close()



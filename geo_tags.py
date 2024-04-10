# -*- coding: utf-8 -*-

import urllib, json

GOOGLE_MAP_KEY = "AIzaSyC0PjE7bxuAj1MjjZldJHNfE2o7GH4N6i8"




def convert_to_degrees(value, ref):
    multiplier = -1

    if ref == 'E' or ref == 'N':
        multiplier = 1

    #remove [ and ]
    value = value[1:-1]

    value_str = value.split(', ')
    try:
        value_str[2] = value_str[2]+'.0'
    except:
        print 'Error with index after split'
        return None

    #print value_str[2]
    try:
        s1, s2 = value_str[2].split('/')
    except:
        #print 'Error with split, trying different'

        try:
            s1 = value_str[2]
            s2 = 1
        except:
            print '3rd value is strange'
            return None


    #print 's1 , s2', s1, s2

    d = float(value_str[0])+0.0
    m = float(value_str[1])+0.0
    s = float(s1) / float (s2)

    #print 's', s

    return multiplier * (d + (m / 60.0) + (s / 3600.0))


        # if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        #     lat = _convert_to_degress(gps_latitude)
        #     if gps_latitude_ref != "N":
        #         lat = 0 - lat
        #
        #     lon = _convert_to_degress(gps_longitude)
        #     if gps_longitude_ref != "E":
        #         lon = 0 - lon



def get_geo_country(data_json):
    country = ''
    try:
        data = data_json['results'][0]['address_components']

    except:
        print 'Error retrieving country'
        return ''

    for d in data:
        if u'country' in d['types']:
            #print d['long_name']
            country = d['long_name']

    return country


def get_geo_city(data_json):
    city = ''
    try:
        data = data_json['results'][0]['address_components']

    except:
        print 'Error retrieving city'
        return ''

    for d in data:
        if u'administrative_area_level_1' in d['types']:
            #print d['long_name']
            city = d['long_name']

    return city


def get_geo_data(latitude, longitude):

    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(latitude) + "," + str(
        longitude) + "&sensor=false&key=" + GOOGLE_MAP_KEY
    print url

    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))
    except:
        print 'Error accessing Google maps api'
        return ['', '']


    return [get_geo_country(data), get_geo_city(data)]



if __name__ == '__main__':
    exif_lat = '[12, 9, 4877243/1000000]'
    exif_log = '[109, 2, 7978363/250000]'

    # exif_lat = '[55, 49, 9178619/500000]'
    # exif_log = '[37, 33, 1351593/25000]'

    exif_lat = '[51, 30, 694791 / 12500]'
    exif_log = '[0, 7, 125997 / 12500]'

    exif_lat = '[57, 37, 21361999 / 1000000]'
    exif_log = '[39, 53, 2851593 / 100000]'




    # 12°09'04.9"N 109°02'31.9"E
    # 12.151355, 109.042198

    print get_geo_data(convert_to_degrees(exif_lat, 'N'), convert_to_degrees(exif_log, 'E'))
    #print unicode('Nevşehir')
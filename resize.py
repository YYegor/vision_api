import PIL
from PIL import Image

basewidth = 300

img = Image.open('2017-01-11 13-14-15.JPG')
width, height = img.size
print width, height

wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)

img.save('2017-01-11 13-14-15___small.JPG')
width, height = img.size
print width, height
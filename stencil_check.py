###
## checks an image to see if there are any islands of white pixels
## to verify that it can be cut as a stencil.
## it does not measure line width.
##
## based on code found at:
## http://stackoverflow.com/questions/12321899/how-to-determine-regions-of-pixels-with-a-shared-value-using-pil
###

import functools
import itertools
from PIL import Image, ImageDraw

def closed_regions(image, test):
    """
    Return all closed regions in image who's pixel satisfy test.
    """
    pixel = image.load()
    xs, ys = map(xrange, image.size)
    todo = set(xy for xy in itertools.product(xs, ys) if test(pixel[xy]))
    while todo:
        region = set()
        edge = set([todo.pop()])
        while edge:
            region |= edge
            todo -= edge
            edge = todo.intersection(itertools.chain.from_iterable(
                ((x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)) 
                    for x, y in edge))
        yield region

def boundingbox(coordinates):
    """
    Return the bounding box that contains all coordinates.
    """
    xs, ys = zip(*coordinates)
    return min(xs), min(ys), max(xs), max(ys)

def pixel_is_color(target, pixel):
    #~ (pr, pg, pb), (tr, tg, tb) = pixel, target
    return pixel == target
is_white = functools.partial(pixel_is_color, (255, 255, 255))
is_black = functools.partial(pixel_is_color, (0, 0, 0))

if __name__ == '__main__':
    import sys
    try:
        imgname = sys.argv[1]
    except IndexError as e:
        print "need image"
        exit()
    
    image = Image.open(imgname)
    draw = ImageDraw.Draw(image)
    white_regions = tuple(closed_regions(image, is_white))
    if len(white_regions) > 2:
        print "invalid stencil, {0} background regions".format(len(white_regions)-1)
        for rect in white_regions:
            draw.rectangle(boundingbox(rect), outline=(255, 0, 0))
        image.show()
    else:
        black_regions = tuple(closed_regions(image, is_black))
        print "valid stencil, {0} cuts made in this image".format(len(black_regions))

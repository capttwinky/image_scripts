#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  weaver.py
#  
#  Use Python Image Library to weave an image from a standard draft.
#  
#  © 2015-01-23
#      Joel Mc Grady <capttwinky@github.com>
#  
from itertools import cycle, repeat
from functools import partial
import random
from datetime import datetime
from os.path import abspath

from PIL import Image


def float_map(x, in_min, in_max, out_min, out_max):
    '''returns y where in_min:x:in_max :: out_min:y:out_max'''
    return (x - in_min) * (out_max - out_min) / float(in_max - in_min) + out_min


def int_map(x, in_min, in_max, out_min, out_max):
    '''automatically convert float_map values to ints'''
    return int(round(float_map(x, in_min, in_max, out_min, out_max)))


def gen_int_map(in_max, out_max, in_min=0, out_min=0):
    '''sets up a general integer mapper between two ranges'''
    return partial(int_map, in_min=in_min, in_max=in_max, out_min=out_min, out_max=out_max)


def color_fade(rgb_start, rgb_end, steps=None):
    '''interpolates the rgb values between two triplets, taking the specified
    number of steps, or just taking the greatest number of non-duplicated
    steps'''
    dfade = {}
    for pix_indx, c_name in enumerate(('red','green','blue',)):
        dfade[c_name] = [rgb_end[pix_indx], rgb_start[pix_indx], 
            abs(rgb_end[pix_indx]-rgb_start[pix_indx])]
    max_fade = steps if steps else max(v[2] for v in dfade.values())
    red_map = gen_int_map(max_fade, dfade['red'][0], out_min=dfade['red'][1])
    green_map = gen_int_map(max_fade, dfade['green'][0], out_min=dfade['green'][1])
    blue_map = gen_int_map(max_fade, dfade['blue'][0], out_min=dfade['blue'][1])
    for i in xrange(1, max_fade+1):
        yield (red_map(i), green_map(i), blue_map(i))


def gradient_gen(gradient_list, total_length):
    '''generates a list of rgb values to create the specified gradient
    gradient_list := [(start_as_%_of_total_length, rgb), ...]
        total_length := number of steps total to generate 
    '''
    gradient_list = sorted(gradient_list)
    mints = [gradient_list[i][0] - gradient_list[i-1][0] for i in xrange(1, len(gradient_list))]
    mpcnt = [int(round(c*total_length)) for c in mints]
    mpcnt.append(total_length-sum(mpcnt))
    color_pairs = [(gradient_list[i-1][1], gradient_list[i][1])
        for i in xrange(1,len(gradient_list))]
    for ((rgb_start, rgb_end), steps) in zip(color_pairs, mpcnt):
        for pxl in color_fade(rgb_start, rgb_end, steps):
            yield pxl

def make_test_image(rgbs, height):
    '''make a sample image of the passed in rgb list, of the specified height'''
    img_width = len(rgbs)
    img_height = height
    img = Image.new('RGB', (img_width,img_height), "black") # create a new black image
    pixels = img.load() # create the pixel map
    for i, color_rgb in enumerate(rgbs):    # for every pixel:
        for j in range(height):
            pixels[i,j] = color_rgb # set the colour accordingly
    return img

def make_thread_image(rgbs, repeats=3):
    '''place test images together to show the repeat'''
    to_ret = make_test_image(rgbs, 50)
    if repeats:
        init_width, init_height = to_ret.size
        final_width = init_width * repeats
        final_image = Image.new('RGB',(final_width,init_height), 'black')
        for xoffset in [init_width*i for i in xrange(repeats)]:
            final_image.paste(to_ret, (xoffset, 0))
        to_ret = final_image
    return to_ret


def make_warp_image(rgbs, thread_width, ends, shots, randomize=True):
    '''make the warp image'''
    clist = cycle(rgbs)  ##infinate thread!!
    image_width = thread_width * ends
    image_height = thread_width * shots
    img = Image.new('RGB', (image_width,image_height), "black") # create a new black image
    pixels = img.load() # create the pixel map
    img_col = 0
    for e in xrange(ends):
        thread = [clist.next() for i in xrange(image_height)]
        for i in xrange(thread_width):
            for j in range(image_height):
                pixels[img_col,j] = thread[j]
            img_col+=1
        if randomize and not random.randint(0,5):
            [clist.next() for i in xrange(random.randint(image_height/4, image_height/2))]
    return img


def make_weft_image(rgbs, thread_width, ends, shots, randomize=True):
    clist = cycle(rgbs)
    image_width = thread_width * ends
    image_height = thread_width * shots
    img = Image.new('RGB', (image_width,image_height), "black") # create a new black image
    pixels = img.load() # create the pixel map
    img_row = 0
    for s in xrange(shots):
        thread = [clist.next() for i in xrange(image_width)]
        for i in xrange(thread_width):
            for j in range(image_width):
                pixels[j,img_row] = thread[j] # set the colour accordingly
            img_row+=1
        if randomize and not random.randint(0,10):
            [clist.next() for i in xrange(random.randint(image_width/4, image_width/2))]
    return img


def make_web_image(warp_thread, weft_thread, thread_width, ends, shots, verbose=False):
    image_width = thread_width * ends
    image_height = thread_width * shots
    ## first make the images for the warp & the weft
    weft_image = make_weft_image(weft_thread, thread_width, ends, shots)
    warp_image = make_warp_image(warp_thread, thread_width, ends, shots)
    if verbose:
        weft_image.show()
        warp_image.show()
    weft_pixels = weft_image.load()
    warp_pixels = warp_image.load()

    ## here are some setups for sample weaves:
    ## plain tabby weave 
    #~ headles = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1))
    #~ pedals = [(headles[0],), (headles[1],), (headles[2],), (headles[3],)]
    #~ pedal_steps = ((pedals[1],pedals[3]), (pedals[0],pedals[2],),)
#~ 
    ## plain twill on the headles 
    #~ headles = ((1,1,0,0), (0,1,1,0), (0,0,1,1), (1,0,0,1))
    #~ pedals = [(headles[0],), (headles[1],), (headles[2],), (headles[3],)]
    #~ pedal_steps = ((pedals[0],), (pedals[1],), (pedals[2],), (pedals[3],),)
#~ 
    ## plain twill on the peadles 
    #~ headles = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1))
    #~ pedals = ((headles[0],headles[1],),
                #~ (headles[1],headles[2],),
                #~ (headles[2],headles[3],),
                #~ (headles[3],headles[0],),)
    #~ pedal_steps = ((pedals[0],), (pedals[1],), (pedals[2],), (pedals[3],),)
#~ 
    #~ ## plain twill in the treads 
    #~ headles = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1))
    #~ pedals = [(headles[0],), (headles[1],), (headles[2],), (headles[3],)]
    #~ pedal_steps = ((pedals[0],pedals[1],),
                     #~ (pedals[1],pedals[2],),
                     #~ (pedals[2],pedals[3],),
                     #~ (pedals[3],pedals[0],),)

    ## rosepath III
    #~ headles = ((1,0,1,0,0,0,0,0),
               #~ (0,1,0,0,0,1,0,0),
               #~ (0,0,0,0,1,0,1,0),
               #~ (0,0,0,1,0,0,0,1),)
    #~ pedals = ((headles[0],headles[1],), 
              #~ (headles[1],headles[2],), 
              #~ (headles[2],headles[3],),
              #~ (headles[3],headles[0],),)
    #~ pedal_steps = ((pedals[0],),
                   #~ (pedals[1],),
                   #~ (pedals[0],),
                   #~ (pedals[3],),
                   #~ (pedals[2],),
                   #~ (pedals[1],),
                   #~ (pedals[2],),
                   #~ (pedals[3],),)
#~ 
    #~ ## rosepath, reverse twill treading
    #~ headles = ((1,0,1,0,0,0,0,0),
               #~ (0,1,0,0,0,1,0,0),
               #~ (0,0,0,0,1,0,1,0),
               #~ (0,0,0,1,0,0,0,1),)
    #~ pedals = ((headles[0],headles[1],), 
              #~ (headles[1],headles[2],), 
              #~ (headles[2],headles[3],),
              #~ (headles[3],headles[0],),)
    #~ pedal_steps = ((pedals[0],),
                   #~ (pedals[1],),
                   #~ (pedals[2],),
                   #~ (pedals[3],),
                   #~ (pedals[2],),
                   #~ (pedals[1],),)
    #~ 
    ## honeysuckle 
    headles = ((1,0,0,0, 1,0,1,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 1,0,1,0, 0,0,),
               (0,1,0,0, 0,1,0,1, 0,1,0,0, 0,0,0,0, 0,1,0,1, 0,1,0,0, 0,1,),
               (0,0,1,0, 0,0,0,0, 1,0,1,0, 1,0,1,0, 1,0,1,0, 0,0,0,0, 1,0,),
               (0,0,0,1, 0,0,0,0, 0,0,0,1, 0,1,0,1, 0,0,0,0, 0,0,0,1, 0,0,),
              )
    pedals = ((headles[0],headles[1],), 
              (headles[1],headles[2],), 
              (headles[2],headles[3],),
              (headles[3],headles[0],),)
    pedal_steps = ((pedals[0],),
                   (pedals[1],),
                   (pedals[2],),
                   (pedals[3],),

                   (pedals[0],),
                   (pedals[1],),
                   (pedals[2],),
                   (pedals[3],),
                   
                   (pedals[0],),
                   
                   (pedals[3],),
                   (pedals[2],),
                   (pedals[1],),
                   (pedals[0],),

                   (pedals[3],),
                   (pedals[2],),
                   (pedals[1],),)
 
    ## now set up the treading
    treads = cycle(pedal_steps)
    img = Image.new('RGB', (image_width,image_height), "black") # create a new black image
    pixels = img.load()
    for s in xrange(shots):
        ## get all the headles that are raised in the current step
        lift = sum(treads.next(),tuple())
        ## set the source image list so that it will
        ## show the weft for any raised thread, otherwise the warp
        shed = [weft_pixels if any(h) else warp_pixels for h in zip(*lift)]
        ## copy the pixels from the source image into the final image
        for y in xrange(thread_width):
            ay = thread_width*s+y
            for e in xrange(ends):
                s_row = shed[e%len(shed)]
                for x in xrange(thread_width):
                    ax = thread_width*e+x
                    pixels[ax,ay] = s_row[ax,ay]
        if verbose == 'extra' and s <= 2*len(pedal_steps):
            img.show()
    return img

def main():
    
    ## some test threads
    
    #~ g_list = [(0, (255,255,0)),(.25,(0,128,255)),(.45,(255,0,255)),(.65,(255,0,0)),(.85,(128,0,128)),(.99,(255,255,0))]
    #~ h_list = [(0, (255,255,0)),(.25,(0,128,255)),(.5,(0,128,128)),(.75,(128,0,128)),(.99,(255,255,0))]
    #~ 
    
    ## blue and orange
    #~ h_list = [(0, (255,100,0)),(.5,(0,0,255)),(.99,(255,100,0))]
    
    ## blue red
    h_list = [(0, (255,0,0)),(.5,(0,128,255)),(.99,(255,0,0))]
    
    ## blue orange
    g_list = [(0, (0,128,255,)),(.5,(255,128,0)),(.99,(0,128,255,))]
    
    ## red-magenta-blue
    #~ g_list = [(0, (255,0,0)),(.33,(255,0,255)),(.66,(0,0,255)),(.99,(255,0,0))]
    
    #g_list = [(0, (0,255,0)),(.35,(0,128,255)),(.25,(255,0,255)),(.65,(255,0,0)),(.85,(0,128,255)),(.99,(0,255,0))]
    
    ## show a sample image of the basic draft
    make_web_image(((255,100,0),), ((0,0,255),), 6, 150, 75).show()
    
    ## first make the warp & weft threads
    thread_0 = list(gradient_gen(h_list, 9000))
    thread_1 = list(gradient_gen(g_list, 7000))
    ## pass those threads into make_web_image    
    op_image = make_web_image(thread_1, thread_0, 6, 200, 150, verbose=True)
    ## show the image
    op_image.show()
    if raw_input('type y <enter> to save this image, or just <enter> to quit. ') == 'y':
        image_name = 'weave_{}.png'.format(datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        op_image.save(image_name)
        print "Saved {}".format(abspath('./{}'.format(image_name)))
    
    return 0

if __name__ == '__main__':
    main()

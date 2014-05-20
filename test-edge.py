#! /usr/bin/env python

import os
import sys
import pyfits
import numpy
import math
from PIL import Image

chwid = 10     # check pixel width (half)
rgstep = 5    # rough check step
chthr = 0.1   # threshold for change detection by average

lconv = 0.1044  # um/pixel

ffits = 0;
fdata = 0;
fsize = ();

pngborder = (255, 0, 0)
pngindig  = (0, 0, 255)
pngtick   = 10

def main():
    global fdata, fsize, chwid, rgstep, lconv
    open_fits(sys.argv[1])
#    print '%d' % len(fsize)
    print 'Image size : x %d / y %d' % (fsize[0], fsize[1])
    cpos = (fsize[0] / 2, fsize[1] / 2)
#    print 'X+'
    cret_xp= check_rough((1, 0), cpos, rgstep, chwid)
#    print 'X-'
    cret_xm = check_rough((-1, 0), cpos, rgstep, chwid)
#    print 'Y+'
    cret_yp = check_rough((0, 1), cpos, rgstep, chwid)
#    print 'Y-'
    cret_ym = check_rough((0, -1), cpos, rgstep, chwid)
    emax = numpy.amin((len(cret_xp), len(cret_xm), len(cret_yp), len(cret_ym)))
    if emax > 3:
        emax = 3
    print 'Detected #', emax
    print 'Rough x+  ', cret_xp
    print 'Rough x-  ', cret_xm
    print 'Rough y+  ', cret_yp
    print 'Rough y-  ', cret_ym

# create centers
    cposd = ()
    clen  = ()
    pngls = () # local size
    pngst = () # local start point
    pnghsize = [1 + chwid, 1+ chwid] # half size, full = hsize * 2 + 1
    for cid in range(0, emax):
        cposd = cposd + ((cpos[0] + (cret_xp[cid][0] - cret_xm[cid][0]) / 2, 
                          cpos[1] + (cret_yp[cid][0] - cret_ym[cid][0]) / 2), )
        clen = clen + ((((cret_xp[cid][0] + cret_xm[cid][0]) / 2, 
                         (cret_xp[cid][1] + cret_xm[cid][1]) / 2),
                        ((cret_yp[cid][0] + cret_ym[cid][0]) / 2,
                         (cret_yp[cid][1] + cret_ym[cid][1]) / 2)), )
        pngls = pngls + (((clen[cid][0][1] - clen[cid][0][0]), 
                          (clen[cid][1][1] - clen[cid][1][0])), )
        pnghsize[0] += pngls[cid][0] + 1
        pnghsize[1] += pngls[cid][1] + 1
        if (cid == 0):
            pngst = pngst + ((chwid + 1, chwid + 1), )
        else:
            pngst = pngst + ((pngst[cid - 1][0] + pngls[cid - 1][0] + 1,
                              pngst[cid - 1][1] + pngls[cid - 1][1] + 1), )
    print 'Center pos', cposd
    print 'Trans reg ', clen
# make array for png output
    pngdata = [(255, 255, 255)] * ((pnghsize[0] * 2 + 1) * (pnghsize[1] * 2 + 1))
    print pnghsize
    print pngst
    print pngls
    draw_edge(pnghsize, pngls, pngst, pngdata)
# fine search
    cfine = ()
    for cid in range(0, emax):
        cl_x = clen[cid][0][1] - clen[cid][0][0]
        cl_y = clen[cid][1][1] - clen[cid][1][0]
        cf_xp = check_fine((1, 0), cposd[cid], chwid, clen[cid][0])
        draw_image(pnghsize,
                (cposd[cid][0] + clen[cid][0][0], cposd[cid][1] - chwid), 
                (pnghsize[0] + pngst[cid][0] + 1, pnghsize[1] - chwid),
                (cl_x, chwid * 2 + 1), pngdata)
        cf_xm = check_fine((-1, 0), cposd[cid], chwid, clen[cid][0])
        draw_image(pnghsize,
                (cposd[cid][0] - clen[cid][0][0] - cl_x, cposd[cid][1] - chwid),
                (pnghsize[0] - pngst[cid][0] - cl_x, pnghsize[1] - chwid),
                (cl_x, chwid * 2 + 1), pngdata)
        cf_yp = check_fine((0, 1), cposd[cid], chwid, clen[cid][1])
        draw_image(pnghsize,
                (cposd[cid][0] - chwid, cposd[cid][1] + clen[cid][1][0]),
                (pnghsize[0] - chwid, pnghsize[1] + pngst[cid][1] + 1), 
                (chwid * 2 + 1, cl_y), pngdata)
        cf_ym = check_fine((0, -1), cposd[cid], chwid, clen[cid][1])
        draw_image(pnghsize,
                (cposd[cid][0] - chwid, cposd[cid][1] - clen[cid][1][0] - cl_y),
                (pnghsize[0] - chwid, pnghsize[1] - pngst[cid][1] - cl_y), 
                (chwid * 2 + 1, cl_y), pngdata)
        cf_xd = (cf_xp + cf_xm)
        cf_yd = (cf_yp + cf_ym)
        cf_xc = (cf_xp - cf_xm) / 2
        cf_yc = (cf_yp - cf_ym) / 2
        draw_detect(pnghsize, pngls, pngst, pngdata, cid, 
                cf_xp - clen[cid][0][0] - 1, cf_xm - clen[cid][0][0] - 1,
                cf_yp - clen[cid][1][0] - 1, cf_ym - clen[cid][1][0] - 1)
#        print '%d %d %d %d' % (cf_xp, cf_xm, cf_yp, cf_ym)
        cfine = cfine + ((cf_xd, cf_yd, cf_xc + cposd[cid][0], cf_yc + cposd[cid][1]), )
        print 'DET : dia x = %.1f (%.2f um), y = %.1f (%.2f um) at (%.2f, %.2f)' % (
            cfine[cid][0], cfine[cid][0] * lconv, cfine[cid][1], 
            cfine[cid][1] * lconv, cfine[cid][2], cfine[cid][3])
    if emax > 1:
        print 'De-center'
        print 'core-clad : (%.2f, %.2f) / (%.2f, %.2f) um' % (
          cfine[0][2] - cfine[1][2], cfine[0][3] - cfine[1][3],
          (cfine[0][2] - cfine[1][2]) * lconv,
          (cfine[0][3] - cfine[1][3]) * lconv)
    if emax > 2:
        print 'core-buff : (%.2f, %.2f) / (%.2f, %.2f) um' % (
          cfine[0][2] - cfine[2][2], cfine[0][3] - cfine[2][3],
          (cfine[0][2] - cfine[2][2]) * lconv,
          (cfine[0][3] - cfine[2][3]) * lconv)
    close_fits()
    draw_center(pnghsize, pngdata)
    save_png(pnghsize, pngdata)

def check_fine(cdir, cpos, check, clen):
    global fdata
    cl = ((cpos[0] - check * abs(cdir[1]), cpos[0] + check * abs(cdir[1]) + 1), 
          (cpos[1] - check * abs(cdir[0]), cpos[1] + check * abs(cdir[0]) + 1))
    cavg = 0
    cdiff = ()
    for shift in range(clen[0], clen[1]):
        cavg_new = numpy.mean(
            fdata[cl[0][0] + shift * cdir[0] : cl[0][1] + shift * cdir[0],
                  cl[1][0] + shift * cdir[1] : cl[1][1] + shift * cdir[1]])
#        print '%d : %f / %f' % (shift, cavg_new, (cavg_new - cavg))
        if (cavg != 0):
            cdiff = cdiff + (cavg_new - cavg,)
        cavg = cavg_new
    cdir = numpy.mean(cdiff)
    cdir = cdir / abs(cdir)
    cmax = 0
    cid = 0
    for shift in range(0, len(cdiff)):
        if (cmax < cdiff[shift] * cdir):
            cmax = cdiff[shift] * cdir
            cid = shift
    return cid + clen[0] + 1

def check_rough(cdir, cpos, step, check):
    global fdata, chthr
    cl = ((cpos[0] - check, cpos[0] + check + 1),
          (cpos[1] - check, cpos[1] + check + 1))
    cavg_orig = numpy.mean(fdata[cl[0][0] : cl[0][1], cl[1][0] : cl[1][1]])
    cret = ()
#    print '%f / %f' % (cavg_orig, fdata[cpos[0], cpos[1]])
    shift = 0
    cavg = cavg_orig
    start = 0
    shift_max = abs(cdir[0] * cpos[0] + cdir[1] * cpos[1]) - check
    while shift < shift_max:
        cavg_new = numpy.mean(
            fdata[cl[0][0] + shift * cdir[0] : cl[0][1] + shift * cdir[0],
                  cl[1][0] + shift * cdir[1] : cl[1][1] + shift * cdir[1]])
        if (abs(cavg_new - cavg) / cavg > chthr):
            if (start == 0):
#                print '++ %d (old %f / new %f / %f %f)' % (shift, cavg, 
#                     cavg_new, cavg - cavg_new, (cavg - cavg_new) / cavg)
                start = shift
#            else:
#                print '+= %d (old %f / new %f / %f %f)' % (shift, cavg, 
#                     cavg_new, cavg - cavg_new, (cavg - cavg_new) / cavg)
        elif (start != 0):
            cret = cret + ((start - step, shift), )
            start = 0
        cavg = cavg_new
        shift += step
    return cret

# copy fdata[fitsorg - size] -> data[pngorg - size]
# fitsorg = origin at FITS image
def draw_image(hsize, fitsorg, pngorg, size, data):
    global fdata, fsize
    wid = hsize[0] * 2 + 1
    freg = fdata[fitsorg[0] : fitsorg[0] + size[0],
                 fitsorg[1] : fitsorg[1] + size[1]]
    fmin = numpy.amin(freg)
    fmax = numpy.amax(freg)
    cl = wid * pngorg[1] + pngorg[0]
    print 'Color:', fmin, fmax, fitsorg, size
    for cy in range(0, len(freg[0])):
        for cx in range(0, len(freg)):
            val = make_color(freg[cx][cy], fmin, fmax)
            data[cl + cx] = (val, val, val)
        cl += wid

# color 255 = white
def make_color(val, fmin, fmax):
    if (val <= fmin):
        return 0
    if (val >= fmax):
        return 255
    return int(math.floor((val - fmin) / (fmax - fmin) * 256))

def draw_detect(hsize, ls, lst, data, cid, xp, xm, yp, ym):
    wid = hsize[0] * 2 + 1
    # tick - X
    cl1 = (hsize[1] - lst[0][1]) * wid + hsize[0]
    cl2 = (hsize[1] + lst[0][1]) * wid + hsize[0]
    for cin in range(0, pngtick):
        data[cl1 + xp + 1 + lst[cid][0] - cin * wid] = pngindig
        data[cl2 + xp + 1 + lst[cid][0] + cin * wid] = pngindig
        data[cl1 - xm - 1 - lst[cid][0] - cin * wid] = pngindig
        data[cl2 - xm - 1 - lst[cid][0] + cin * wid] = pngindig
    # tick - Y
    cl1 = (hsize[1] - lst[cid][1] - ym - 1) * wid + hsize[0]
    cl2 = (hsize[1] + lst[cid][1] + yp + 1) * wid + hsize[0]
    for cin in range(0, pngtick):
        data[cl1 - lst[0][0] - cin] = pngindig
        data[cl1 + lst[0][0] + cin] = pngindig
        data[cl2 - lst[0][0] - cin] = pngindig
        data[cl2 + lst[0][0] + cin] = pngindig

def draw_center(hsize, data):
    wid = hsize[0] * 2 + 1
    cl1 = hsize[1] * wid
    for cin in range(0, wid):
        data[cl1 + cin] = (128, 128, 128)
    cl1 = hsize[0]
    for cin in range(0, hsize[1] * 2 + 1):
        data[cl1] = (128, 128, 128)
        cl1 += wid

#    pngls = () # local size
#    pngst = () # local start point
#    pnghsize = [1 + chwid, 1+ chwid] # half size, full = hsize * 2 + 1
def draw_edge(hsize, ls, lst, data):
    global chwid
    wid = hsize[0] * 2 + 1
    # draw long lines - side of X
    cl1 = (hsize[1] - lst[0][1]) * wid
    cl2 = (hsize[1] + lst[0][1]) * wid
    for cin in range(0, wid):
        # (cid, hsize[1] * 2 + ls[0][1] + 1)
        data[cl1 + cin] = pngborder
        data[cl2 + cin] = pngborder
    # draw long lines - side of Y
    cl1 = hsize[0] - lst[0][0]
    cl2 = hsize[0] + lst[0][0]
    for cin in range(0, hsize[1] * 2 + 1):
        data[cl1] = pngborder
        data[cl2] = pngborder
        cl1 += wid
        cl2 += wid
    # draw separation - X
    cl1 = (hsize[1] - lst[0][1] + 1) * wid + hsize[0]
    for cin in range(0, chwid * 2 + 1):
        for cl2 in range(1, len(lst)):
            data[cl1 + lst[cl2][0] + cin * wid] = pngborder
            data[cl1 - lst[cl2][0] + cin * wid] = pngborder
        data[cl1 + hsize[0] + cin * wid] = pngborder
        data[cl1 - hsize[0] + cin * wid] = pngborder
    # draw separation - Y
    cl1 = hsize[0] - lst[0][0] + 1
    for cin in range(0, chwid * 2 + 1):
        for cl2 in range(1, len(lst)):
            data[(hsize[1] - lst[cl2][1]) * wid + cl1 + cin] = pngborder
            data[(hsize[1] + lst[cl2][1]) * wid + cl1 + cin] = pngborder
        data[cl1 + cin] = pngborder
        data[hsize[1] * 2 * wid + cl1 + cin] = pngborder

def save_png(hsize, data):
    if (len(data) != (hsize[0] * 2 + 1) * (hsize[1] * 2 + 1)): 
        return -1
    timg = Image.new('RGB', (hsize[0] * 2 + 1, hsize[1] * 2 + 1))
    timg.putdata(data)
    timg.save(sys.argv[1] + '.png', 'PNG')
    return 0

def open_fits(fname):
    global ffits, fdata, fsize
    ffits = pyfits.open(fname)
    fdata = ffits[0].data
    fsize = fdata.shape

def close_fits():
    global ffits
    # need to do something?
    ffits.close()

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print '%s <fits-name>' % sys.argv[1]
        exit
    main()



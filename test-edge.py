#! /usr/bin/env python

import os
import sys
import pyfits
import numpy

chwid = 5     # check pixel width (half)
rgstep = 5    # rough check step
chthr = 0.05   # threshold for change detection by average

lconv = 0.1044  # um/pixel

ffits = 0;
fdata = 0;
fsize = ();

def main():
    global fdata, fsize
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
    for cid in range(0, emax):
        cposd = cposd + ((cpos[0] + (cret_xp[cid][0] - cret_xm[cid][0]) / 2, 
                          cpos[1] + (cret_yp[cid][0] - cret_ym[cid][0]) / 2), )
        clen = clen + ((((cret_xp[cid][0] + cret_xm[cid][0]) / 2, 
                         (cret_xp[cid][1] + cret_xm[cid][1]) / 2),
                        ((cret_yp[cid][0] + cret_ym[cid][0]) / 2,
                         (cret_yp[cid][1] + cret_ym[cid][1]) / 2)), )
    print 'Center pos', cposd
    print 'Trans reg ', clen
# fine search
    cfine = ()
    for cid in range(0, emax):
        cf_xp = check_fine((1, 0), cposd[cid], chwid, clen[cid][0])
        cf_xm = check_fine((-1, 0), cposd[cid], chwid, clen[cid][0])
        cf_yp = check_fine((0, 1), cposd[cid], chwid, clen[cid][1])
        cf_ym = check_fine((0, -1), cposd[cid], chwid, clen[cid][1])
        cf_xd = (cf_xp + cf_xm)
        cf_yd = (cf_yp + cf_ym)
        cf_xc = (cf_xp - cf_xm) / 2
        cf_yc = (cf_yp - cf_ym) / 2
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

def open_fits(fname):
    global ffits, fdata, fsize
    ffits = pyfits.open(fname)
    fdata = ffits[0].data
    fsize = fdata.shape

def close_fits():
    # need to do something?
    ffits.close()

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print '%s <fits-name>' % sys.argv[1]
        exit
    main()



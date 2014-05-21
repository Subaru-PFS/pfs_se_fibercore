
# Algorithm

  This script will measure center and diameter for core/clad/buffer in two phases.
  First phase is rough transitional region detection, and second phase is somewhat
fine detection of boundary.
  At first phase, starting from the center of image, with four straight rectangular
coordinates - X+, X-, Y+, Y-
* script will calculate a moving average of square regions with a configured size by step of a configured step
* mark centers of regions as 'transitional region' whose average changed more than a configured ratio from last step
* make consecutive 'transitional region' centers as one transitional region
* mark transitional regions as boundaries of core/clad, clad/buffer, buffer/outer(air), from innermost
  After first phase, script will get up to twelve (three regions for four directions)
detected regions, and calculate new center positions per each boundary.
* if number of detected regions are less than three, assign boundary IDs from inner (e.g. first for core/clad)
     un-assigned boundary IDs will be marked as non-detection (and be not checked further)
* calculate new center position for search to be started with, as average of innermost of four regions
     if regions are 640-800 and 700-800, new center position will be 670 - average of 640 and 700
* calculate new search regions as averages of inner and outer of regions
     if regions are 640-800 and 700-800, new search region will be 670-800
  After this, script will have rough calculated center positions and search regions
for both X and Y, per each boundary (up to 3), and starts second phase
* calculate a moving average of string regions with a configured size (1 x size) by step of 1
* make an array of moving difference, and mark largest one as boundary
* calculate center position as average of boundary points
  After second phase, script will get centers and diameters for three boundaries in X and Y.


# Configurable parameters

* chwid : region width (1 + 2 * chwid) to calcurate average (both axis for rough)
* rgstep : step size to move region center during rough phase
* chthr : threshold to mark as transitional region during rough phase
* detsat : saturation detection threshold
* glog : global log file (adding one line per run)
* lconv : conversion parameter of um/pixel
* pngborder : border color of each cripped image
* pngindig : tick color
* pngtick : tick length


# Sample output

% ./test-edge.py Fujikura6_polish_1.fit
Image size : x 2049 / y 2447
Detected # 3
Rough x+   ((635, 670), (820, 865), (930, 990))
Rough x-   ((580, 610), (785, 820), (845, 880))
Rough y+   ((620, 655), (805, 860), (890, 950))
Rough y-   ((595, 625), (795, 820), (855, 885))
Center pos ((1051, 1235), (1041, 1228), (1066, 1240))
Trans reg  (((607, 640), (607, 640)), ((802, 842), (800, 840)), ((887, 935), (872, 917)))
DET : dia x = 1236.0 (129.04 um), y = 1237.0 (129.14 um) at (1053.00, 1239.00)
DET : dia x = 1638.0 (171.01 um), y = 1617.0 (168.81 um) at (1043.00, 1229.00)
DET : dia x = 1818.0 (189.80 um), y = 1795.0 (187.40 um) at (1065.00, 1250.00)
De-center
core-clad : (10.00, 10.00) / (1.04, 1.04) um
core-buff : (-12.00, -11.00) / (-1.25, -1.15) um


% ./test-edge.py Polymicro_polish_2.fit
Image size : x 2049 / y 2447
Detected # 3
Rough x+   ((525, 550), (755, 790), (835, 900), (920, 940))
Rough x-   ((610, 635), (845, 875), (935, 1000))
Rough y+   ((550, 580), (780, 825), (850, 905), (985, 1030))
Rough y-   ((580, 605), (810, 835), (895, 955))
Center pos ((981, 1208), (979, 1208), (974, 1200))
Trans reg  (((567, 592), (565, 592)), ((800, 832), (795, 830)), ((885, 950), (872, 930)))
DET : dia x = 1148.0 (119.85 um), y = 1156.0 (120.69 um) at (980.00, 1214.00)
DET : dia x = 1616.0 (168.71 um), y = 1605.0 (167.56 um) at (979.00, 1213.00)
DET : dia x = 1858.0 (193.98 um), y = 1822.0 (190.22 um) at (987.00, 1194.00)
De-center
core-clad : (1.00, 1.00) / (0.10, 0.10) um
core-buff : (-7.00, 20.00) / (-0.73, 2.09) um


(Note: conversion factor is wrong for next)
% ./test-edge.py Fujikura_clad1.fit
Image size : x 2049 / y 2447
Detected # 3
Rough x+   ((605, 635), (795, 830), (875, 890), (890, 905), (910, 925))
Rough x-   ((575, 605), (755, 785), (855, 885))
Rough y+   ((580, 615), (820, 845), (845, 870))
Rough y-   ((600, 630), (790, 805), (850, 870))
Center pos ((1039, 1213), (1044, 1238), (1034, 1220))
Trans reg  (((590, 620), (590, 622)), ((775, 807), (805, 825)), ((865, 887), (847, 870)))
DET : dia x = 1197.0 (124.97 um), y = 1197.0 (124.97 um) at (1038.00, 1213.00)
DET : dia x = 1571.0 (164.01 um), y = 1632.0 (170.38 um) at (1047.00, 1236.00)
DET : dia x = 1757.0 (183.43 um), y = 1721.0 (179.67 um) at (1027.00, 1216.00)
De-center
core-clad : (-9.00, -23.00) / (-0.94, -2.40) um
core-buff : (11.00, -3.00) / (1.15, -0.31) um


(Note: conversion factor is wrong for next)
% ./test-edge.py Ploymicro_clad2.fit
Image size : x 2049 / y 2447
Detected # 2
Rough x+   ((550, 590), (755, 770), (775, 800), (845, 910))
Rough x-   ((565, 605), (815, 890))
Rough y+   ((575, 610), (820, 905))
Rough y-   ((545, 605), (810, 890))
Center pos ((1016, 1238), (994, 1228))
Trans reg  (((557, 597), (560, 607)), ((785, 830), (815, 897)))
DET : dia x = 1129.0 (117.87 um), y = 1130.0 (117.97 um) at (1015.00, 1239.00)
DET : dia x = 1635.0 (170.69 um), y = 1766.0 (184.37 um) at (982.00, 1234.00)
De-center
core-clad : (33.00, 5.00) / (3.45, 0.52) um

# PNG image output

PNG image of second phase will be saved as <fits_name>.png, contains cripped 
images of regions used at second phase calculation. Note, output images are 90 
degree crockwise rotated respected to DS9 display. Gray scaled images are 
scaled by minimum value to black and maximum value to white, and blue ticks 
mark detected positions. Central gray lines (one each for vertical and 
horizontal) is gray (128) in the middle of black and white for reference.


# Outstanding issues and unimplemented features

* output OK/NG for detection
* poor failure detection (miss detection of transtional regions)
* check contrast of image (and refine configurations if possible?)

## Boundary detection algorithm

  Currently, this script takes 'largest moving difference' as boundary, but moving
difference are not so smooth (see attached; using core/clad, Fujikura6_polish_1.fit;
green circles are marked as boundary).
  A pixel size of current system is small (a level of 0.1um/pixel) and might be
over-sampling, so broad transitions could be from diffraction limited.

## More directions for fine search phase

  As for now, script only searches to X and Y direction. With increasing directions
from 4 (per 90 degree) to 8 (per 45 degree), we might be possible to check ellipticity.


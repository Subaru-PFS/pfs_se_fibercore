# :%s/template/filename/g

set out 'template.xp.png'
set term png
set lmargin 8
set rmargin 2
set xrange [0:120]
set multiplot layout 3,1
unset xtics
set tmargin 0.5
set bmargin 0
plot 'template.log' every :4::0 u ($2+column(-2)*40):($3) w l title 'Raw count'
plot 'template.log' every :4::0 u ($2+column(-2)*40):($4) notitle, 'template.log' every :4::0 u ($2+column(-2)*40):($5) notitle
set xtics
unset tmargin
unset bmargin
plot 'template.log' every :4::0 u ($2+column(-2)*40):($4/$5) notitle
unset multiplot
reread
set out

set out 'template.xm.png'
set term png
set lmargin 8
set rmargin 2
set xrange [0:120]
set multiplot layout 3,1
unset xtics
set tmargin 0.5
set bmargin 0
plot 'template.log' every :4::1 u ($2+column(-2)*40):($3) w l title 'Raw count'
plot 'template.log' every :4::1 u ($2+column(-2)*40):($4) notitle, 'template.log' every :4::1 u ($2+column(-2)*40):($5) notitle
set xtics
unset tmargin
unset bmargin
plot 'template.log' every :4::1 u ($2+column(-2)*40):($4/$5) notitle
unset multiplot
reread
set out

set out 'template.yp.png'
set term png
set lmargin 8
set rmargin 2
set xrange [0:120]
set multiplot layout 3,1
unset xtics
set tmargin 0.5
set bmargin 0
plot 'template.log' every :4::2 u ($2+column(-2)*40):($3) w l title 'Raw count'
plot 'template.log' every :4::2 u ($2+column(-2)*40):($4) notitle, 'template.log' every :4::2 u ($2+column(-2)*40):($5) notitle
set xtics
unset tmargin
unset bmargin
plot 'template.log' every :4::2 u ($2+column(-2)*40):($4/$5) notitle
unset multiplot
reread
set out

set out 'template.ym.png'
set term png
set lmargin 8
set rmargin 2
set xrange [0:120]
set multiplot layout 3,1
unset xtics
set tmargin 0.5
set bmargin 0
plot 'template.log' every :4::3 u ($2+column(-2)*40):($3) w l title 'Raw count'
plot 'template.log' every :4::3 u ($2+column(-2)*40):($4) notitle, 'template.log' every :4::3 u ($2+column(-2)*40):($5) notitle
set xtics
unset tmargin
unset bmargin
plot 'template.log' every :4::3 u ($2+column(-2)*40):($4/$5) notitle
unset multiplot
reread
set out

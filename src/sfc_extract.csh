#!/bin/tcsh

set i=1

foreach f (../downloads/*nc)

echo $i, $f

ncks -O -h -d siglay,0 -d siglev,0 -v aice,vice,tsfc,temp,lon,lat,nv,lonc,latc,h,Times $f ../sfc_subset/`basename $f .nc`.sfc.nc

set i=`echo $i | awk '{printf("%d",$1+1)}'`

end








#!/bin/sh


module load nco

date


# FVCOM output files
output_erie="./nos.leofs.2022122213Z-2612Z.sfc.nc"
output_mh="./nos.lmhofs.2022122213Z-2612Z.sfc.nc"
output_sup="./nos.lsofs.2022122213Z-2612Z.sfc.nc"
output_ont="./nos.loofs.2022122213Z-2612Z.sfc.nc"


## extract GL mask variables
echo 'Copying a file for GL mask on RRFS grid ...'
cp fv3mask_C3463.nc ./tmp.nc


# get time info
echo
echo 'getting time information from a FVCOM output file...'
samplefn=$output_erie
echo $samplefn
ncks -O -h -v time,Times $samplefn time.nc
ncrename -O -h -d time,Time time.nc # rename
ncks -h -A time.nc tmp.nc # append
ncdump -v Times tmp.nc | tail -52
rm time.nc


echo 'adding variables (blank for now) to output file ...'
date
## add a variable container for tsfc
echo ''
echo 'adding variables (blank for now) to output file ...'
ncap2 -O -h -s 'twsfc[$Time,$lat,$lon]=glmask' tmp.nc out_fv3grid.nc

echo 1 `date`
ncatted -O -h -a long_name,twsfc,o,c,water_surface_temperature out_fv3grid.nc
ncatted -O -h -a units,twsfc,o,c,degC out_fv3grid.nc
ncatted -O -h -a description,twsfc,o,c,"water surface temperature" out_fv3grid.nc
#date
ncap2 -O -h -s 'tisfc[$Time,$lat,$lon]=glmask' out_fv3grid.nc out_fv3grid.nc
ncatted -O -h -a long_name,twsfc,o,c,water_surface_temperature out_fv3grid.nc
ncatted -O -h -a long_name,tisfc,o,c,ice_surface_temperature out_fv3grid.nc
ncatted -O -h -a units,tisfc,o,c,degC out_fv3grid.nc
ncatted -O -h -a description,tisfc,o,c,"ice surface temperature" out_fv3grid.nc
#date
ncap2 -O -h -s 'aice[$Time,$lat,$lon]=glmask' out_fv3grid.nc out_fv3grid.nc
ncatted -O -h -a long_name,aice,o,c,ice_concentration out_fv3grid.nc
ncatted -O -h -a units,aice,o,c,- out_fv3grid.nc
ncatted -O -h -a description,aice,o,c,"ice fraction [0-1]" out_fv3grid.nc
#date

ncap2 -O -h -s 'vice[$Time,$lat,$lon]=glmask' out_fv3grid.nc out_fv3grid.nc
ncatted -O -h -a long_name,vice,o,c,mean_ice_volume out_fv3grid.nc
ncatted -O -h -a units,vice,o,c,m out_fv3grid.nc
ncatted -O -h -a description,vice,o,c,"mean ice volume [m]" out_fv3grid.nc


#date
ncap2 -O -h -s 'tsfc[$Time,$lat,$lon]=glmask' out_fv3grid.nc out_fv3grid.nc
ncatted -O -h -a long_name,tsfc,o,c,lake_skin_temperature out_fv3grid.nc
ncatted -O -h -a units,tsfc,o,c,degC out_fv3grid.nc
ncatted -O -h -a description,tsfc,o,c,"skin temperature of lake and ice surfaces (weighted-mean based on ice concentration)" out_fv3grid.nc
echo 2 `date`

# edit mask attributes
ncatted -O -h -a description,glmask,o,c,'Great Lakes mask (1 if overwater 0 otherwise)' out_fv3grid.nc
echo 3 `date`



# run interpolation script
echo
echo 'now running the Python script for remapping ...'
date

echo $output_erie $output_mh $output_sup $output_ont
python3 ./interp_skintemp_5lakes_ice_fv3grid_ver7.py $output_erie $output_mh $output_sup $output_ont > python.log

cat python.log
if [ "`tail -1 python.log`" != "interp_skintemp_5lakes_ice_fv3grid_ver7.py completed successfully" ]
then
   echo 'Problem with interp_skintemp_5lakes_ice_fv3grid_ver7.py - ABORT'
   date
   exit
fi
date



# remove time dimension from mask, lon&lat info.
#ncwa -O -h -v LAKEMASK -a Time  out_fv3grid.nc maskinfo.nc
# extract skin temp info
ncks -O -h -v geolon,geolat,glmask,twsfc,tisfc,aice,vice,tsfc,time,Times out_fv3grid.nc tsfc_fv3grid.nc
ncap2 -O -s 'geolon=double(geolon);geolat=double(geolat);time=double(time)' tsfc_fv3grid.nc tsfc_fv3grid.nc
echo 'skin temp info extracted'

#exit

# remove temporary files
echo
echo 'removing temporary files...'
rm tmp.nc out_fv3grid.nc



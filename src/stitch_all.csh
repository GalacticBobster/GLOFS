#!/bin/csh

set ofsname = "lsofs"
set out_file = "nos.${ofsname}.stitched.sfc.nc"

# Get all matching files
set file_list = ( `ls ../sfc_subset/*${ofsname}*sfc.nc` )

# Check if any files found
if ( $#file_list == 0 ) then
    echo "No matching files found for ${ofsname}"
    exit 1
endif

# Report number of files
echo "📦 Running ncrcat on $#file_list files..."

# Run ncrcat
ncrcat -O -h $file_list $out_file

echo "Output file created: $out_file"


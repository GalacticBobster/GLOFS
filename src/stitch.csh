#!/bin/tcsh

# Stitch individual files in time for Dec 22 13Z, 2022 - Dec 26 12Z, 2022

#set ofsname="lmhofs"
#set ofsname="leofs"
#set ofsname="lsofs"
set ofsname="loofs"


ncrcat -O -h  sfc_subset/nos.${ofsname}.fields.n00[1,2,3,4,5].20221222.t18z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221223.t00z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221223.t06z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221223.t12z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221223.t18z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221224.t00z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221224.t06z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221224.t12z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221224.t18z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221225.t00z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221225.t06z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221225.t12z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221225.t18z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221226.t00z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221226.t06z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n00[0-5].20221226.t12z_sfc.nc  \
             sfc_subset/nos.${ofsname}.fields.n000.20221226.t18z_sfc.nc  \
             nos.${ofsname}.2022122213Z-2612Z.sfc.nc






#!/bin/bash

echo Write frequency channel:
read channel

echo Write group directory:
read group

echo Write declination:
read declination

#ssh -i ${GXSSH} man318@venice.atnf.csiro.au "mkdir -p /DATA/CARINA_5/man318/idg/Dec${declination}/$group"
#ssh -i ${GXSSH} man318@venice.atnf.csiro.au "mkdir -p /DATA/CARINA_5/man318/idg/Dec${declination}/$group/$channel"

arr=()
while IFS= read -r data; do arr+=("$data"); done < all.txt
for element in ${arr[@]}; 
do
    # Copying calibration plots to Carina
    #ssh -i ${GXSSH} man318@venice.atnf.csiro.au "mkdir -p /DATA/CARINA_5/man318/idg/Dec${declination}/$group/$channel/$element"
    cd "$element"
    rsync -rvp -e "ssh -i ${GXSSH}" *.png smantovanini@garrawarla.pawsey.org.au:/scratch/pawsey0272/smantovanini/IDG/GalacticPlane/Dec$declination/$group/$channel/$element/ 
    #rsync -rvp -e "ssh -i ${GXSSH}" *.png man318@venice.atnf.csiro.au:/DATA/CARINA_5/man318/idg/Dec$declination/$group/$channel/$element/
    cd ..
done

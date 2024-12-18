#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=workq
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=19
#SBTACH --mem=150G

module load singularity

for file in Epoch00??.fits
do
    if [[ ! -e ${file%.fits}_nan.fits ]]
    then
        singularity exec $GXCONTAINER python ./nan_pix.py $file
    fi
    singularity exec $GXCONTAINER BANE --noclobber ${file%.fits}_nan.fits
done

singularity exec $GXCONTAINER swarp -c galcar_weighted.swarp *nan.fits

#! /bin/bash

usage()
{
echo "obs_priorized_catalogue.sh [-p project] [-d dep] [-t] [-m mosaicdir] [-c comb_freq] -n mosaic_name
  -p project  : project, (must be specified, no default)
  -d dep      : job number for dependency (afterok)
  -t          : test. Don't submit job, just make the batch file
                and then return the submission command  
  -m mosaicdir: Directory name where mosaics stored (default=project/mosaic) 
  -c priorcat : Name of the catalogue to use for prior fits (default=mosaicnm_170-231MHz_comp_rescaled.fits depending on extension)
  -e extension : Extension for hte image name (e.g ddmod for blur corrected) (default=none)
  -n mosaicnm : Name of the mosaic, typically the drift name e.g. XG_D-27_20201015 (no default, must be specified)" 1>&2;
exit 1;
}

pipeuser=$(whoami)

# initial variables 
dep=
queue="-p ${GXSTANDARDQ}"
tst=
mosaicdir=
prior_cat=
extension=
# parse args and set options
while getopts ':td:p:m:c:e:n:' OPTION
do
    case "$OPTION" in
    d)
        dep=${OPTARG} ;;
    p)
        project=${OPTARG} ;;
    m) 
        mosaicdir=${OPTARG} ;;
    e)
        extension=${OPTARG} ;;
    t)
        tst=1 ;;
    c)
        prior_cat=${OPTARG} ;;
    n)
        mosaicnm=${OPTARG} ;;
    ? | : | h)
            usage ;;
  esac
done

if [[ -z ${project} ]] || [[ -z ${mosaicnm} ]]
then
    usage
fi

if [[ ! -z ${dep} ]]
then
    depend="--dependency=afterok:${dep}"
fi

if [[ ! -z ${GXACCOUNT} ]]
then
    account="--account=${GXACCOUNT}"
fi

base="${GXSCRATCH}/${project}"
listbase=$(basename "${mosaicnm}")
listbase=${listbase%%.*}

script="${GXSCRIPT}/priorized_catalogue_${listbase}.sh"

cat "${GXBASE}/templates/priorized_catalogue.tmpl" | sed -e "s:BASEDIR:${base}:g" \
                                                -e "s:PIPEUSER:${pipeuser}:g" \
                                                -e "s:MOSAICNM:${mosaicnm}:g" \
                                                -e "s:MOSAICDIR:${mosaicdir}:g" \
                                                -e "s:EXTENSION:${extension}:g" \
                                                -e "s:PRIORCAT:${prior_cat}:g" > ${script}

output="${GXLOG}/priorized_catalogue_${listbase}.o%A_%a"
error="${GXLOG}/priorized_catalogue_${listbase}.e%A_%a"

chmod 755 "${script}"

# sbatch submissions need to start with a shebang
echo '#!/bin/bash' > "${script}.sbatch"
echo "srun --cpus-per-task=${GXNCPUS} --ntasks=1 --ntasks-per-node=1 singularity run ${GXCONTAINER} ${script}" >> "${script}.sbatch"

# Automatically runs a job array for each sub-band
sub="sbatch  --begin=now+20minutes --array=0-24  --export=ALL  --time=10:00:00 --mem=${GXABSMEMORY}G -M ${GXCOMPUTER} --output=${output} --error=${error}"
sub="${sub} ${GXNCPULINE} ${account} ${GXTASKLINE} ${depend} ${queue} ${script}.sbatch"
if [[ ! -z ${tst} ]]
then
    echo "script is ${script}"
    echo "submit via:"
    echo "${sub}"
    exit 0
fi

# submit job
jobid=($(${sub}))
jobid=${jobid[3]}

# rename the err/output files as we now know the jobid
error=${error//%A/"${jobid}"}
output=${output//%A/"${jobid}"}

echo "Submitted ${script} as ${jobid} . Follow progress here:"
# record submission
for taskid in $(seq 1 1 24)
do
    terror="${error//%a/${taskid}}"
    toutput="${output//%a/${taskid}}"
    subchan=${subchans[$taskid]}

    echo "${toutput}"
    echo "${terror}"

done 

#! /bin/bash

usage()
{
echo "obs_download.sh [-p project] [-d dep] [-s timeave] [-k freqav] [-t] -c channel -r ramin -R ramax -m decmin -M decmax
  -d dep      : job number for dependency (afterok)
  -p project  : project, (must be specified, no default)
  -s timeres  : time resolution in sec. default = 2 s
  -k freqres  : freq resolution in KHz. default = 40 kHz
  -f edgeflag : number of edge band channels flagged. default = 80
  -g          : download gpubox fits files instead of measurement sets
  -t          : test. Don't submit job, just make the batch file
                and then return the submission command
  -c channel  : the channel of the obsids to process
  -r ramin    : minimum ra to use
  -R ramax    : maximum ra to use
  -m decmin   : minimum dec to use
  -M decmax   : maximum dec to use" 1>&2;
exit 1;
}

# Supercomputer options
# Hardcode for downloading
if [ ! -z $GXCOPYA ] 
then
    account="--account ${GXCOPYA}"
fi
#standardq="${GXCOPYQ}"

pipeuser=$(whoami)

#initial variables
dep=
#queue="-p $standardq"
tst=
gpubox=
timeres=
freqres=
edgeflag=80

# parse args and set options
while getopts ':tgd:p:s:k:c:r:R:m:M:f:e:' OPTION
do
    case "$OPTION" in
    d)
        dep=${OPTARG} ;;
    p)
        project=${OPTARG} ;;
	s)
	    timeres=${OPTARG} ;;
	k)
	    freqres=${OPTARG} ;;
	c)
	    channel=${OPTARG} ;;
	r)
            ramin=${OPTARG} ;;
	R)
            ramax=${OPTARG} ;;
	m)
            decmin=${OPTARG} ;;
	M)
            decmax=${OPTARG} ;;
    t)
        tst=1 ;;
    g)
        gpubox=1 ;;
    f)
        edgeflag=${OPTARG} ;;
    ? | : | h)
            usage ;;
  esac
done

# if channel and coordinates are not specified or an empty file then just print help
if [[ -z ${channel} ]] || [[ -z ${ramin} ]] || [[ -z ${ramax} ]] || [[ -z ${decmin} ]] || [[ -z ${decmax} ]]
then
    usage
fi


if [[ ! -z ${dep} ]]
then
    depend="--dependency=afterok:${dep}"
fi

listbase=$(basename ${ramin})
#listbase=${listbase%%.*}
script="${GXSCRIPT}/download_${listbase}.sh"

cat "${GXBASE}/templates/download.tmpl" | sed -e "s:CHANNEL:${channel}:g" \
                                 -e "s:STEM:${stem}:g"  \
                                 -e "s:TRES:${timeres}:g" \
                                 -e "s:FRES:${freqres}:g" \
                                 -e "s:BASEDIR:${base}:g" \
				 -e "s:RAMIN:${ramin}:g" \
				 -e "s:EDGEFLAG:${edgeflag}:g" \
				 -e "s:RAMAX:${ramax}:g" \
				 -e "s:DECMIN:${decmin}:g" \
				 -e "s:DECMAX:${decmax}:g" \
                                 -e "s:PIPEUSER:${pipeuser}:g" > "${script}"

output="${GXLOG}/download_${listbase}.o%A"
error="${GXLOG}/download_${listbase}.e%A"

chmod 755 "${script}"

# sbatch submissions need to start with a shebang
echo '#!/bin/bash' > "${script}.sbatch"
echo "export MWA_ASVO_API_KEY='97f4a9da-34e6-489e-810f-aa45e32acecc'" >> "${script}.sbatch"
#echo "module load singularity" >> "${script}.sbatch"
echo "srun --export=all singularity run ${GXCONTAINER} ${script}" >> "${script}.sbatch"

# This is the only task that should reasonably be expected to run on another cluster. 
# Export all GLEAM-X pipeline configurable variables and the MWA_ASVO_API_KEY to ensure 
# obs_mantra completes as expected
sub="sbatch --begin=now+1minutes --mem=10G --export=$(echo ${!GX*} | tr ' ' ','),MWA_ASVO_API_KEY,SINGULARITY_BINDPATH  --time=08:00:00 -M ${GXCOPYM} --output=${output} --error=${error}"
sub="${sub} ${depend} ${account} ${script}.sbatch"

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
error="${error//%A/${jobid[0]}}"
output="${output//%A/${jobid[0]}}"

# record submission
n=1
for obsnum in $dllist
do
    if [ "${GXTRACK}" = "track" ]
    then
        ${GXCONTAINER} track_task.py queue --jobid="${jobid[0]}" --taskid="${n}" --task='download' --submission_time="$(date +%s)" \
                        --batch_file="${script}" --obs_id="${obsnum}" --stderr="${error}" --stdout="${output}"
    fi
    ((n+=1))
done

echo "Submitted ${script} as ${jobid} . Follow progress here:"
echo "${output}"
echo "${error}"

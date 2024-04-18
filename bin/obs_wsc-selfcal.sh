#! /bin/bash

usage()
{
echo "wsc-selfcal.sh [-d dep] [-p project] [-a account] [-z] [-t] obsnum
  -d dep     : job number for dependency (afterok)
  -p project : project, (must be specified, no default)
  -z         : Debugging mode: image the CORRECTED_DATA column
                instead of imaging the DATA column
  -t         : test. Don't submit job, just make the batch file
               and then return the submission command
  obsnum     : the obsid to process, or a text file of obsids (newline separated). 
               A job-array task will be submitted to process the collection of obsids. " 1>&2;
exit 1;
}

pipeuser="${GXUSER}"

#initial variables
dep=
tst=
debug=
# parse args and set options
while getopts ':tzd:a:p:' OPTION
do
    case "$OPTION" in
        d)
            dep=${OPTARG}
            ;;
    a)
        account=${OPTARG}
        ;;
    p)
        project=${OPTARG}
        ;;
    z)
        debug=1
        ;;
        t)
            tst=1
            ;;
        ? | : | h)
            usage
            ;;
  esac
done

# set the obsid to be the first non option
shift  "$(($OPTIND -1))"
obsnum=$1

queue="-p gpuq"
base="${GXSCRATCH}/$project"
code="${GXBASE}"

# if obsid is empty then just print help

if [[ -z ${obsnum} ]] || [[ -z $project ]] || [[ ! -d ${base} ]]
then
    usage
fi

if [[ ! -z ${dep} ]]
then
    if [[ -f ${obsnum} ]]
    then
        depend="--dependency=aftercorr:${dep}"
    else
        depend="--dependency=afterok:${dep}"
    fi
fi

if [[ ! -z ${GXACCOUNT} ]]
then
    account="--account=${GXACCOUNT}"
fi

# Establish job array options
numfiles=1
jobarray=''

# start the real program

script="${GXSCRIPT}/wsc_selfcal_${obsnum}.sh"
cat "${GXBASE}/templates/wsc_selfcal.tmpl" | sed -e "s:OBSNUM:${obsnum}:g" \
                                 -e "s:BASEDIR:${base}:g" \
                                 -e "s:PROJECT:${project}:g" \
                                 -e "s:DEBUG:${debug}:g" \
                                 -e "s:PIPEUSER:${pipeuser}:g" > "${script}"

output="${GXLOG}/wsc_selfcal_${obsnum}.o%A"
error="${GXLOG}/wsc_selfcal_${obsnum}.e%A"

if [[ -f ${obsnum} ]]
then
   output="${output}_%a"
   error="${error}_%a"
fi

chmod 755 "${script}"

# sbatch submissions need to start with a shebang
#Don't need to run sbatch because i'm specifying singularity to use for each line.

sub="sbatch --begin=now+5minutes --export=ALL --time=24:00:00 --mem=370G --account=mwasci --output=${output} --error=${error} --nodes=1 --cores=1 --gres=gpu:1 --cpus-per-gpu=38 --partition=gpuq --tmp=890GB"
sub="${sub} ${jobarray} ${depend} ${queue} ${script}"
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

echo "Submitted ${script} as ${jobid} . Follow progress here:"

for taskid in $(seq ${numfiles})
    do
    # rename the err/output files as we now know the jobid
    obserror=$(echo "${error}" | sed -e "s/%A/${jobid}/" -e "s/%a/${taskid}/")
    obsoutput=$(echo "${output}" | sed -e "s/%A/${jobid}/" -e "s/%a/${taskid}/")

    if [[ -f ${obsnum} ]]
    then
        obs=$(sed -n -e "${taskid}"p "${obsnum}")
    else
        obs=$obsnum
    fi

    if [ "${GXTRACK}" = "track" ]
    then
        # record submission
        ${GXCONTAINER} track_task.py queue --jobid="${jobid}" --taskid="${taskid}" --task='selfcal' --submission_time="$(date +%s)" \
                            --batch_file="${script}" --obs_id="${obs}" --stderr="${obserror}" --stdout="${obsoutput}"
    fi

    echo "$obsoutput"
    echo "$obserror"
done

#! /bin/bash

usage()
{
echo "backup.sh [-d dep] [-p project] [-a account] [-z] [-t] obsnum
  -d dep     : job number for dependency (afterok)
  -p project : project, (must be specified, no default)
  -t         : test. Don't submit job, just make the batch file
               and then return the submission command
  -c channel
  -r ra region" 1>&2;
exit 1;
}

pipeuser="${GXUSER}"

#initial variables
dep=
tst=
debug=
# parse args and set options
while getopts ':td:c:p:r:e:' OPTION
do
    case "$OPTION" in
        d)
            dep=${OPTARG}
            ;;
    c)
        channel=${OPTARG}
        ;;
    p)
        project=${OPTARG}
        ;;
    e)  
        declination=${OPTARG}
        ;;
    r)
        raregion=${OPTARG}
        ;;
        t)
            tst=1
            ;;
        ? | : | h)
            usage
            ;;
  esac
done

queue="-p workq"
base="${GXSCRATCH}/$project"
code="${GXBASE}"
remote="/mnt/gxarchive"

# If channel is empty then just print help
if [[ -z ${channel} ]] || [[ -z $project ]] || [[ ! -d ${base} ]] || [[ -z ${raregion} ]] || [[ -z ${declination} ]]
then
    usage
fi

if [[ ! -z ${dep} ]]
then
    if [[ -f ${channel} ]]
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

numfiles=1
jobarray=''

# Start the real program
script="${GXSCRIPT}/backup_${raregion}_${channel}.sh"
cat "${GXBASE}/templates/backup.tmpl" | sed -e "s:CHANNEL:${channel}:g" \
                                 -e "s:RAREGION:${raregion}:g" \
                                 -e "s:DECLINATION:${declination}:g" \
                                 -e "s:BASEDIR:${base}:g" \
                                 -e "s:REMOTE:${remote}:g" \
                                 -e "s:PIPEUSER:${pipeuser}:g" > "${script}"

output="${GXLOG}/backup_${raregion}_${channel}.o%A"
error="${GXLOG}/backup_${raregion}_${channel}.e%A"

chmod 755 "${script}"

# sbatch submissions need to start with a shebang
#Don't need to run sbatch because i'm specifying singularity to use for each line.

sub="sbatch --begin=now+1minutes --export=ALL --time=24:00:00 --mem-per-cpu=8G --account=mwasci --output=${output} --error=${error} --nodes=1 --cpus-per-task=4 --partition=workq --ntasks-per-node=1 --cpus-per-task=4 --job-name=backup_${raregion}_${channel} --open-mode=append --parsable -M garrawarla" 
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
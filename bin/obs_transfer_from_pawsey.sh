#! /bin/bash

usage()
{
echo "transfer_from_pawsey.sh [-d declination] [-g group] [-c channel] [-t]
  -d declination : include the negative or positive sign, no default
  -g group     : right ascension group
  -p project : where to download them
  -c channel : frequency channel
  -t         : test. Don't submit job, just make the batch file
               and return the submission command" 1>&2;
exit 1;
}

pipeuser="${GXUSER}"

while getopts ':td:g:c:p:' OPTION
do
    case "$OPTION" in
        d)
            declination=${OPTARG}
            ;;
        g)
            group=${OPTARG}
            ;;
        c)
            channel=${OPTARG}
            ;;
	p)
	    project=${OPTARG}
	    ;;
        t)
            tst=1
            ;;
        ? | : | h)
            usage
            ;;
  esac
done

# If one of the option is empty then just pring help
if [[ -z ${declination} ]] || [[ -z ${group} ]] || [[ -z ${channel} ]] || [[ -z ${project} ]]
then
    usage
fi

base="${GXSCRATCH}/$project"
code="${GXBASE}"

if [[ ! -z ${GXACCOUNT} ]]
then
    account="--account=${GXACCOUNT}"
fi

numfiles=1
jobarray=''

# Start the real program
script="${GXSCRATCH}/$project/transfer_from_pawsey_${group}_${channel}.sh"
cat "${GXBASE}/templates/transfer_from_pawsey.tmpl" | sed -e "s:CHANNEL:${channel}:g" \
                                 -e "s:GROUP:${group}:g" \
                                 -e "s:DECLINATION:${declination}:g" \
                                 -e "s:BASEDIR:${base}:g" \
                                 -e "s:PROJECT:${project}:g" \
                                 -e "s:PIPEUSER:${pipeuser}:g" > "${script}"

output="${GXSCRATCH}/$project/transfer_from_pawsey_${group}_${channel}.o%A"
error="${GXSCRATCH}/$project/transfer_from_pawsey_${group}_${channel}.e%A"

chmod 755 "${script}"

# sbatch submissions need to start with a shebang
#Don't need to run sbatch because i'm specifying singularity to use for each line.

sub="sbatch --begin=now+1minutes --export=ALL --time=15:00:00 --mem=250G --account=OD-207757 --output=${output} --error=${error} --nodes=1 --cpus-per-task=10 --ntasks-per-node=1 --job-name=transfer_from_pawsey_${group}_${channel}" 
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
echo "$output"
echo "$error"

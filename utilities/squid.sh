#! /bin/bash -l
#SBATCH --export=ALL,MWA_ASVO_API_KEY,SINGULARITY_BINDPATH
#SBATCH --mem=200GB
#SBATCH --time=05:00:00
#SBATCH --output=squid.o%A
#SBATCH --error=squid.e%A


# IF YOU NEED TO ACTUALLY SUBMIT THE JOBS UNCOMMENT! 
# export params="output=ms,flag_edge_width=80,avg_time_res=${tres},avg_freq_res=${fres}"
# singularity run $GXCONTAINER giant-squid submit-conv --parameters=$params ${obslist}
    
# get list of ready ones: 
#singularity run /software/projects/mwasci/kross/GLEAM-X-pipeline/gleamx_tools_clx.img giant-squid list --states ready total145.txt | cut -d "|" -f 3 | tail -n +4  | head -n -1 > ready_for_download.txt
#list=()
#list=$(cat "ready_for_download.txt")
#for obs in $list
#do
#    obsfile=$(echo "${obs}_"[0-9]*".tar")
#    if [[ -d $obs ]]
#    then             
#        if [[ -e $obsfile ]]
#        then 
#            echo "already have tar for $obs not downloading again!" 
#            sed -i "/$obs/d" "ready_for_download.txt"
#        elif [[ -d "$obs/$obs.ms" ]]
#        then 
#            echo "There's already a ms here! Not downloading for $obs" 
#            sed -i "/$obs/d" "ready_for_download.txt"
#        fi
#    else 
#        if [[ -e $obsfile ]]
#        then 
#            echo "already have tar for $obs not downloading again!" 
#            sed -i "/$obs/d" "ready_for_download.txt"
#        fi 
#    fi
#done 

#num_ready=$(cat "ready_for_download.txt" | wc -l)
#echo "There are ${num_ready} obsids ready for download. Downloading with giant-squid now!" 

#if [[ ${num_ready} == 0 ]]
#then 
#    echo "There are no jobs ready, don't run the giant-squid or it will just download anything that's ready" 
#else
    # TO AVOID IT GETTING CONFUSED IF THERE ARE MUTLIPLE JOBS ASSOCIATED WITH THE OBSID
    singularity run /software/projects/mwasci/kross/GLEAM-X-pipeline/gleamx_tools_clx.img giant-squid list --states ready ready_for_download.txt | cut -d "|" -f 2 | tail -n +4  | head -n -1 > ready_for_download_jobid.txt
    # Download just the tar file and untar inside directory below
    singularity run /software/projects/mwasci/kross/GLEAM-X-pipeline/gleamx_tools_clx.img giant-squid download -k ready_for_download_jobid.txt 
#fi  

list=()
list=$(cat "ready_for_download.txt")
for obs in $list
do
        if [[ ! -d "${obs}" ]]
        then
            mkdir "${obs}"
        fi

        cd "${obs}" || exit 1

        if [[ -d "${obs}.ms" ]]
        then
            echo "${obs}.ms already exists; please remove directory before running untar job."
        else
            mv ../*${obs}*.tar ./
            for file in *.tar
	    do
                tar xf "$file"
            done
	fi
        cd ..
done

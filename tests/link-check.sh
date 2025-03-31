#!/bin/bash

LOCAL_HOST="http://localhost:8000/intro.html"
MAX_WAIT_TIME=60 # 30 sec
OPTIONS="--exclude 'reddit.com' \
         --exclude 'anaconda.org' \
         --exclude 'arxiv.org' \
         --exclude 'docker.com' \
         --exclude 'stackoverflow.com' \
         --exclude 'linuxize.com' \
         --exclude 'cyberciti.biz' \
         --exclude 'gitlab.yourgitlab.com' \
         --exclude 'pushshift.io' \
         --exclude 'howtogeek.com' \
         --exclude 'linux.die.net' \
         --exclude 'https://taurus.hrsk.tu-dresden.de/' \
         --exclude 'https://github.com/' \
         --exclude 'https://frontend-data.netlify.com/' \
         --exclude 'https://byobu.org/' \
         --exclude 'http://ad.vgiscience.org/yfcc_gridagg/*' \
         --exclude 'https://gruenerring-leipzig.de/' \
         --exclude 'bfn.de' \
         --exclude 'alexanderdunkel.com' \
         --exclude 'hpcprojekte.zih.tu-dresden.de' \
         --exclude 'https://wwwpub.zih.tu-dresden.de' \
         --exclude 'https://doi.org' \
         --exclude 'https://www.preprints.org' \
         --color=always \
         --ignore-fragments \
         --buffer-size=16384 \
         --max-connections=10 \
         --header='User-Agent:curl/7.54.0' \
         --skip-tls-verification \
         --max-response-body-size 100000000 \
         --junit > rspec.xml"

         # --verbose \
         
# Wait for server to respond
for i in $(seq 1 60); do
    IS_SERVER_RUNNING=$(curl -LI ${LOCAL_HOST} -o /dev/null -w '%{http_code}' -s)
    if [[ "${IS_SERVER_RUNNING}" == "200" ]]; then
        echo "Server is running at ${LOCAL_HOST}. Running Muffet now..."
        eval muffet "${OPTIONS}" ${LOCAL_HOST} && \
        echo "Muffet ran successfully" && exit 0 || \
        echo "Muffet failed"
    fi
    sleep 1
done

# Wait for the server to respond
# for i in $(seq 1 60); do
#     IS_SERVER_RUNNING=$(curl -LI ${LOCAL_HOST} -o /dev/null -w '%{http_code}' -s)
#     if [[ "${IS_SERVER_RUNNING}" == "200" ]]; then
#         # Server is running, now run Muffet once
#         echo "Server is running at ${LOCAL_HOST}. Running Muffet now..."
#         
#         # Run Muffet and capture output
#         eval muffet "${OPTIONS}" ${LOCAL_HOST} > muffet_output.log 2>&1
#         
#         # Check Muffet output
#         cat muffet_output.log
#         
#         # Check if rspec.xml was generated
#         if [[ -f rspec.xml ]]; then
#             echo "rspec.xml generated successfully"
#         else
#             echo "rspec.xml was not generated. Muffet might have failed."
#             exit 1
#         fi
#         
#         break  # Exit the loop after Muffet runs successfully
#     fi
#     sleep 1  # Wait 1 second before retrying
# done

echo "error: Server is not up after 60 seconds"
exit 1

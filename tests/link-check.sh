#!/bin/bash

LOCAL_HOST="http://localhost:8000/"
MAX_WAIT_TIME=60 # 30 sec
BUFFER_SIZE=16384 # default: 4096, increase required for github-gists
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
         --ignore-fragments \
         --buffer-size $BUFFER_SIZE \
         --max-response-body-size 100000000 \
         --junit > rspec.xml"

for i in $(seq 0 ${MAX_WAIT_TIME}); do # 5 min
    sleep 0.5
    IS_SERVER_RUNNING=$(curl -LI ${LOCAL_HOST} -o /dev/null -w '%{http_code}' -s)
    if [[ "${IS_SERVER_RUNNING}" == "200" ]]; then
        eval muffet "${OPTIONS}" ${LOCAL_HOST} && exit 0 || exit 1
    fi
done

echo "error: time out $((${MAX_WAIT_TIME}/2)) sec" && exit 1

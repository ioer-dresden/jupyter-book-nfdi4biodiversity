#!/bin/sh

LOCAL_HOST="http://localhost:8000/intro.html"
MAX_WAIT_TIME=60 # 1 min
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
         --exclude 'https://kommisdd.dresden.de' \
         --exclude 'http://localhost:8000/_static/videos/Video.webm' \
         --exclude 'http://localhost:8000/_static/videos/Video3.webm' \
         --exclude 'academic.oup.com' \
         --exclude 'wiley.com' \
         --exclude 'campus.fdz.ioer.info' \
         --color=always \
         --ignore-fragments \
         --buffer-size=16384 \
         --max-connections=10 \
         --header='User-Agent:curl/7.54.0' \
         --skip-tls-verification \
         --max-response-body-size 100000000 \
         --junit > rspec.xml"

for i in $(seq 1 ${MAX_WAIT_TIME}); do
    sleep 5
    IS_SERVER_RUNNING=$(curl -LI ${LOCAL_HOST} -o /dev/null -w '%{http_code}' -s)
    if [ "${IS_SERVER_RUNNING}" = "200" ]; then  # Change from [[ ... ]] to [ ... ]
        eval muffet ${OPTIONS} ${LOCAL_HOST}
        if [ $? -eq 0 ]; then
            exit 0
        else
            exit 1
        fi
    fi
done
exit 1 # If the server was not responsive within the wait time

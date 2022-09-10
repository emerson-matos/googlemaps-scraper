# to debug remove `-e SE_START_XVFB=false` and add `-p 7900:7900`

docker run -d -p 4444:4444 -e SE_START_XVFB=false --shm-size="2g" selenium/standalone-chrome:latest
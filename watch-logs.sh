#! /bin/bash

tail -n 50 -f logs/scraper.log & 
tail -n 50 -f logs/main.log &
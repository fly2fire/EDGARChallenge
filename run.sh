#!/bin/bash
#
# include the directory paths of the input, inactivity period, and output file
#
python ./src/Track_EDGAR.py ./input/log.csv ./input/inactivity_period.txt ./output/sessionization.txt

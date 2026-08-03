#!/bin/bash
S=/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad
nice -n 9 $S/kissat/build/kissat -q pure_sigma18.cnf pure_sigma18_clean.drat
echo "kissat exit $?" > drat18.status
nice -n 12 $S/drat-trim/drat-trim pure_sigma18.cnf pure_sigma18_clean.drat 2>&1 | grep -E "VERIFIED|ERROR" >> drat18.status

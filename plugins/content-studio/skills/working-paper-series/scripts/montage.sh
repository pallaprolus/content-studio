#!/usr/bin/env bash
# Contact sheet of every page's frame 0, three per row: SERIES/out/all.png
# usage: scripts/montage.sh SERIES      (run render.py SERIES pages first)
set -e; cd "$1/out"; n=$(ls page-*-frame0.png | wc -l)
for k in $(seq 1 $n); do ffmpeg -loglevel error -y -i page-$k-frame0.png -vf "scale=540:674" m$k.png; done
ffmpeg -loglevel error -y -f lavfi -i color=white:s=540x674 -frames:v 1 blank.png
rows=""; r=0
for s in $(seq 1 3 $n); do in=""; c=0; for k in $(seq $s $((s+2))); do [ $k -le $n ] && in="$in -i m$k.png" || in="$in -i blank.png"; done
  ffmpeg -loglevel error -y $in -filter_complex hstack=inputs=3 row$r.png; rows="$rows -i row$r.png"; r=$((r+1)); done
if [ $r -gt 1 ]; then ffmpeg -loglevel error -y $rows -filter_complex vstack=inputs=$r all.png; else cp row0.png all.png; fi
rm -f m*.png row*.png blank.png; echo "$1/out/all.png"

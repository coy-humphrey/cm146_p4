#!/bin/bash

opponents=("opponent_bots/easy_bot.py"
           "opponent_bots/spread_bot.py"
           "opponent_bots/aggressive_bot.py"
           "opponent_bots/defensive_bot.py"
           "opponent_bots/production_bot.py")

maps=(71 13 24 56 7)

my_python="python3.5"
my_bot="behavior_tree_bot/bt_bot.py"

len=$((${#opponents[@]}-1))

show_game=true

for i in `seq 0 $len`;
do
	map="maps/map"
	map=$map${maps[$i]}".txt"
	if [ "$show_game" = true ] ; then
		eval "java -jar tools/PlayGame.jar $map 1000 1000 log.txt \"$my_python $my_bot\" \"$my_python ${opponents[$i]}\" | java -jar tools/ShowGame.jar"
	else
		eval "java -jar tools/PlayGame.jar $map 1000 1000 log.txt \"$my_python $my_bot\" \"$my_python ${opponents[$i]}\" 2>&1 | grep 'Win\|crash\|time'"
	fi
done
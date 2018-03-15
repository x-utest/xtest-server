#!/bin/bash
exe_project_name="xt-server-api"
python_file_name="start.py"

#shell code
exe_file_folder="/www/$exe_project_name"
exe_file_tag="$exe_project_name/$python_file_name"
exe_file_path="$exe_file_folder/$python_file_name"
log_path="/var/log/$exe_project_name/$exe_project_name.log"

case "$1" in
	start)
		echo "start $exe_project_name"
		cd $exe_file_folder
		nohup python $exe_file_path  1>$log_path 2>$log_path.error &
		echo $exe_file_path
		echo $log_path
		echo $log_path.error
	;;
	restart)
		echo "kill $exe_project_name"
		ps  -ef|grep python |grep $exe_file_tag|awk '{print $2}'|xargs kill -9

		echo "start $exe_project_name"
		cd $exe_file_folder
		nohup python $exe_file_path 1>$log_path 2>$log_path.error &
		echo $exe_file_path
		echo $log_path
		echo $log_path.error
	;;
	stop)
		echo "kill $exe_project_name"
		ps  -ef|grep python |grep $exe_file_tag|awk '{print $2}'|xargs kill -9
	;;
esac
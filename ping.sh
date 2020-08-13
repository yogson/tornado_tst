while true; do
	curl -w "%{time_total}" 127.0.0.1:8888
	sleep 1
done
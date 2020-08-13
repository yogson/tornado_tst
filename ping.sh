while true; do
	curl -w "%{time_total}" 192.168.88.35:8888
	sleep 1
done
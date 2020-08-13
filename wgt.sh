for (( i = 0; i <10; i++ )); do
	wget -P FILES 192.168.88.35:8888/download/$((1 + RANDOM % 6)).txt &
done
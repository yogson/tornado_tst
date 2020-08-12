for (( i = 0; i <20; i++ )); do
	wget -P FILES 127.0.0.1:8888/download/$((1 + RANDOM % 6)).txt &
done
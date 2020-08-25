for (( i = 0; i <20; i++ )); do
	wget -P /home/yogson/Downloads 127.0.0.1:8888/download/$((1 + RANDOM % 7)).txt &
done
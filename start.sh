cd mongodb/
echo "Starting MongoDB at port 27017 and Mongo Express at port 8081"
docker-compose up -d
cd ../

cd app_api/
echo "Starting API"
docker-compose up -d
cd ../

cd mqtt/
echo "Starting MQTT Broker"
docker-compose up -d
cd ../

cd subscriber/
echo "Starting subscriber for mqtt broker"
docker-compose up -d
cd ../

read -p "How many simultaneous deliverers you want to simulate?: " number_deliverers

echo "Use 'docker logs -f sub' to monitor the receiving data from the subscriber!"

sleep 3

python publisher/location_pub.py -n $number_deliverers

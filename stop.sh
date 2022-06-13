cd mongodb/
echo "Turning off Mongo DB and Mongo Express"
docker-compose down
cd ../

cd app_api/
echo "Turning off API"
docker-compose down
cd ../

cd subscriber/
echo "Turning off Subscriber"
docker-compose down
cd ../

cd mqtt/
echo "Turning off MQTT Broker"
docker-compose down
cd ../

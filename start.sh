cd mongodb/
docker - compose up - d - -force - recreate
cd ../

cd app_api/
docker - compose up - d - -force - recreate
cd ../

cd subscriber/
docker - compose up - d - -force - recreate
cd ../

cd mqtt/
docker - compose up - d - -force - recreate
cd ../

sleep 5

python publisher/location_pub.py

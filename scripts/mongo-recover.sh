#simple script to recover mongo DB if it crashes

rm /var/lib/mongodb/mongod.lock
rm /tmp/mongodb-27017.sock

service mongodb start

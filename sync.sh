# nohup sudo -b -u apache /var/www/vatic-checker/sync.sh

while true; do
    sleep 2
    rsync -a --delete --exclude frames /var/www/vatic-checker/src/vatic_checker/public/ /var/www/vatic-checker-live/public
    cp /var/www/vatic-checker/src/server.py /var/www/vatic-checker-live/server.py
done

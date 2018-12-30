# nohup sudo -b -u apache /var/www/vatic-checker/sync.sh

while true; do
    sleep 2
    rsync -a --delete --exclude public/frames /var/www/vatic-checker/ /var/www/vatic-checker-live
done

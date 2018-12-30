# Database setup
First time setup
`mysql -u root -e 'create database vaticChecker;'`

Reset the database
`mysql -u root -e 'drop database vaticChecker; create database vaticChecker;'`


# load test videos
TODO: make this right
sudo -u apache checker load ./tests/frames/zero --filename aslized/ben_jarashow_1745 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 28624 --end 29000 --duration 376 --label yll
sudo -u apache checker load ./tests/frames/one --filename aslized/ben_jarashow_1759 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 141417 --end 142833 --duration 1416 --label jasll


cd /var/www/
sudo rm -Rf vatic-checker-live/
mysql -u root -e 'drop database vaticChecker; create database vaticChecker;'
checker setup --database
sudo checker init vatic-checker-live
sudo chown -R apache:apache vatic-checker-live
sudo cp -R vatic-checker/tests/frames vatic-checker-live/
sudo chown -R apache:apache vatic-checker-live
cd vatic-checker-live
checker newuser jkeane

# load training
sudo -u apache checker loadtraining ./frames/zero --name aslized/ben_jarashow_1745 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 28624 --end 29000 --duration 376 --label yll
sudo -u apache checker loadtraining ./frames/zero --name aslized/ben_jarashow_1745 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 28624 --end 29000 --duration 376 --label yll

#load videos
sudo -u apache checker load ./frames/zero --name aslized/ben_jarashow_1745 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 28624 --end 29000 --duration 376 --label yll
sudo -u apache checker load ./frames/one --name aslized/ben_jarashow_1759 --video_path "/share/data/asl-data/completed_annotations/aurora_complete/youtube_general/Journal of American Sign Languages and Literatures.mp4" --start 141417 --end 142833 --duration 1416 --label jasll

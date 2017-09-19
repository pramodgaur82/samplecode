#!/bin/bash
echo "Now in production, be careful using this!"
read -rsp $'Press any key to continue...\n' -n1 key
rm -rf  db_repository
rm -f app.db
python db_create.py
python db_default_users.py
sudo chgrp www-data app.db
sudo chmod g+rw app.db
sudo chmod o-rwx app.db

# python db_dummy_users.py
# python db_assign_tags.py

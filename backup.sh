#! /bin/bash

# Gets date of most recent backup.    
newestfile=$(cd /home/romesh/meguk_backup && find . -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")        
budate=`echo $newestfile| cut -c10-19`

# Gets current date

cdate=$(date --iso)

# If the current date is the same as the date of the most recent backup, don't run the backup, just give a notification that says it has already been done today.

if [ $cdate = $budate ]; then
    echo "Backup already run"

# If the dates are different, start the backup.
else
    echo "Starting backup"

    tar -cvpzf /home/romesh/meguk_backup/backup-$(date +%Y-%m-%d).tar.gz "/meguk2017.com" --exclude=.git && echo "Backup finished"

fi

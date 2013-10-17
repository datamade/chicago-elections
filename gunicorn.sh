#!/bin/bash
set -e
VENV=/home/datamade/.virtualenvs/elections
LOGFILE=/home/datamade/logs/elections/gunicorn.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=datamade
GROUP=datamade
cd /home/datamade/projects/elections
source $VENV/bin/activate
source /home/datamade/.zshenv
test -d $LOGDIR || mkdir -p $LOGDIR
exec $VENV/bin/gunicorn -w $NUM_WORKERS --daemon --bind 127.0.0.1:9999 --user=$USER --group=$GROUP --log-level=debug --log-file=$LOGFILE 2>>$LOGFILE app:app

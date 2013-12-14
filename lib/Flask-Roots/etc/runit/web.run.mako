#!/bin/bash

ROOT_PATH="${ROOT_PATH}"
INSTANCE_PATH="${INSTANCE_PATH}"
SELF="${'${BASH_SOURCE[0]}'}"

# Get the owner of the `run` command. We are using Python since `stat` did not
# present a consistent interface on Linux and OS X.
if [[ $(id -u) == "0" ]]; then
    
    OWNER=$(python -c "import os, pwd; print pwd.getpwuid(os.stat('$SELF').st_uid).pw_name")
    
    # runit.
    if [[ "$(which chpst)" ]]; then
        PRELUDE="chpst -u $OWNER"

    # daemontools.
    elif [[ "$(which setuidgid)" ]]; then
        PRELUDE="setuidgid $OWNER"
    
    fi

fi

. "${ROOT_PATH}/bin/activate"

cd "$ROOT_PATH"

exec 2>&1
exec $PRELUDE gunicorn \
    -k gevent \
    -b 0.0.0.0:${PORT} \
    -p "$(dirname "$SELF")/pid" \
    ${APP_ENTRYPOINT}

#/bin/sh

SCRIPT_DIR=$(dirname $(realpath $0))

. $SCRIPT_DIR/CloudData.sh

OUTPUT=$(wget --user="$CLOUD_USER" --password="$CLOUD_PASS" --output-document="$SCRIPT_DIR/KeepassFile.kdbx" "https://cloud.4fh.eu/public.php/webdav/firefox.kdbx" 2>&1 )
RESULT=$?
if [ $RESULT -ne 0 ]; then
        echo WGET ERROR $RESULT
        echo $OUTPUT
fi
#!/bin/bash

nohup /opt/bathbuddy/bathbuddy.py -d 0 -c /opt/bathbuddy/bathbuddy.cfg &
NAME="music"
echo "HTTP/1.0 200 OK"
echo "Content-type:text/html\r\n"
echo "<html><head>"
echo "<title>$NAME</title>"
echo '<meta name="description" content="'$NAME'">'
echo '<meta name="keywords" content="'$NAME'">'
echo '<meta http-equiv="Content-type"
content="text/html;charset=UTF-8">'
echo '<meta name="ROBOTS" content="noindex">'
echo "</head><body><pre>"
echo "running unlimited music"
echo "</pre></body></html>"
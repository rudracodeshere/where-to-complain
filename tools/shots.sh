#!/bin/sh
# usage: tools/shots.sh before|after   (screenshots of local docs/ via headless Chrome)
P=$1; D=$(cd "$(dirname "$0")/.." && pwd)
for page in home:index.html guide:star-health-complaint-escalation/index.html; do
  n=${page%%:*}; f=${page#*:}
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=390,2400 --screenshot="$D/design-shots/$P-$n-mobile.png" "file://$D/docs/$f" 2>/dev/null
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=1280,2000 --screenshot="$D/design-shots/$P-$n-desktop.png" "file://$D/docs/$f" 2>/dev/null
done
ls -la "$D/design-shots"

#!/bin/sh

grep "@needauth\|@rpc" -A1 g*/s*/r*/*.py | grep -v "\-\-" | cut -d '/' -f 4 > tmpdoc
cut -d - -f 2 tmpdoc | sed 'N;s/\n//' | sed 's/py:@//' > tmpdoc2
sed 's/needauth\s*def //' tmpdoc2 | sed 's/rpc\s*def //' | sed 's/__init__.//' > tmpdoc
sed 's/, user)/)/' tmpdoc | sed 's/(user)/()/' | sed 's/:\s*$//' 
rm tmpdoc tmpdoc2


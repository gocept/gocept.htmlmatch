===============================
Using the ``htmlmatch`` package
===============================

Simple matching
===============

Sometimes it matches:

>>> from gocept.htmlmatch.match import imatch
>>> imatch('<html><h1></h1><p></p></html>',
...        '<html><h1></h1><p></p></html>')

Sometimes it doesn't:

>>> imatch('<html><h1></h1><p></p></html>',
...        '<html><body><h1></h1><p></p></body></html>')
Matched:
<html>
Got:
<body>
Expected:
<h1>

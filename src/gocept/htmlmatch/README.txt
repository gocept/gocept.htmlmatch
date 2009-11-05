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


Alternative elements
====================

When specifying a pattern to match, we can allow single tags to have any name
out of a given set of alternatives. The simplest case is to allow one
alternative name for one tag:

>>> imatch('<html><h1 m:alt="h2"></h1><p></p></html>',
...        '<html><h1></h1><p></p></html>')

>>> imatch('<html><h1 m:alt="h2"></h1><p></p></html>',
...        '<html><h2></h2><p></p></html>')

>>> imatch('<html><h1 m:alt="h2"></h1><p></p></html>',
...        '<html><h3></h3><p></p></html>')
Matched:
<html>
Got:
<h3>
Expected:
<h1> or <h2>

If there are more than one alternative names for a tag, they may be listed
separated by whitespace:

>>> imatch('<html><h1 m:alt="h2 h3"></h1><p m:alt="div"></p></html>',
...        '<html><h3></h3><div></div></html>')

>>> imatch('<html><h1 m:alt="h2 h3"></h1><p m:alt="div"></p></html>',
...        '<html><h4></h4><div></div></html>')
Matched:
<html>
Got:
<h4>
Expected:
<h1> or <h2> or <h3>

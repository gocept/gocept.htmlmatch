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


Ellipsis
========

Pieces of XML we are not interested in may be ignored by using an ellipsis in
the pattern:

>>> imatch('<html><body><m:ellipsis></m:ellipsis><p></p></body></html>',
...        '<html><body><h1></h1><div><p></p></div><p></p></body></html>')

The paragraph element just matched is that after the elided material; the one
inside the div element does not match:

>>> imatch('<html><body><m:ellipsis></m:ellipsis><p></p></body></html>',
...        '<html><body><h1></h1><div><p></p></div></body></html>')
Matched:


Input will also match if there is no element at all at the place of the
ellipsis:

>>> imatch('<html><body><m:ellipsis></m:ellipsis><p></p></body></html>',
...        '<html><body><p></p></body></html>')

Ellipses are capable of doing weird stuff:

>>> imatch('<body><m:ellipsis></m:ellipsis><p><span></span></p></body>',
...        '<body><p></p><p><span></span></p></body>')

We can also use an ellipsis to specify XML content that is nested within zero
or more elements we don't care about, along with any number of sibling
elements:

>>> imatch('<html><body><m:ellipsis><p></p></m:ellipsis></body></html>',
...        '<html><body><h1></h1><p></p></body></html>')

>>> imatch('<html><body><m:ellipsis><p></p></m:ellipsis></body></html>',
...        '<html><body><div><div><h1></h1><p></p></div></div></body></html>')

It is of course a mistake for the content nested within the ellipsis not to
exist in a suitable place in the input at all. The mismatch will be reported
to occur at the point just after the closing ellipsis tag:

>>> imatch('<html><body><m:ellipsis><p></p></m:ellipsis></body></html>',
...        '<html><body><div><div><h1></h1></div></div></body></html>')
Matched:
<html><body><div><div><h1></h1></div></div>

Ellipses may also be nested:

>>> imatch("""\
... <html>
...   <m:ellipsis>
...     <div>
...       <m:ellipsis>
...         <p></p>
...       </m:ellipsis>
...     </div>
...   </m:ellipsis>
... </html>
... """, """\
... <html>
...   <body>
...     <div>
...       <div>
...         <h1></h1>
...         <div>
...           <h2></h2>
...           <p></p>
...         </div>
...       </div>
...       <table></table>
...     </div>
...   </body>
... </html>
... """)

(Write something clever about the reporting here)

>>> imatch("""\
... <html>
...   <m:ellipsis>
...     <div>
...       <m:ellipsis>
...         <p></p>
...       </m:ellipsis>
...     </div>
...   </m:ellipsis>
... </html>
... """, """\
... <html>
...   <body>
...     <div>
...       <div>
...         <h1></h1>
...         <div>
...           <h2></h2>
...         </div>
...       </div>
...       <table></table>
...     </div>
...     <p></p>
...   </body>
... </html>
... """)
Matched:
<html>
  <body>
    <div>
      <div>
        <h1></h1>
        <div>
          <h2></h2>
        </div>
      </div>
      <table></table>

Ellipses may be used at the beginning and end of the expression:

>>> imatch('<m:ellipsis><p></p></m:ellipsis>', '<p></p>')
>>> imatch('<m:ellipsis><p></p></m:ellipsis>', '<html><p></p></html>')
>>> imatch('<m:ellipsis><p></p></m:ellipsis>', '<html><b></b></html>')
>>> imatch('<m:ellipsis><p><a></a></p></m:ellipsis>',
...        '<html><p></p><p><b></b></p><p><a><b></b></a></p></html>')

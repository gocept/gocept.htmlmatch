# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import xml.etree.ElementTree


class HTMLMatch(object):
    """A match instance describes how well an xml input text conforms
    to a pattern.

    """

    matches = None
    got = None
    expected = None

    def __init__(self, expression, input):
        self.expression = expression
        self.input = input
        self.matched_input = []
        self.expression_root = xml.etree.ElementTree.fromstring(expression)
        self.input_root = xml.etree.ElementTree.fromstring(input)

    def __call__(self):
        pass

    def report(self):
        """Generate a human readable report in the case the input text
        did not match the pattern.

        """
        r = StringIO.StringIO()
        r.write('Matched:'+'\n')
        r.write(''.join(map(str, self.matched_input))+'\n')
        r.write('Got:'+'\n')
        r.write(str(self.got)+'\n')
        r.write('Expected:'+'\n')
        r.write(str(self.expected)+'\n')
        return r.getvalue()


def match(expression, input):
    """Convenience function that configures the state machine and runs
    it on the input.

    Returns an HTMLMatch instance.

    """
    m = HTMLMatch(expression, input)
    m()
    return m


def imatch(expression, input):
    """Convenience wrapper for ``match`` that handles input and output in a
    way friendly to interactive environments or doc-tests.
    """
    m = match(expression, input)
    if not m.matches:
        print m.report(),

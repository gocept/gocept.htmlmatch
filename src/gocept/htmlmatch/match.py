# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import xml.etree.ElementTree


class Mismatch(Exception):
    """A mismatch between subtrees of expression and input was found."""

    def __init__(self, expected, got):
        self.expected = expected
        self.got = got


def start_tag(node):
    return '<%s>' % node.tag


def end_tag(node):
    return '</%s>' % node.tag


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
        self.matched_input = StringIO.StringIO()
        self.expression_root = xml.etree.ElementTree.fromstring(expression)
        self.input_root = xml.etree.ElementTree.fromstring(input)

    def match(self, expression_node, input_node):
        if expression_node.tag != input_node.tag:
            raise Mismatch(start_tag(expression_node),
                           start_tag(input_node))
        self.matched_input.write(start_tag(input_node))
        input_children = input_node.getchildren()
        for expression_child in expression_node.getchildren():
            try:
                input_child = input_children.pop(0)
            except IndexError:
                # encountered closing tag too early
                raise Mismatch(start_tag(expression_child),
                               end_tag(input_node))
            self.match(expression_child, input_child)
        if input_children:
            raise Mismatch(end_tag(expression_node),
                           start_tag(input_children[0]))
        self.matched_input.write(end_tag(input_node))

    def __call__(self):
        try:
            self.match(self.expression_root, self.input_root)
        except Mismatch, m:
            self.expected = m.expected
            self.got = m.got
            self.matches = False
        else:
            self.matches = True

    def report(self):
        """Generate a human readable report in the case the input text
        did not match the pattern.

        """
        r = StringIO.StringIO()
        r.write('Matched:'+'\n')
        r.write(self.matched_input.getvalue()+'\n')
        r.write('Got:'+'\n')
        r.write(self.got+'\n')
        r.write('Expected:'+'\n')
        r.write(self.expected+'\n')
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

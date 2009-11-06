# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO

try:
    from lxml import etree as ElementTree
    from lxml.etree import _Element as element_class
except ImportError:
    from xml.etree import ElementTree
    from xml.etree.ElementTree import _ElementInterface as element_class


NAMESPACE = 'http://xml.gocept.com/namespaces/htmlmatch'
NS = '{%s}' % NAMESPACE


class Mismatch(Exception):
    """A mismatch between subtrees of expression and input was found."""

    def __init__(self, expected, got):
        self.expected = expected
        self.got = got


def start_tag(node):
    if isinstance(node, element_class):
        return '<%s>' % node.tag
    tags = node
    return ' or '.join(sorted('<%s>' % tag for tag in tags))


def end_tag(node):
    return '</%s>' % node.tag


class HTMLMatch(object):
    """A match instance describes how well an xml element tree conforms to a
    match pattern also given as an element tree.

    """

    matches = None
    got = None
    expected = None

    def __init__(self, expression, input):
        self.expression = expression
        self.input = input
        self.matched_input = StringIO.StringIO()

    def match(self, expression_node, input_node):
        expected_tags = ([expression_node.tag]
                         + expression_node.get(NS+'alt', '').split())
        if input_node.tag not in expected_tags:
            raise Mismatch(start_tag(expected_tags),
                           start_tag(input_node))
        self.matched_input.write(start_tag(input_node))

        expression_children = expression_node.getchildren()
        input_children = input_node.getchildren()
        while expression_children and input_children:
            self.match(expression_children.pop(0), input_children.pop(0))
        if expression_children:
            # encountered closing tag too early
            raise Mismatch(start_tag(expression_children[0]),
                           end_tag(input_node))
        if input_children:
            # encountered extra stuff before the closing tag
            raise Mismatch(end_tag(expression_node),
                           start_tag(input_children[0]))

        self.matched_input.write(end_tag(input_node))

    def __call__(self):
        try:
            self.match(self.expression, self.input)
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
    expression_root = ElementTree.fromstring(
        '<root xmlns:m="%s">%s</root>' % (NAMESPACE, expression)
        ).getchildren()[0]
    input_root = ElementTree.fromstring(input)
    m = HTMLMatch(expression_root, input_root)
    m()
    return m


def imatch(expression, input):
    """Convenience wrapper for ``match`` that handles input and output in a
    way friendly to interactive environments or doc-tests.
    """
    m = match(expression, input)
    if not m.matches:
        print m.report(),

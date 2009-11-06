# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

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


def start_tag(node):
    if isinstance(node, element_class):
        return '<%s>' % node.tag
    tags = node
    return ' or '.join(sorted('<%s>' % tag for tag in tags))


def end_tag(node):
    return '</%s>' % node.tag


class MatchInfo(object):
    """Information about an event encountered while matching."""

    element = None
    event = '' # start, end
    weight = 0

    def __init__(self, element, event, weight):
        self.element = element
        self.event = event
        self.weight = weight


class MatchPath(object):
    """Accumulated MatchInfos up to a mismatch."""

    def __init__(self, infos, expected, got):
        self.infos = infos
        self.expected = expected
        self.got = got

    def report(self):
        return ''

    def weight(self):
        return sum(info.weight for info in self.infos)

    def depth(self):
        return (sum(1 for info in self.infos if info.event == 'start')
                - sum(1 for info in self.infos if info.event == 'end'))


class HTMLMatch(object):
    """A match instance describes how well an xml element tree conforms to a
    match pattern also given as an element tree.

    """

    matches = None

    def __init__(self, expression, input):
        self.expression = expression
        self.input = input
        self.matched_input = []
        self.expected = []
        self.match_paths = []

    def mismatch(self, got):
        self.match_paths.append(MatchPath(
                sum(self.matched_input, []), self.expected[-1], got))

    def element_match(self, expression_node, input_node):
        """Match an expression node to an input node.

        The expression must not be an ellipsis.

        Returns nothing.

        """
        expected_tags = ([expression_node.tag]
                         + expression_node.get(NS+'alt', '').split())
        if input_node.tag not in expected_tags:
            self.mismatch(start_tag(input_node))
            raise Mismatch
        self.matched_input[-1].append(MatchInfo(input_node, 'start', 1))

        self.sequence_match(expression_node.getchildren(),
                            input_node.getchildren())

        self.matched_input[-1].append(MatchInfo(input_node, 'end', 1))

    def subsequence_match(self, expression_nodes, input_nodes):
        """Match a sequence of expression nodes to a subsequence of input
        nodes.

        Expression nodes may contain ellipses.

        Returns the remaining input nodes.

        """
        input_nodes = input_nodes[:]
        while True:
            try:
                return self.start_match(expression_nodes, input_nodes)
            except Mismatch:
                if not input_nodes:
                    raise
            del input_nodes[0]

    def ellipsis_match(self, expression_nodes, input_nodes):
        """Match a sequence of expression nodes to a subsequence of input
        nodes or their children recursively.

        Returns the remaining input nodes. If the match occurred on the
        children of an input node, all input nodes following that one will be
        returned.

        """
        input_nodes = input_nodes[:]
        try:
            return self.subsequence_match(expression_nodes, input_nodes)
        except Mismatch, mismatch:
            while input_nodes:
                try:
                    self.ellipsis_match(expression_nodes,
                                        input_nodes.pop(0).getchildren())
                except Mismatch:
                    pass
                else:
                    return input_nodes
            else:
                raise mismatch

    def start_match(self, expression_nodes, input_nodes):
        """Match a sequence of expression nodes to the start of a sequence of
        input nodes.

        Expression nodes may contain ellipses.

        Returns the remaining input nodes.

        """
        expression_nodes = expression_nodes[:]
        input_nodes = input_nodes[:]
        while expression_nodes and input_nodes:
            # match node by node until we encounter an ellipsis
            expression_node = expression_nodes.pop(0)

            if expression_node.tag == NS + 'ellipsis':
                break

            self.element_match(expression_node, input_nodes.pop(0))
        else:
            # we didn't encounter any ellipses, all expression nodes must have
            # matched
            if expression_nodes:
                # encountered closing tag too early
                raise Mismatch(start_tag(expression_nodes[0]), '')

            return input_nodes

        if expression_node.getchildren():
            # match the expression inside the ellipsis, eat any input up to a
            # match
            input_nodes = self.ellipsis_match(
                expression_node.getchildren(), input_nodes)

        if not expression_nodes:
            # eat all input after the ellipsis
            return []

        # match all remaining expression nodes up to the end of the input, eat
        # any input after the ellipsis up to a match
        while True:
            try:
                self.sequence_match(expression_nodes, input_nodes)
            except Mismatch:
                if not input_nodes:
                    raise
            else:
                return []
            del input_nodes[0]

    def sequence_match(self, expression_nodes, input_nodes):
        """Match a sequence of expression nodes to a complete sequence of
        input nodes.

        Expression nodes may contain ellipses.

        Returns nothing.

        """
        input_nodes = self.start_match(expression_nodes, input_nodes)
        if input_nodes:
            # encountered extra stuff before the closing tag
            raise Mismatch('',
                           start_tag(input_nodes[0]))

    def __call__(self):
        self.matched_input.append([])
        try:
            self.sequence_match([self.expression], [self.input])
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

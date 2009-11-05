# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest


def test_suite():
    return doctest.DocFileSuite('README.txt', package='gocept.htmlmatch')

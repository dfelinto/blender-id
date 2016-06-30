# -*- encoding: utf-8 -*-

import datetime
import json
import logging

from common_test_class import AbstractBlenderIdTest

log = logging.getLogger(__name__)


class UserNameTest(AbstractBlenderIdTest):
    def test_split_name(self):
        from application.modules.oauth import split_name

        self.assertEqual((u'Fürst', u'Name'),
                         split_name(u'Fürst Name'))

        self.assertEqual((u'First', u'Double Lastname'),
                         split_name(u'First Double Lastname'))

        self.assertEqual((u'Double First', u'Double Lastname'),
                         split_name(u'Double First Double Lastname'))

        self.assertEqual((u'', u'Last'),
                         split_name(u'Last'))

        self.assertEqual((u'', u''),
                         split_name(u''))

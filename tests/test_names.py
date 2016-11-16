# -*- encoding: utf-8 -*-

import datetime
import json
import logging

from common_test_class import AbstractBlenderIdTest

log = logging.getLogger(__name__)


class UserNameTest(AbstractBlenderIdTest):
    def test_split_name(self):
        from application.modules.oauth import split_name

        self.assertEqual(('Fürst', 'Name'),
                         split_name('Fürst Name'))

        self.assertEqual(('First', 'Double Lastname'),
                         split_name('First Double Lastname'))

        self.assertEqual(('Double First', 'Double Lastname'),
                         split_name('Double First Double Lastname'))

        self.assertEqual(('', 'Last'),
                         split_name('Last'))

        self.assertEqual(('', ''),
                         split_name(''))

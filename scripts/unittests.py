__author__ = 'ross'

import unittest
import lxc_base
import os


class TestClass(unittest.TestCase):

    def testRootAccess(self):
        '''
        Test Case for root access, should work with non-root and root users
        '''
        is_root = os.geteuid() == 0
        assert is_root == lxc_base.root_access(), "root_access function not assessing correct access"

    def testStartNoExistingContainer(self):
        '''
        Test case for start command, container is assumed not to exist
        '''
        container = "xcvbn"
        start_cmd = ["echo", "container started"]
        assert not lxc_base.start(start_cmd, container), "container name may already exist, " \
                                                         "or function is not checking for existing container"

    def testStartExistingContainer(self):
        '''
        Test case for start command, container is assumed to exist
        '''
        container = "test"
        start_cmd = ["echo", "container started"]
        assert lxc_base.start(start_cmd, container), "container may not exist, or start function is incorrect"


if __name__ == "__main__":
    unittest.main()
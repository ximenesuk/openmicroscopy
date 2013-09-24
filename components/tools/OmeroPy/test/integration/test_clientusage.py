#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
   Tests for the demonstrating client usage

   Copyright 2010 Glencoe Software, Inc. All rights reserved.
   Use is subject to license terms supplied in LICENSE.txt

"""

import omero
import unittest
import test.integration.library as lib

from omero.rtypes import rstring, rlong
from omero.util.concurrency import get_event

class TestClientUsage(lib.ITest):
    """
    Note: this is the only test which should use 'omero.client()'
    All others should use the new_client(user=) syntax from lib.ITest
    """

    #def testClientClosedAutomatically(self): # -> ClientUsageTest

    # Move to ClientUsageTest (it clearly originally came from there!)
    def testClientClosedManually(self):
        client = omero.client()
        client.createSession();
        client.getSession().closeOnDestroy();
        client.closeSession();

    #def testUseSharedMemory(self): # -> ClientUsageTest

    #def testCreateInsecureClientTicket2099(self): # -> ClientUsageTest

    #def testGetStatefulServices(self): # -> ClientUsageTest

if __name__ == '__main__':
    unittest.main()


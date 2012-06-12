#!/usr/bin/env python

"""
   Integration test for adding annotations to Project.
"""
import unittest
import integration.library as lib
import omero
from omero.rtypes import *

class HandleTest(lib.ITest):

    def setUp(self):
        lib.ITest.setUp(self)
        # create group and users
        users = ["one","two","three"]
        group = self.new_group(perms='rw----')
        exps = {}
        exps["one"] = self.new_user(group=group)
        exps["two"] = self.new_user(group=group)
        exps["three"] = self.new_user(group=group)

        # clients and services
        clients = {}
        self.updateServices = {}
        self.deleteServices = {}
        for user in users:
            clients[user] = self.new_client(user=exps[user], group=group)
            self.updateServices[user] = clients[user].sf.getUpdateService()
            self.deleteServices[user] = clients[user].sf.getDeleteService()

    def testHandleFirstUser(self):
        user = "one"
        # Create something to hang a delete off
        img = omero.model.ImageI()
        img.name = omero.rtypes.rstring("")
        img.acquisitionDate = omero.rtypes.rtime(0)
        img = self.updateServices[user].saveAndReturnObject( img )

        # Now set up the delete
        command = omero.api.delete.DeleteCommand("/Image", img.id.val, None)
        handle = self.deleteServices[user].queueDelete([command])
        # Does the handle object exist?
        handle.finished()

    def testHandleSecondUser(self):
        user = "two"
        # Create something to hang a delete off
        img = omero.model.ImageI()
        img.name = omero.rtypes.rstring("")
        img.acquisitionDate = omero.rtypes.rtime(0)
        img = self.updateServices[user].saveAndReturnObject( img )

        # Now set up the delete
        command = omero.api.delete.DeleteCommand("/Image", img.id.val, None)
        handle = self.deleteServices[user].queueDelete([command])
        # Does the handle object exist?
        handle.finished()

    def testHandleLastUser(self):
        user = "three"
        # Create something to hang a delete off
        img = omero.model.ImageI()
        img.name = omero.rtypes.rstring("")
        img.acquisitionDate = omero.rtypes.rtime(0)
        img = self.updateServices[user].saveAndReturnObject( img )

        # Now set up the delete
        command = omero.api.delete.DeleteCommand("/Image", img.id.val, None)
        handle = self.deleteServices[user].queueDelete([command])
        # Does the handle object exist?
        handle.finished()

if __name__ == '__main__':
    unittest.main()

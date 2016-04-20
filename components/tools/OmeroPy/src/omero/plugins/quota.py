#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2016 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
quota plugin for managing quotas.
"""

import sys

from omero.cli import admin_only
from omero.cli import CmdControl
from omero.cli import CLI
from omero.cmd import DiskUsage
from omero.gateway import BlitzGateway
from omero.model import NamedValue as NV
from omero.rtypes import rstring

from omero_model_MapAnnotationI import MapAnnotationI
from omero_model_ExperimenterAnnotationLinkI import ExperimenterAnnotationLinkI

HELP = """Quota management utilities"""

# TODO: move to constants
NSQUOTAMAP = "NSQUOTAMAP"


class QuotaControl(CmdControl):

    def _configure(self, parser):

        parser.add_login_arguments()
        sub = parser.sub()

        status = parser.add(sub, self.status)
        status.add_login_arguments()
        status.add_style_argument()
        status.add_argument(
            "obj", nargs="?",
            help=("Users to be queried in the form "
                  "'Experimenter:<Id>[,<Id> ...]', or 'Experimenter:*' "
                  "to query all users."))
        status.add_argument(
            "--wait", type=long,
            help="Number of seconds to wait for the processing to complete "
            "(Indefinite < 0; No wait=0).", default=-1)
        update = parser.add(sub, self.update)
        update.add_argument(
            "obj",
            help=("Users to be queried in the form "
                  "'Experimenter:<Id>[,<Id> ...]', or 'Experimenter:*' "
                  "to query all users."))
        update_group = update.add_mutually_exclusive_group(required=True)
        update_group.add_argument(
            "--set", type=long,
            help="Create new or update existing quota (MiB).")
        update_group.add_argument(
            "--clear", action="store_true",
            help="Remove any existing quota.")

    def status(self, args):
        """Shows quota status for users."""

        client = self.ctx.conn(args)
        req = DiskUsage()
        if args.obj:
            try:
                klass, ids = self._quota_obj(args.obj)
            except ValueError, ve:
                self.ctx.err(ve)
                return
        else:
            admin = client.sf.getAdminService()
            uid = admin.getEventContext().userId
            klass = "Experimenter"
            ids = [uid]

        if ids:
            req.objects = {klass: ids}
        else:
            req.classes = [klass]
        cb = None
        try:
            rsp, status, cb = self.response(client, req, wait=args.wait)
            err = self.get_error(rsp)
            if err:
                self.ctx.err("Error: " + rsp.parameters['message'])
            else:
                self._quota_report(rsp, args)
        finally:
            if cb is not None:
                cb.close(True)  # Close handle

    @admin_only
    def update(self, args):
        """Sets, updates and clears the quota for users (admin-only)."""

        try:
            klass, ids = self._quota_obj(args.obj)
        except ValueError, ve:
            self.ctx.err(ve)
            return
        client = self.ctx.conn(args)
        gateway = BlitzGateway(client_obj=client)
        gateway.SERVICE_OPTS.setOmeroGroup("-1")
        update = client.sf.getUpdateService()
        if ids:
            for id in ids:
                user = gateway.getObject("Experimenter", id)
                ma = self._get_quota_map(user)
                if args.set:
                    if args.set < 0:
                        self.ctx.die(
                            600, "Error: quota cannot be a negative value")
                    quota = args.set*1024*1024
                    if ma:
                        self._update_quota_map(ma, quota, update)
                    else:
                        self._create_quota_map(user, quota, update)
                else:
                    if ma:
                        self._delete_quota_map(user)

    def _get_quota_map(self, user):
        """ Get the quota map annotation for a single user. """
        anns = list(user.listAnnotations(ns=NSQUOTAMAP))
        if anns:
            return anns[0]

    def _create_quota_map(self, user, quota, update):
        """ Create a quota map annotation for a single user. """
        ma = MapAnnotationI()
        ma.setNs(rstring("NSQUOTAMAP"))
        ma.setMapValue([NV('Quota', str(quota))])
        ma = update.saveAndReturnObject(ma)

        eal = ExperimenterAnnotationLinkI()
        eal.parent = user._obj
        eal.child = ma
        eal = update.saveAndReturnObject(eal)

    def _update_quota_map(self, ma, quota, update):
        """ Update the value of the quota map annotation for a single user. """
        ma = ma._obj
        ma.setMapValue([NV('Quota', str(quota))])
        ma = update.saveAndReturnObject(ma)

    def _delete_quota_map(self, user):
        """ Delete the quota map annotation for a single user. """
        user.removeAnnotations(NSQUOTAMAP)

    def _quota_obj(self, obj):
        """
        Take the positional argument, check it is valid
        then extract the class and ids
        """
        try:
            parts = obj.split(":", 1)
            assert len(parts) == 2
            klass = parts[0]
            if klass not in ("User", "Experimenter"):
                raise ValueError("Quota not applicable to: %s" % klass)
            if klass == "User":
                klass = "Experimenter"
            if '*' in parts[1]:
                ids = None
            else:
                ids = parts[1].split(",")
                ids = map(long, ids)
        except:
            raise ValueError("Bad object specification: %s" % obj)
        return (klass, ids)

    def _quota_report(self, rsp, args):
        """
        Generate a report containing the bytes used and quota per user.
        """
        subtotals = {}

        for userGroup in rsp.totalBytesUsed.keys():
            size = rsp.totalBytesUsed[userGroup]
            key = userGroup.first
            if key in subtotals.keys():
                subtotals[key] += size
            else:
                subtotals[key] = size

        client = self.ctx.conn(args)
        gateway = BlitzGateway(client_obj=client)
        gateway.SERVICE_OPTS.setOmeroGroup("-1")
        for key in subtotals.keys():
            user = gateway.getObject("Experimenter", key)
            ma = self._get_quota_map(user)
            if ma and ma._obj.getMapValue()[0].name == "Quota":
                q = long(ma._obj.getMapValue()[0].value)
                if q != 0:
                    percent = int(100.0*subtotals[key]/q)
                else:
                    percent = "NA"
                subtotals[key] = (subtotals[key], q, "%s%%" % percent)
            else:
                subtotals[key] = (subtotals[key], None, "NA")
        if len(subtotals.keys()) > 1:
            self._multiple_quota_report(subtotals, args)
        else:
            self._single_quota_report(subtotals.values()[0])

    def _single_quota_report(self, values):
        """
        Output the total bytes used and the quota.
        """
        self.ctx.out("%s of %s (%s%%)" % values)

    def _multiple_quota_report(self, subtotals, args):
        """
        Print a breakdown of quota usage in table form, including
        user id, bytes used, quota and perentage used.
        """
        from omero.util.text import TableBuilder

        showCols = ["user", "used (bytes)", "quota (bytes)", "used"]

        align = 'lrrr'
        tb = TableBuilder(*showCols)
        tb.set_align(align)
        if args.style:
            tb.set_style(args.style)

        for key in subtotals.keys():
            row = [key]
            row.extend(list(subtotals[key]))
            tb.row(*tuple(row))

        self.ctx.out(str(tb.build()))

try:
    register("quota", QuotaControl, HELP)
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("quota", QuotaControl, HELP)
        cli.invoke(sys.argv[1:])

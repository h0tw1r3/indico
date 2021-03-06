# -*- coding: utf-8 -*-
##
##
## This file is part of CDS Indico.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 CERN.
##
## CDS Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Indico; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


from MaKaC.common.utils import *

from indico.core.extpoint import Component
from indico.core.extpoint.events import INavigationContributor
from MaKaC.plugins.util import PluginsWrapper
from indico.core.extpoint.index import ICatalogIndexProvider
from zope.interface import implements
from MaKaC.plugins.Collaboration.Vidyo.indexes import BookingsByVidyoRoomIndex, BOOKINGS_BY_VIDYO_ROOMS_INDEX
from MaKaC.plugins.Collaboration.Vidyo.common import VidyoTools

class VidyoContributor(Component):

    implements(INavigationContributor)

    @classmethod
    def addCheckBox2CloneConf(cls, obj, list):
        """ we show the clone checkbox if:
            * The Vidyo Plugin is active.
            * There are vidyo services in the event created by the user who wants to clone
        """
        #list of creators of the chat rooms
        if PluginsWrapper('Collaboration', 'Vidyo').isActive() and len(obj._conf.getCSBookingManager().getBookingList(filterByType="Vidyo")) !=0:
            list['cloneOptions'] += _("""<li><input type="checkbox" name="cloneVidyo" id="cloneVidyo" value="1" checked="checked"/>Vidyo</li>""")

    @classmethod
    def fillCloneDict(self, obj, params):
        options = params['options']
        paramNames = params['paramNames']
        options['vidyo'] = 'cloneVidyo' in paramNames

    @classmethod
    def cloneEvent(cls, confToClone, params):
        """ we'll clone only the vidyo services created by the user who is cloning the conference"""
        conf = params['conf']
        options = params['options']

        if options.get("vidyo", True):
            for vs in confToClone.getCSBookingManager().getBookingList(filterByType="Vidyo"):
                # Do not cloning the booking when were are NOT cloning the timetable (optionas has sessions and contribs)
                # and the booking is linked to a contrib/session
                if (options.get('sessions', False) and options.get('contributions', False)) or not vs.hasSessionOrContributionLink():
                    newBooking = vs.clone(conf)
                    conf.getCSBookingManager().addBooking(newBooking)
                    VidyoTools.getIndexByVidyoRoom().index_obj(newBooking)

class CatalogIndexProvider(Component):
    implements(ICatalogIndexProvider)

    def catalogIndexProvider(self, obj):
        return [(BOOKINGS_BY_VIDYO_ROOMS_INDEX, BookingsByVidyoRoomIndex)]



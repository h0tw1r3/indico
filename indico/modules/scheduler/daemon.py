#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
##
## This file is part of CDS Indico.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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

import sys, getopt, os, time, logging
from MaKaC.common.Configuration import Config

def _isPosix():
    return os.name == "posix"

def _isWindows():
    return os.name == "nt"

def _savePID(pid, pid_file):
    try:
        open(pid_file, "w").write(str(pid))
    except IOError, e:
        print "Exception while trying to store the daemon PID in the file '%s':\n%s" % (linuxPIDFile, e)


def _getPID(printExceptions=True):
    try:
        pid = int(open(linuxPIDFile, "r").read().strip())
        return pid
    except IOError, e:
        if printExceptions:
            print "Exception while opening the file '%s' with the daemon PID:\n%s" % (linuxPIDFile, e)
    except ValueError, e:
        if printExceptions:
            print "Exception while reading the file '%s' with the daemon PID:\nThere is not a PID in the file" % (linuxPIDFile)
    return -1


def _killProcess():
    if not _isPosix():
        return False

    pid = _getPID()
    if pid != -1:
        try:
            os.kill(pid, 9)
        except OSError, e:
            print e
        else:
            os.remove(linuxPIDFile)
            return True

    return False

def initDefaultTasks():
    from datetime import timedelta, datetime
    from pytz import timezone
    try:
        from MaKaC.conference import CategoryManager
        from MaKaC.common import DBMgr
        from MaKaC.common.timerExec import HelperTaskList, StatisticsUpdater, task
        from MaKaC.common.timezoneUtils import nowutc
    except ImportError, e:
        print "ImportError:%s"%e
        sys.exit(0)


    print "\nTrying to connect with the database...\nIf you don't see any following message, please make sure that you have already started the database because you might have a connection problem with it.\n"
    DBMgr.getInstance().startRequest()
    print "Database connection established."
    # ------------------------ STATISTICS ------------------------
    tl = HelperTaskList.getTaskListInstance()
    catRoot = CategoryManager().getRoot()
    try:
        if catRoot.statsUpdater != None:
            tl.removeTask(catRoot.statsUpdater)
            catRoot.statsUpdater = None
    except:
        catRoot.statsUpdater = None
    su = StatisticsUpdater(catRoot)
    su.setId("StatisticsUpdater")
    ta = task()
    d = nowutc() + timedelta(days=1)
    ta.setStartDate(datetime(d.year, d.month, d.day, 1, 0, tzinfo=timezone('UTC')))
    ta.setInterval(timedelta(days=1))
    ta.addObj(su)
    tl.addTask(ta)
    catRoot.statsUpdater = ta
    print "Added statistics updater task to the tasks list."
    # --------------------- END STATISTICS ---------------------
    DBMgr.getInstance().endRequest()
    print ""


def run(log=None):
    from indico.modules.scheduler import Scheduler

    Scheduler().run()
    # initDefaultTasks()


def startScheduler():
    """
    Run the function listed in the toExec instance each 'duration' seconds
    """
    oldPID=_getPID(False)
    if oldPID!=-1:
        print "Scheduler daemon is already running"
        sys.exit(0)

    if _isPosix():
        pid=os.fork()
        if pid==0:
            #Child
            run()
        else:
            #Parent
            _savePID(pid, linuxPIDFile)
            print "Daemon started! (pid=%s)\n"%pid
            time.sleep(3)
    elif _isWindows():
        print "Close this window to stop the server"
        run()
    else:
        print "Impossible to start the daemon"


def stopScheduler():
    if _killProcess():
        print "Daemon stopped!"
    else:
        print "Impossible to stop the process, please do it manually"


def restartScheduler():
    stopScheduler()
    startScheduler()


def main():
    """
    Main cycle
    """

    global linuxPIDFile

    cfg = Config.getInstance()

    # logging setup
    handler = logging.FileHandler(os.path.join(cfg.getLogDir(), 'scheduler.log'), 'a')
    handler.setFormatter(logging.Formatter('%(asctime)s %(process)s %(name)s: %(levelname)-8s %(message)s'))

    root_logger = logging.getLogger('')
    root_logger.addHandler(handler)

#    if MT_MODE == 'PROCESS':
#        mp_logger = multiprocessing.get_logger()
#        mp_logger.setLevel(logging.DEBUG)
#        mp_logger.addHandler(handler)

    cfg = Config.getInstance()
    linuxPIDFile = "%s/IndicoScheduler.pid" % cfg.getLogDir()

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hstr", [ "help", "start", "stop", "restart" ])
    except getopt.GetoptError, e:
        usage()
        sys.exit(2)

    arg = None
    if len(args) == 1:
        arg=args[0]
    elif len(opts)==1:
        arg=opts[0][0]

    if arg:
        if arg in ("start", "s", "-s"):
            startScheduler()
        elif arg in ("stop", "t", "-t"):
            stopScheduler()
        elif arg in ("restart", "r", "-r"):
            restartScheduler()
        elif arg in ("help", "h", "-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit(2)
        return
    else:
        usage()
        sys.exit(2)


def usage():
    print "\nUsage: %s start|stop|restart [-h]\n" % sys.argv[0]
    print "  -h                    Help"
    print "  -s                    Start the scheduler daemon"
    print "  -t                    Stop the scheduler daemon"
    print "  -r                    Restart the scheduler daemon"


if __name__ == "__main__":
    main()
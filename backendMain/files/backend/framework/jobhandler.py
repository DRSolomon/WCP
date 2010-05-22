import imp
import sys
from time import *
from modules.basishandler import *

class jobhandler(object):
    
    def __init__ (self, env):
        self.env = env
        
    def findPendingJobs(self):
        lastRun = localtime(self.env.config.get("last_run_backend"))
        currentTime = localtime()
        
        triggers = ['asap']
        
        if lastRun.tm_hour != currentTime.tm_hour:
            triggers.append('hourchange')
            
        if lastRun.tm_mday != currentTime.tm_mday:
            triggers.append('daychange')
            
        if lastRun.tm_wday == 6 and currentTime.tm_wday == 0:
            triggers.append('weekchange')
            
        if lastRun.tm_mon != currentTime.tm_mon:
            triggers.append('monthchange')
            
        if lastRun.tm_year != currentTime.tm_year:
            triggers.append('yearchange')
        
        self.jobs = self.env.db.queryDict("SELECT * \
                                       FROM     cp" + self.env.cpnr + "_jobhandler_task jt \
                                       WHERE    nextExec IN ('" + "','".join(triggers) + "')\
                                       ORDER BY priority DESC, jobhandlerTaskID ASC")
        
    def firePendingJobs(self):
        for job in self.jobs:
            #try:
                module = self.loadModule(job['jobhandler'])
                func = getattr(module, job['jobhandler'])
                obj = func(job['data'], self.env)
                job['retVar'] = obj.run()
            #except Exception, e:
                #job['retVar'] = e
        
    def finishJobs(self):
        for job in self.jobs:
            if job['retVar'] != 'success':
                #do something here
                print "error ocurred"
                print job
            else:
                if job['volatile'] == 1:
                    self.env.db.query("DELETE FROM cp" + self.env.cpnr + "_jobhandler_task \
                                   WHERE jobhandlerTaskID = " + str(job['jobhandlerTaskID']))
                else:
                    self.env.db.query("UPDATE cp" + self.env.cpnr + "_jobhandler_task \
                                   SET lastExec = UNIX_TIMESTAMP() \
                                   WHERE jobhandlerTaskID = " + str(job['jobhandlerTaskID']))
                      
        self.env.config.set("last_run_backend", int(time()))

    def loadModule(self, name):                
        # Fast path: see if the module has already been imported.
        
        try:
            return sys.modules[name]
        except KeyError:
            pass
        
        name = "modules/" + name

        # If any of the following calls raises an exception,
        # there's a problem we can't handle -- let the caller handle it.
        fp, pathname, description = imp.find_module(name)
    
        try:
            return imp.load_module(name, fp, pathname, description)
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()
        
        
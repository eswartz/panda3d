"""DistributedObject module: contains the DistributedObject class"""

from PandaObject import *
#from ToonBaseGlobal import *

class DistributedObject(PandaObject):
    """Distributed Object class:"""
    def __init__(self, cr):
        try:
            self.DistributedObject_initialized
        except:
            self.DistributedObject_initialized = 1
            self.cr = cr
        return None

    def disable(self):
        """disable(self)
        Inheritors should redefine this to take appropriate action on disable
        """
        pass

    def delete(self):
        """delete(self)
        Inheritors should redefine this to take appropriate action on delete
        """
        pass

    def generate(self):
        """generate(self)
        Inheritors should redefine this to take appropriate action on generate
        """
        pass
    
    def getDoId(self):
        """getDoId(self)
        Return the distributed object id
        """
        return self.doId
    
    def updateRequiredFields(self, cdc, di):
        for i in cdc.allRequiredCDU:
            i.updateField(cdc, self, di)

    def updateRequiredOtherFields(self, cdc, di):
        # First, update the required fields
        for i in cdc.allRequiredCDU:
            i.updateField(cdc, self, di)
        # Determine how many other fields there are
        numberOfOtherFields = di.getArg(STUint16)
        # Update each of the other fields
        for i in range(numberOfOtherFields):
            cdc.updateField(self, di)
        return None

    def sendUpdate(self, fieldName, args):
        self.cr.sendUpdate(self, fieldName, args)

    def taskName(self, taskString):
        return (taskString + "-" + str(self.getDoId()))
    



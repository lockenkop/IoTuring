from Logger.Logger import Logger

from threading import Thread
import time

DEFAULT_LOOP_TIMEOUT = 3

class Warehouse():
    name = "Unnamed"
    
    def __init__(self) -> None:
        self.entities = []
        self.loopTimeout = DEFAULT_LOOP_TIMEOUT

    def AddEntity(self, entityInstance) -> None:
        """ Add an entity instance to the warehouse's enitities """
        self.entities.append(entityInstance)

    def Start(self) -> None:
        """ Start a thread that will loop the Loop function"""
        Thread(target=self.LoopThread).start()

    def SetLoopTimeout(self, timeout) -> None:
        """ Set a timeout between 2 loops """
        self.loopTimeout = timeout

    def ShouldCallLoop(self) -> bool:
        """ Wait the timeout time and then tell it can run the Loop function """
        time.sleep(self.loopTimeout)
        return True 

    def LoopThread(self) -> None:
        """ Entry point of the warehouse thread, will run Loop() periodically """
        while(True):
            if self.ShouldCallLoop():
                self.Loop()

    def GetEntities(self) -> list:
        return self.entities

    def Loop(self) -> None:
        """ Must be implemented in subclasses """
        pass

    def GetName(self) -> str:
        return self.name

    def Log(self, messageType, message) -> None:
        Logger.getInstance().Log(messageType, self.GetName() + " Warehouse", message)
        

    # Example Call: class.ConfigurationPreset(class)

    # These must be places only in subclasses of warehouses
    def InstantiateWithConfiguration(self,configuration):
        """ Receive a configuration and instantiate the warehouse with the correct ordered parameters """
        return 


    def ConfigurationPreset(self):
        """ Prepare a preset to manage settings insert/edit for the warehouse """
        return None
class Scene:
    instances = []
    def update(self, dt):
        for instance in self.instances:
            instance.update(dt)
    def render(self):
        for instance in self.instances:
            instance.render()

    def leave(self): 
        while len(self.instances) > 0:
            self.instances.pop(0)


    def addInstance(self, object):
        self.instances.append(object)

    def destroyInstance(self, object, runDestroyEvent = True):
        try:
            idx = self.instances.index(object)
            if runDestroyEvent: object.destroy()
            self.instances.pop(idx)
        except ValueError:
            print("WARNING!! attempted to remove non-existent instance in scene")

    def destroyInstanceByName(self, objectName, runDestroyEvent = True):
        for instance in self.instances:
            if instance.__class__.__name__ == objectName:
                self.destroyInstance(instance)

    def instanceExists(self, object):
        try:
            idx = self.instances.index(object)
            return True
        except ValueError:
            return False
    def instanceExistsByName(self, objectName):
        for instance in self.instances:
            if instance.__class__.__name__ == objectName: return True
            
        return False
        
class Scene:
    instances = []
    def update(self, dt):
        for instance in self.instances:
            instance.update(dt)
    def render(self):
        for instance in self.instances:
            instance.render()


    def addInstance(self, object):
        self.instances.append(object)

    def destroyInstance(self, object):
        try:
            idx = self.instances.index(object)
            self.instances.pop(idx)
        except ValueError:
            print("WARNING!! attempted to remove non-existent instance in scene")

    def instanceExists(self, object):
        try:
            idx = self.instances.index(object)
            return True
        except ValueError:
            return False
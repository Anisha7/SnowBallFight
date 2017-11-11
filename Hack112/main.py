import direct.directbase.DirectStart
 

class MyApp(ShowBase):

   def __init__(self):

        # load environment
        self.scene = self.loadModel("panda3d-master/models/environment.egg")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

# hi there

run()

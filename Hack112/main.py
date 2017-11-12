from math import pi, sin, cos
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task


class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
        
        self.win.setClearColor((1, 1, 1, 1))

        # environment setup
        self.environ = loader.loadModel("models/world")
        self.environ.reparentTo(render)
        # Load the environment model.
    #     self.scene = self.loader.loadModel("models/environment")
    #     # Reparent the model to render.
    #     self.scene.reparentTo(render)

    #     # Apply scale and position transforms on the model.
    #     self.scene.setScale(0.25, 0.25, 0.25)
    #     self.scene.setPos(-8, 42, 0)

<<<<<<< HEAD
run()

# test hi there
=======
    #     self.scene.setColor(0, 1, 1, 1)
 
 # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
         # Update to fit player movement, rotate as player rotates
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
 
app = MyApp()
app.run()
>>>>>>> 0fc624daf45a0b9e19a75e6cbfaa58237659b1cb

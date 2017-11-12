#############################
# Sockets Client Demo
# by Rohan Varma
# adapted by Kyle Chin
#############################
import socket
import threading
from queue import Queue
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random
import sys
import os
import math
from ralph import * 

HOST = "localhost" # put your IP address here if playing on multiple computers
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

####################################
# customize these functions
####################################

def keyPressed(event, data):
    dx, dy = 0, 0
    msg = ""

    # moving
    if event.keysym in ["Up", "Down", "Left", "Right"]:
      speed = 5
      if event.keysym == "Up":
        dy = -speed
      elif event.keysym == "Down":
        dy = speed
      elif event.keysym == "Left":
        dx = -speed
      elif event.keysym == "Right":
        dx = speed
      # move myself
      data.me.move(dx, dy)
      # update message to send
      msg = "playerMoved %d %d\n" % (dx, dy)

    # teleporting
    elif event.keysym == "space":
      # get a random coordinate
      x = random.randint(0, data.width)
      y = random.randint(0, data.height)
      # teleport myself
      data.me.teleport(x, y)
      # update the message
      msg = "playerTeleported %d %d\n" % (x, y)

    # send the message to other players!
    if (msg != ""):
      print ("sending: ", msg,)
      data.server.send(msg.encode())

# def timerFired(data):
#     # timerFired receives instructions and executes them
#     if (serverMsg.qsize() > 0):
#       msg = serverMsg.get(False)
#       try:
#         print("received: ", msg, "\n")
#         msg = msg.split()
#         command = msg[0]

#         if (command == "myIDis"):
#           myPID = msg[1]
#           data.me.changePID(myPID)

#         elif (command == "newPlayer"):
#           newPID = msg[1]
#           #data.otherStrangers[newPID] = Dot(newPID, x, y)
#           data.otherStrangers[newPID] = Ralph(newPID)

#         elif (command == "playerMoved"):
#           PID = msg[1]
#           dx = int(msg[2])
#           dy = int(msg[3])
#           data.otherStrangers[PID].move(dx, dy)

#         elif (command == "playerTeleported"):
#           PID = msg[1]
#           x = int(msg[2])
#           y = int(msg[3])
#           data.otherStrangers[PID].teleport(x, y)
#       except:
#         print("failed")
#       serverMsg.task_done()


###############################################################################
#!/usr/bin/env python

# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller
#
# Last Updated: 2015-03-13
#
# This tutorial provides an example of creating a character
# and having it walk around on uneven terrain, as well
# as implementing a fully rotatable camera.



# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.07,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))

class RoamingRalphDemo(ShowBase):
    def __init__(self, data):
        # Set up the window, camera, etc.
        ShowBase.__init__(self)

        self.otherStrangers = dict()
        self.otherStrangersIsMoving = dict()
        self.data = data
        # Set the background color to black
        self.win.setClearColor((0, 0, 0, 1))

        # This is used to store which keys are currently pressed.
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "cam-left": 0, "cam-right": 0}

        # Post the instructions
        self.title = addTitle(
            "Panda3D Tutorial: Roaming Ralph (Walking on Uneven Terrain)")
        self.inst1 = addInstructions(0.06, "[ESC]: Quit")
        self.inst2 = addInstructions(0.12, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.18, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.24, "[Up Arrow]: Run Ralph Forward")
        self.inst6 = addInstructions(0.30, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.36, "[S]: Rotate Camera Right")

        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.

        self.environ = loader.loadModel("models/world")
        self.environ.reparentTo(render)

        # Create the main character, Ralph

        ralphStartPos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})

        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(ralphStartPos + (0, 0, 0.5))
        print(ralphStartPos)

        

        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(2.0)

        # Accept the control keys for movement and rotation

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_up", self.setKey, ["forward", True])
        self.accept("a", self.setKey, ["cam-left", True])
        self.accept("s", self.setKey, ["cam-right", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("arrow_up-up", self.setKey, ["forward", False])
        self.accept("a-up", self.setKey, ["cam-left", False])
        self.accept("s-up", self.setKey, ["cam-right", False])

        taskMgr.add(self.move, "moveTask")
        taskMgr.add(self.timerFired, "timerTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)

        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0, 0, 9)
        self.ralphGroundRay.setDirection(0, 0, -1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.ralphGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0, 0, 9)
        self.camGroundRay.setDirection(0, 0, -1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = self.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Uncomment this line to see the collision rays
        #self.ralphGroundColNp.show()
        #self.camGroundColNp.show()

        # Uncomment this line to show a visual representation of the
        # collisions occuring
        #self.cTrav.showCollisions(render)

        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((-5, -5, -5))
        directionalLight.setColor((1, 1, 1, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
        startpos = self.ralph.getPos()
        
        if self.keyMap["cam-left"]:
            msg = ""
            self.camera.setX(self.camera, -20 * dt)
            msg = "cameraMovedLeft\n"
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())
        elif self.keyMap["cam-right"]:
            msg = ""
            self.camera.setX(self.camera, +20 * dt)
            msg = "cameraMovedRight\n"
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())
        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        # startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.
        elif self.keyMap["left"]:
            msg = ""
            self.ralph.setH(self.ralph.getH() + 300 * dt)
            msg = "playerRotatedLeft %f\n" % (300 * dt)
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())
        elif self.keyMap["right"]:
            msg = ""
            self.ralph.setH(self.ralph.getH() - 300 * dt)
            msg = "playerRotatedRight %f\n" % (300 * dt)
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())
        elif self.keyMap["forward"]:
            msg = ""
            self.ralph.setY(self.ralph, -25 * dt)
            msg = "playerForwarded %f\n" % (-25 * dt)
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())
        else:
            msg = ""
            msg = "NoCommands\n"
            if (msg != ""):
                print ("sending: ", msg)
                self.data.server.send(msg.encode())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"]:
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk", 5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # Normally, we would have to call traverse() to check for collisions.
        # However, the class ShowBase that we inherit from has a task to do
        # this for us, if we assign a CollisionTraverser to self.cTrav.
        #self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = list(self.ralphGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.

        entries = list(self.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.camera.getZ() < self.ralph.getZ() + 2.0:
            self.camera.setZ(self.ralph.getZ() + 2.0)

        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        self.camera.lookAt(self.floater)
        return task.cont

    def timerFired(self, task):
    # timerFired receives instructions and executes them
        if (self.data.serverMsg.qsize() > 0):
            msg = self.data.serverMsg.get(False)
            #try:
            print("received: ", msg, "\n")
            msg = msg.split()
            command = msg[0]

            if (command == "myIDis"):
                # myPID = msg[1]
                # data.me.changePID(myPID)
                pass

            elif (command == "newPlayer"):
                print("there is a new player")
                newPID = msg[1]
                print(newPID)
                #data.otherStrangers[newPID] = Dot(newPID, x, y)
                ralphStartPos = self.environ.find("**/start_point").getPos()
                self.otherStrangers[newPID] = Actor("models/ralph",
                       {"run": "models/ralph-run",
                        "walk": "models/ralph-walk"})
                self.otherStrangersIsMoving[newPID] = False
                self.otherStrangers[newPID].reparentTo(render)
                self.otherStrangers[newPID].setScale(.2)
                self.otherStrangers[newPID].setPos(ralphStartPos + (0, 0, 0.5))
                print(ralphStartPos)

            elif (command == "playerForwarded"):
                print("other player forward")
                PID = msg[1]
                dy = float(msg[2])
                print(PID, dy)
                print(self.otherStrangers[PID].getY())
                print(type(self.otherStrangers[PID]))
                self.otherStrangers[PID].setY(self.otherStrangers[PID], dy)
                # self.ralph.setY(self.ralph, -25 * dt)
                print(self.otherStrangers[PID].getY())
                if self.otherStrangersIsMoving[PID] is False:
                    self.otherStrangers[PID].loop("run")
                    self.otherStrangersIsMoving[PID] = True

            elif (command == "playerRotatedLeft"):
                print("other player rotated left")
                PID = msg[1]
                dtheta = float(msg[2])
                print(PID, dtheta)
                print(self.otherStrangers[PID].getH())
                print(type(self.otherStrangers[PID]))
                # self.ralph.setH(self.ralph.getH() + 300 * dt)
                self.otherStrangers[PID].setH(self.otherStrangers[PID].getH()+dtheta)
                # self.ralph.setY(self.ralph, -25 * dt)
                print(self.otherStrangers[PID].getH())
                if self.otherStrangersIsMoving[PID] is False:
                    self.otherStrangers[PID].loop("run")
                    self.otherStrangersIsMoving[PID] = True

            elif (command == "playerRotatedRight"):
                print("other player rotated right")
                PID = msg[1]
                dtheta = float(msg[2])
                print(PID, dtheta)
                print(self.otherStrangers[PID].getH())
                print(type(self.otherStrangers[PID]))
                # self.ralph.setH(self.ralph.getH() + 300 * dt)
                self.otherStrangers[PID].setH(self.otherStrangers[PID].getH()-dtheta)
                # self.ralph.setY(self.ralph, -25 * dt)
                print(self.otherStrangers[PID].getH())
                if not self.otherStrangersIsMoving[PID]:
                    print("I'm here")
                    self.otherStrangers[PID].loop("run")
                    self.otherStrangersIsMoving[PID] = True

            elif (command == "cameraMovedLeft"):
                print("other player moved camrea left")
                PID = msg[1]
                print(PID)
                print(self.otherStrangersIsMoving[PID])
                if self.otherStrangersIsMoving[PID]:
                    print("has successfully resetted it to true")
                    self.otherStrangers[PID].stop()
                    self.otherStrangers[PID].pose("walk", 5)
                    self.otherStrangersIsMoving[PID] = False

            elif (command == "cameraMovedRight"):
                PID = msg[1]
                print("other player moved camrea right")
                print(PID)
                print(self.otherStrangersIsMoving[PID])
                if self.otherStrangersIsMoving[PID]:
                    print("has successfully resetted it to true")
                    self.otherStrangers[PID].stop()
                    self.otherStrangers[PID].pose("walk", 5)
                    self.otherStrangersIsMoving[PID] = False

            else:
                print("no keyinputs from other player")
                PID = msg[1]
                print(PID)
                print(self.otherStrangersIsMoving[PID])
                if self.otherStrangersIsMoving[PID]:
                    print("has successfully resetted it to true")
                    self.otherStrangers[PID].stop()
                    self.otherStrangers[PID].pose("walk", 5)
                    self.otherStrangersIsMoving[PID] = False

            #except:
                #print("failed")

            self.data.serverMsg.task_done()


        return task.cont






def init(data):
    # data.me = Dot("Lonely", data.width/2, data.height/2)
    # data.me = Ralph("Lonely")
    # data.otherStrangers = dict()
    pass

def runMe(serverMsg=None, server=None):
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    init(data)
    demo = RoamingRalphDemo(data)
    demo.run()

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

runMe(serverMsg, server)



# try a list of actors
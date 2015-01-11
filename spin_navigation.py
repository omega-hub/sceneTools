# Keys
#  - Mouse Right button + movement rotates the model
#  - Mouse wheel zooms in/out
# Use 
#  import spin_navigation
#  spin_navigation.root = [root node that you want to manipulate]
from omega import *
from euclid import *
from math import *
 
startPos = None
rotating = False
 
# Set this variable to the object that you want to rotate/scale.
root = None
 
def onEvent():
    global startPos
    global rotating
    global root
    e = getEvent()
    if(e.isButtonDown(EventFlags.Right)):
        startPos = e.getPosition()
        rotating = True
    elif(e.isButtonUp(EventFlags.Right)):
        rotating = False
    
    if(rotating == True and e.getServiceType() == ServiceType.Pointer 
    and e.getType() == EventType.Move):
        dx = e.getPosition().x - startPos.x
        dy = e.getPosition().y - startPos.y
        startPos = e.getPosition()
        root.rotate(Vector3(0, 1, 0), radians(dx), Space.World)
        root.rotate(Vector3(1, 0, 0), radians(dy), Space.World)
        #root.roll(radians(dx))
        
    if(e.getServiceType() == ServiceType.Pointer 
    and e.getType() == EventType.Zoom):
        zoom = e.getExtraDataInt(0)
        s = 0.9
        if(zoom > 0): s = 1.1
        root.setScale(root.getScale() * s)
        
    
setEventFunction(onEvent)    
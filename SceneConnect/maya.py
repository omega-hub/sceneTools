import maya.cmds as cmds
import subprocess
selectedObject = None

# Path to the omegalib binary directory on the system (where orun and olaunch live) 
omegalibPath = "D:/Workspace/omegalib/build/bin/release/"

# Name of the script to start when launching an application
scriptName = "cyclops/examples/python/spincube.py"

# When set to true, the application will run using the remote application
# launcher (olauncher)
remoteRun = False

# The target execution machine, when launching an application in remote mode
targetMachine = "localhost"

# The name of the sceneImport module in the application script. This is needed
# to make runtime object editing possible.
# The beginning of the application script should have a line like
# > from sceneTools import sceneImport as [X]
# where [X} is the scene module name. We use 'scene' as a default scene module name
sceneModuleName = "scene"

#------------------------------------------------------------------------------
# Build and run button clicked
def onRunButtonClick(e):
    subprocess.Popen(omegalibPath + "orun -s cyclops/examples/python/spincube.py")

#------------------------------------------------------------------------------
# Application stop button clicked
def onStopButtonClick(e):
    connect(targetMachine)
    sendCommand('oexit()')
    bye()
    
#------------------------------------------------------------------------------
# Create the SceneConnect GUI
def showSceneConnectUI():
        # delete window if already exists
        if cmds.window("omegaSceneConnect", exists=True):
            cmds.deleteUI("omegaSceneConnect")
        
        window = cmds.window("omegaSceneConnect", title = "Omegalib SceneConnect", w=300, h=300, mnb=False,mxb=False)
        cmds.showWindow(window)
        
        mainLayout = cmds.columnLayout(w=300,h=300)
        omegaPathText = cmds.textField(annotation="Omegalib Path:")
        
        runButton = cmds.button(label='Build and Run', w=300, h=50, command=onRunButtonClick)
        stopButton = cmds.button(label='Stop', w=300, h=50, command=onStopButtonClick)


#------------------------------------------------------------------------------
# handle translation events
translateXJobId = 0
translateYJobId = 0
translateZJobId = 0
def onTranslate():
    if(selectedObject.startswith('o_')):
        objname = selectedObject[2:].split('_')[0]
        x = cmds.getAttr(selectedObject + '.translateX')
        y = cmds.getAttr(selectedObject + '.translateY')
        z = cmds.getAttr(selectedObject + '.translateZ')
        print('Translating ' + objname + 'to ' + str((x, y, z)))
        sendCommand('scene.objects.' + objname + '.setPosition' + str((x, y, z)))

#------------------------------------------------------------------------------
# handle rotation events
rotateXJobId = 0
rotateYJobId = 0
rotateZJobId = 0
def onRotate():
    if(selectedObject.startswith('o_')):
        objname = selectedObject[2:].split('_')[0]
        x = cmds.getAttr(selectedObject + '.rotateX')
        y = cmds.getAttr(selectedObject + '.rotateY')
        z = cmds.getAttr(selectedObject + '.rotateZ')
        print('Rotating ' + objname + 'to ' + str((x, y, z)))
        sendCommand('scene.objects.' + objname + '.setOrientation(quaternionFromEulerDeg' + str((x, y, z)) + ')')

        
#------------------------------------------------------------------------------
# selection changed handler: rewire event handlers on selection change 
def onSelectionChanged():
    global selectedObject
    global translateXJobId
    global translateYJobId
    global translateZJobId
    global rotateXJobId
    global rotateYJobId
    global rotateZJobId
    
    sel = cmds.ls(selection=True)
    print(sel)
    
    # kill old event handlers
    if(selectedObject != None):
        cmds.scriptJob(kill=translateXJobId)
        cmds.scriptJob(kill=translateYJobId)
        cmds.scriptJob(kill=translateZJobId)
        cmds.scriptJob(kill=rotateXJobId)
        cmds.scriptJob(kill=rotateYJobId)
        cmds.scriptJob(kill=rotateZJobId)
    
    # on new selection, connect to client
    if(len(sel) > 0 and selectedObject == None):
        connect(targetMachine)
    
    # if selection has cleared, disconnect from client
    if(len(sel) == 0 and selectedObject != None):
        bye()
    
    if(len(sel) > 0):
        selectedObject = sel[0]
        translateXJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateX", onTranslate])
        translateYJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateY", onTranslate])
        translateZJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateZ", onTranslate])
        rotateXJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateX", onRotate])
        rotateYJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateY", onRotate])
        rotateZJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateZ", onRotate])
        print('sel changed ' + selectedObject)
    else:
       selectedObject = None
    
#------------------------------------------------------------------------------
# initialize the script
cmds.scriptJob(killAll=True)
cmds.scriptJob(event=["SelectionChanged", onSelectionChanged])
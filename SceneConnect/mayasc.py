import maya.cmds as cmds
import maya.mel as mel
import subprocess
import os
from mcsend import *
selectedObject = None

# Path to the omegalib binary directory on the system (where orun and olaunch live) 
omegalibPath = "D:/Workspace/omegalib/build/bin/release/"

# The target execution machine, when launching an application in remote mode
targetMachine = "localhost"

# The name of the sceneImport module in the application script. This is needed
# to make runtime object editing possible.
# The beginning of the application script should have a line like
# > from sceneTools import sceneImport as [X]
# where [X} is the scene module name. We use 'scene' as a default scene module name
sceneModuleName = "scene"

runningRemote = False

# set to true when we are running the current
# scene in omegalib.
running = False

# Load saved options if available
if(cmds.optionVar(exists='omegalibPath')):
    omegalibPath = cmds.optionVar(q='omegalibPath')
if(cmds.optionVar(exists='targetMachine')):
    targetMachine = cmds.optionVar(q='targetMachine')
if(cmds.optionVar(exists='sceneModuleName')):
    sceneModuleName = cmds.optionVar(q='sceneModuleName')


#------------------------------------------------------------------------------
# Build and run button clicked
def onRunButtonClick(e):
    global runningRemote
    global running
    projectPath = cmds.file(sceneName=True, query=True)
    projectFile = os.path.basename(projectPath)
    projectPath = os.path.dirname(projectPath)
    
    # entry script name = maya file name
    scriptName = projectFile[:-3] + '.py'
    
    #export the current scene to fbx.
    mel.eval('FBXExport -f "'+projectPath + '/' + projectFile[:-3]+'".fbx')
    
    command = '{0}/orun -s {1}/{2}'.format(omegalibPath, projectPath, scriptName)
    runningRemote = False
    running = True
    subprocess.Popen(command)

#------------------------------------------------------------------------------
# Build and run button clicked
def onRunRemoteButtonClick(e):
    global targetMachine
    global runningRemote
    
    projectPath = cmds.file(sceneName=True, query=True)
    projectFile = os.path.basename(projectPath)
    projectPath = os.path.dirname(projectPath)
    
    # entry script name = maya file name
    scriptName = projectFile[:-3] + '.py'
    
    #export the current scene to fbx.
    mel.eval('FBXExport -f "'+projectPath + '/' + projectFile[:-3]+'".fbx')
    
    command = '{0}/olauncher -s {1} -h {2}'.format(omegalibPath, scriptName, targetMachine)
    global runningRemote
    global running
    running = True
    runningRemote = True
    subprocess.Popen(command, cwd=projectPath)

#------------------------------------------------------------------------------
# Application stop button clicked
def onStopButtonClick(e):
    global runningRemote
    global running
    if(runningRemote):
        connect(targetMachine)
    else:
        connect('localhost')
    sendCommand('oexit()')
    bye()
    running = False
    
#------------------------------------------------------------------------------
# Omegalib path set button click
def onOmegalibPathButtonClick():
    p = cmds.fileDialog2(fileMode=3)
    global omegalibPathBox
    cmds.textFieldButtonGrp(omegalibPathBox, edit=True, text=p[0])
    
#------------------------------------------------------------------------------
def onOkButtonClick(e):
    # Save options
    global omegalibPath
    global sceneModuleName
    global targetMachine
    
    omegalibPath = cmds.textFieldButtonGrp(omegalibPathBox, query=True, text=True)
    sceneModuleName = cmds.textFieldGrp(sceneModuleBox, query=True, text=True)
    targetMachine = cmds.textFieldGrp(targetMachineBox, query=True, text=True)
    cmds.optionVar(stringValue=('omegalibPath', omegalibPath))
    cmds.optionVar(stringValue=('sceneModuleName', sceneModuleName))
    cmds.optionVar(stringValue=('targetMachine', targetMachine))
    cmds.deleteUI("omegaSceneConnectWindow")

#------------------------------------------------------------------------------
def onCancelButtonClick(e):
    cmds.deleteUI("omegaSceneConnectWindow")

#------------------------------------------------------------------------------
# Create the SceneConnect GUI
def showSceneConnectUI():
        # delete window if already exists
        if cmds.window("omegaSceneConnectWindow", exists=True):
            cmds.deleteUI("omegaSceneConnectWindow")
        
        window = cmds.window("omegaSceneConnectWindow", w=300, h=200, title = "Omegalib SceneConnect", mnb=False,mxb=False)
        
        layout = cmds.columnLayout(adjustableColumn=True)
        
        global omegalibPathBox
        omegalibPathBox = cmds.textFieldButtonGrp(label="Omegalib Path:", text=omegalibPath, buttonLabel="...", adjustableColumn=2, buttonCommand=onOmegalibPathButtonClick)
        
        global targetMachineBox
        targetMachineBox = cmds.textFieldGrp(label="Target Machine:", text=targetMachine, adjustableColumn=2)
        
        global sceneModuleBox
        sceneModuleBox = cmds.textFieldGrp(label="Scene Module Name:", text = sceneModuleName, adjustableColumn=2)
        
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1)
        cmds.separator(style='none')
        cmds.button(label='Ok', command=onOkButtonClick)
        cmds.button(label='Cancel', command=onCancelButtonClick)
        cmds.showWindow(window)

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
# handle node name change events
def onNodeNameChange():
    global selectedObject
    oldSelectedObject = selectedObject
    selectedObject = cmds.ls(selection=True)
    selectedObject = selectedObject[0]
    if(selectedObject.startswith('o_')):
        args = selectedObject[2:].split('_')
        print('args ' + str(len(args)))
        if(len(args) == 2):
            objname = args[0]
            className = args[1]
            
            oldargs = selectedObject[2:].split('_')
            if(len(oldargs) == 2):
                oldobjname = args[0]
                oldclassName = args[1]
                # delete old label
                if(cmds.objExists(oldobjname + '_label')):
                    cmds.delete(oldobjname + '_label')
            
            x = cmds.getAttr(selectedObject + '.translateX')
            y = cmds.getAttr(selectedObject + '.translateY')
            z = cmds.getAttr(selectedObject + '.translateZ')
            a = cmds.annotate(selectedObject, point=(x,y + 1,z), text=className)
            a = cmds.rename(a, objname + '_label')
            cmds.parent(a, selectedObject, shape=True)
            
            # color this object wireframe differently
            cmds.color(selectedObject, userDefined = 1)
            cmds.color(a, userDefined = 1)
            
            # After creating the annotation, it will be selected.
            # re-select the original object
            cmds.select(selectedObject)
        
        
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
    global nameChangeJobId
    global running
    
    sel = cmds.ls(selection=True)
    
    if(not running):
        # NOTE: name change handler is processed even when maya is not connected
        # to a running omegalib application.
        # kill old event handlers
        if(selectedObject != None):
            cmds.scriptJob(kill=nameChangeJobId)
        if(len(sel) > 0):
            selectedObject = sel[0]
            nameChangeJobId = cmds.scriptJob(nodeNameChanged=[selectedObject, onNodeNameChange])
        else:
           selectedObject = None
    else:
        # kill old event handlers
        if(selectedObject != None):
            cmds.scriptJob(kill=translateXJobId)
            cmds.scriptJob(kill=translateYJobId)
            cmds.scriptJob(kill=translateZJobId)
            cmds.scriptJob(kill=rotateXJobId)
            cmds.scriptJob(kill=rotateYJobId)
            cmds.scriptJob(kill=rotateZJobId)
            cmds.scriptJob(kill=nameChangeJobId)
        
        # on new selection, connect to client
        if(len(sel) > 0 and selectedObject == None):
            print('connecting')
            connect(targetMachine)
        
        # if selection has cleared, disconnect from client
        if(len(sel) == 0 and selectedObject != None):
            print('disconnecting')
            bye()
        
        if(len(sel) > 0):
            selectedObject = sel[0]
            translateXJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateX", onTranslate])
            translateYJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateY", onTranslate])
            translateZJobId = cmds.scriptJob(attributeChange=[selectedObject + ".translateZ", onTranslate])
            rotateXJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateX", onRotate])
            rotateYJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateY", onRotate])
            rotateZJobId = cmds.scriptJob(attributeChange=[selectedObject + ".rotateZ", onRotate])
            nameChangeJobId = cmds.scriptJob(nodeNameChanged=[selectedObject, onNodeNameChange])
        else:
           selectedObject = None
    
#------------------------------------------------------------------------------
# initialize the script
cmds.scriptJob(killAll=True)
cmds.scriptJob(event=["SelectionChanged", onSelectionChanged])


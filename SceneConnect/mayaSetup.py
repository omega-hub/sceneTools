import os
import sys
import re
import maya.cmds
import maya.mel
import shutil

def srcDirMissing(SrcDir):
    if not os.path.exists(os.path.normpath(SrcDir)):
        maya.cmds.confirmDialog(title=what+' install', message='Sorry, the directory\n"%s"\ndoes not appear to exist'%(SrcDir),button='OK')
        return True
    return False

def setup(VisToolsDir=None, HasValidPyPath=None):
    what = "OmegalibSceneConnect"
    # vistoolsdir is path to SceneConnect directory. Get as parameter or
    # figure it out here.
    visToolsDir = VisToolsDir
    if visToolsDir is None:
        sceneName = maya.cmds.file(sn=True,q=True)
        visToolsDir = os.path.split(sceneName)[0]
    
    # mel and python dirs are the same. If we miss any of them, exit.    
    visMelPath = visToolsDir
    visPyPath = visToolsDir
    if srcDirMissing(visToolsDir) or srcDirMissing(visMelPath) or srcDirMissing(visPyPath):
        return
        
    mayaVers = os.path.split(os.environ['MAYA_LOCATION'])[-1].__str__()[4:]
    x64 = os.environ.get('PROCESSOR_ARCHITECTURE','32bit')
    if x64 == 'AMD64':
        mayaVers += '-x64'
        
    homeDir = os.environ.get('HOME','.')
    # copy icons to homedir/maya/mayaveers/prefs/icons
    mayaIconDir=os.path.join(homeDir,'maya',mayaVers,'prefs','icons')
    mayaShelfDir=os.path.join(homeDir,'maya',mayaVers,'prefs','shelves')
    shutil.copyfile(visToolsDir + "/options.png", mayaIconDir + "/options.png")
    shutil.copyfile(visToolsDir + "/run.png", mayaIconDir + "/run.png")
    shutil.copyfile(visToolsDir + "/runRemote.png", mayaIconDir + "/runRemote.png")
    shutil.copyfile(visToolsDir + "/stop.png", mayaIconDir + "/stop.png")
    
    userSetupFile = None
    userPythonFile = None
    needMel = False
    needPy = True
    if HasValidPyPath is not None:
        needPy = not HasValidPyPath
    else:
        needPy = not sys.path.__contains__(visPyPath)
    existingMelPaths = maya.mel.eval('getenv "MAYA_SHELF_PATH"').split(';')
    needMel = existingMelPaths.__contains__(visMelPath)
    if not (needMel or needPy):
        maya.cmds.confirmDialog(title=what+' install', message='The correct paths are\nalready installed!\nNo need for changes.', messageAlign='center',button='OK')
        return
    needMel = not needMel
    for pName in existingMelPaths:
        if os.path.exists(pName):
            if needMel:
                m = os.path.join(pName,'userSetup.py')
                if os.path.exists(m):
                    userSetupFile = m
    fm = 'w'
    if userSetupFile:
        fm = 'a'
    else:
        mayaDefaultScriptDir = os.path.join(homeDir,'maya',mayaVers,'scripts')
        if not os.path.exists(mayaDefaultScriptDir):
            maya.cmds.confirmDialog(title=what+' install failure',message='Cannot find location to create userSetup.mel\n%s'%(mayaDefaultScriptDir),button='OK')
            return
        userSetupFile = os.path.join(mayaDefaultScriptDir,'userSetup.py')
    fp = open(userSetupFile,fm)
    fp.write('# '+what+' '+'='*20+'\n\n')
    fp.write('import sys\n')
    #vx = re.sub(r'\\',r'\\\\',visPyPath)
    fp.write('sys.path.append("%s")\n'%(visPyPath))
    fp.write('import mayasc\n')

    fp.write('\n')
    fp.close()
    
    # copy shelf
    shutil.copyfile(visToolsDir + "/shelf_SceneConnect.mel", mayaShelfDir + "/shelf_SceneConnect.mel")
    
    
    maya.cmds.confirmDialog(title=what+' install', message="Installation done! Reopen Maya to start using SceneConnect.", messageAlign='center', button='OK')

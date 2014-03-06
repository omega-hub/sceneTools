from cyclops import *
from sceneTools import sceneImport as scene

def SpotLight(node):
    light = Light.create()
    node.addChild(light)
    node.setVisible(False)
    light.setLightType(LightType.Spot)
    light.setSpotCutoff(70)
    light.setSpotExponent(4)
    light.setLightDirection(Vector3(0,-1,0))
    light.setColor(Color(0.4,0.4,0.4,1))
    #light.setAmbient(Color(0.2,0.2,0.2,1))
    sm = ShadowMap()
    sm.setSoft(True)
    light.setShadow(sm)

scene.importFile("simpleScene.fbx", globals())

scene.root.setScale(0.2, 0.2, 0.2)
scene.root.setEffect("colored")

cam = getDefaultCamera()
cam.setPosition(0, 0, 6)
cam.lookAt(scene.root.getPosition(), Vector3(0, 1, 0))
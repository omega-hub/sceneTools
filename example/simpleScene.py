from cyclops import *
from sceneTools import sceneImport as scene

def light(node):
    print('creating light')
    light = Light.create()
    node.addChild(light)
    node.setVisible(False)
    light.setLightType(LightType.Spot)
    light.setSpotCutoff(70)
    light.setSpotExponent(4)
    light.setLightDirection(Vector3(0,-1,0))
    light.setColor(Color(1,1,1,1))
    light.setAmbient(Color(0.2,0.2,0.2,1))
    sm = ShadowMap()
    light.setShadow(sm)

scene.importFile("simpleScene.fbx", globals())

scene.root.setScale(0.2, 0.2, 0.2)
scene.root.setEffect("colored")

# create some ambient light
lightAmbient = Light.create()
lightAmbient.setLightType(LightType.Directional)
lightAmbient.setLightDirection(Vector3(0.1, -1, 0))
lightAmbient.setAmbient(Color(0.2,0.2,0.3,1))
lightAmbient.setColor(Color(0.3,0.3,0.1,1))


cam = getDefaultCamera()
cam.setPosition(0, 0, -10)
cam.lookAt(Vector3(0,2,0), Vector3(0, 1, 0))
from cyclops import *

class OBJS: pass

model = None
root = None
objects = OBJS()


def importFile(filename, callerGlobals, optimize=False):
    global model
    global root
    
    # Load a static model
    model = ModelInfo()
    model.name = "scene"
    model.path = filename
    model.optimize = optimize
    getSceneManager().loadModel(model)

    # Create a scene object using the loaded model
    root = StaticObject.create("scene")
    _traverse('', '', callerGlobals)
    
def _traverse(path, lastChild, callerGlobals):
    #print('traversing ' + path)
    pieces = root.listPieces(path)
    for p in pieces:
        if(p != lastChild):
            if p.startswith('o_'):
                objname = p[2:]
                args = objname.split('_')
                # add an attribute to objects pointing to this scene object
                piecePath = path + '/' + p
                piecePath = piecePath.strip('/')
                setattr(objects, args[0], root.getPiece(piecePath))
                # see if we have a creator function name for this object.
                # if we do, invoke it.
                if(len(args) == 2):
                   cmd = args[1] + '(objects.' + args[0] + ')'
                   #print('calling ' + cmd)
                   eval(cmd, callerGlobals, globals())
            # recurse traversal
            childpath = path + p + '/'
            _traverse(childpath, p, callerGlobals)

    
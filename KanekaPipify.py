#    (C) Copyright 2015 by Autodesk, Inc.
#    Permission to use, copy, modify, and distribute this software in
#    object code form for any purpose and without fee is hereby granted,
#    provided that the above copyright notice appears in all copies and
#    that both that copyright notice and the limited warranty and restricted
#    rights notice below appear in all supporting documentation.
#    
#    AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS.
#    AUTODESK SPECIFICALLY DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR
#    FITNESS FOR A PARTICULAR USE. AUTODESK, INC. DOES NOT WARRANT THAT THE
#    OPERATION OF THE PROGRAM WILL BE UNINTERRUPTED OR ERROR FREE.

import adsk.core, adsk.fusion, traceback

# Global variable used to maintain a reference to all event handlers.
handlers = []

dim=.238125

def getInputs(inputs):
    try:
        selection = inputs.itemById('selectEnt').selection(0)
        face = selection.entity
        
        evalType = inputs.itemById('evalType').selectedItem.name
        
        density = int(inputs.itemById('number').value)
    
        return(evalType, face, density)
    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def add_pip(lines, ent, pip, sketchPoints):
    p0 = ent.geometry.getData()[1]

#    recLines = lines.addTwoPointRectangle(ent.geometry.getData()[1], ent.geometry.getData()[1])
    sketchPoint = sketchPoints.add(p0)
    
    # Move sketch point
    translation = adsk.core.Vector3D.create(dim*pip*2, 0, 0)
    sketchPoint.move(translation)



    x = sketchPoint.geometry.x
    y = sketchPoint.geometry.y
    z = sketchPoint.geometry.z
    p1 = adsk.core.Point3D.create(x + dim, y, z)
    lines.addByTwoPoints(sketchPoint.geometry, p1)
    p2 = adsk.core.Point3D.create(x + dim, y-dim, z)
    lines.addByTwoPoints(p1, p2)
    p3 = adsk.core.Point3D.create(x + dim*2, y-dim, z)
    lines.addByTwoPoints(p2, p3)
    p4 = adsk.core.Point3D.create(x + dim*2, y, z)
    lines.addByTwoPoints(p3, p4)


#    seg2 = lines.addByTwoPoints(ent.geometry.getData()[1], ent.geometry.getData()[1] + dim)
#    seg3 = lines.addByTwoPoints(ent.geometry.getData()[1], ent.geometry.getData()[1] + dim)
#    seg4 = lines.addByTwoPoints(ent.geometry.getData()[1], ent.geometry.getData()[1] + dim)

            
def draw(ent, num_pips):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)

    # Get the root component of the active design.
    rootComp = design.rootComponent

    # Create a new sketch on the xy plane.

    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    # Get sketch points
    sketchPoints = sketch.sketchPoints
    
    # Draw two connected lines.
    lines = sketch.sketchCurves.sketchLines;
    
    for x in range(num_pips):
        add_pip(lines, ent, x, sketchPoints)



# ExecutePreview event handler class.
class MyExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            # Get the current info from the dialog.
            inputs = cmdArgs.command.commandInputs
            (evalType, ent, num_pips) = getInputs(inputs)
                  
            draw(ent, num_pips)
            
            # Set this property indicating that the preview is a good
            # result and can be used as the final result when the command
            # is executed.
            cmdArgs.isValidResult = True
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Called when the command is executed.  However, because this command
# is using the ExecutePreview event and is setting the isValidResult property
# to true, the results created in the preview will be used as the final
# results and the Execute will not be called.
class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the current info from the dialog.
            inputs = args.command.commandInputs        
            (evalType, face, density) = getInputs(inputs)

            draw(face)
            
        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# CommandCreated event handler class.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = adsk.core.Command.cast(args.command)
            inputs = command.commandInputs

            # Create a selection input to get a selected entity from the user.            
            selectInput = inputs.addSelectionInput('selectEnt', 'Selection', 'Select an entity')
            
            selectInput.addSelectionFilter('SketchLines')

            selectInput.setSelectionLimits(1, 1)
            
            # Create a text box that will be used to display the results.
            textResult = inputs.addTextBoxCommandInput('textResult', '', '', 2, True)
            # Create a text box that will be used to display the results.
            varResult = inputs.addTextBoxCommandInput('varResult', '', '', 2, True)    
    
    
            # Add the selection input to get the points.
            typeInput = inputs.addDropDownCommandInput('evalType', 'Huristic', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            typeInput.listItems.add('Floor', True, '', -1)
            typeInput.listItems.add('Ceiling', True, '', -1)

            # Add the unitless value input to get the density.            
            densityInput = inputs.addValueInput('number', 'NumPips', '', adsk.core.ValueInput.createByString('10'))
            baseDimInput = inputs.addDistanceValueCommandInput('baseDim', 'baseDimInput', adsk.core.ValueInput.createByString('3in/32'))

    
            # Connect to the input changed event.
            onInputChanged = MyInputChangedHandler()
            command.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)
            
            
            # Connect to the execute preview and execute events.
            onExecutePreview = MyExecutePreviewHandler()
            command.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)
            
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# InputChanged event handler class.
class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:


           
            
            
            # Get the selection command input.
            cmdInput = adsk.core.CommandInput.cast(args.input)
            if cmdInput.id == 'selectEnt':
                selInput = adsk.core.SelectionCommandInput.cast(cmdInput)
                # Check that an entity is selected.
                if selInput.selectionCount > 0:
                    ent = selInput.selection(0).entity

                    # Create a string showing the proxy path.    
                    path = getPath(ent)
                    entType = ent.objectType
                    entType = entType.split(':')
                    entType = entType[len(entType)-1]
                    path += '/' + entType
                    
                    # Get the text box command input and display the path string in it.
                    textResult = cmdInput.parentCommand.commandInputs.itemById('textResult')
                    textResult.text = path
                    
                                       # Get the text box command input and display the path string in it.
                    varResult = cmdInput.parentCommand.commandInputs.itemById('varResult')
                    
                    # if It's a line then this is x, y of the first and second point.
                    varResult.text = "begin: (" + str(ent.geometry.getData()[1].x) + ", " + str(ent.geometry.getData()[1].y) + ")"
                    varResult.text += "  end: (" + str(ent.geometry.getData()[2].x) + ", " + str(ent.geometry.getData()[2].y) + ")"

                    
                    # If we were instpecting a point these are the x, y coords
#                    varResult.text = str(ent.geometry.getData()[1]) + ", " + str(ent.geometry.getData()[2])

        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


        
# Builds up the string showing the proxy path by stepping up the path from
# the proxy entity itself to each occurrence that defines its context.
def getPath(ent):
    path = ''
    if ent.assemblyContext:

        occ = ent.assemblyContext
        while occ:
            if path == '':
                path = occ.name
            else:
                path = occ.name + '/' + path

            occ = occ.assemblyContext
        
        path = 'Root/' + path
    else:
        path = 'Root'

    return path        
        
        
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Create a new command and connect to the command created event.
        buttonDef = ui.commandDefinitions.addButtonDefinition('ekinsKanekaPipifyPath', 'Kaneka Pipify', 'Create pips along vector.', 'Resources/KanekaPipify')
        onCommandCreated = MyCommandCreatedHandler()
        buttonDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # Add a control for the command into the SKETCH panel.
        inspectPanel = ui.allToolbarPanels.itemById('SketchPanel')
        inspectPanel.controls.addCommand(buttonDef)                
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Clean up all UI related to this command.
        buttonDef = ui.commandDefinitions.itemById('ekinsKanekaPipifyPath')
        if buttonDef:
            buttonDef.deleteMe()

        inspectPanel = ui.allToolbarPanels.itemById('InspectPanel')
        if inspectPanel.controls.itemById('ekinsKanekaPipifyPath'):
            inspectPanel.controls.itemById('ekinsKanekaPipifyPath').deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

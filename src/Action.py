'''
Action designates an event that changes the state of item (leads to the result of the action)
This class defines the action and turns it into HTML
'''

from ActionController import ActionController

class Action:

    #types pf the Action described by Drescher's microworld
    Type = {
        #a synthetic action
        'COMPOSITE': 'COMPOSITE',
        # list of possible primitive actions
        'NULL_ACTION' : 'NULL_ACTION',
        'MOVE_LEFT':'MOVE_LEFT', 'MOVE_RIGHT':'MOVE_RIGHT', 'MOVE_UP':'MOVE_UP', 'MOVE_DOWN':'MOVE_DOWN',
        'GAZE_LEFT': 'GAZE_LEFT', 'GAZE_RIGHT':'GAZE_RIGHT', 'GAZE_UP':'GAZE_UP', 'GAZE_DOWN':'GAZE_DOWN',
        'CENTER_GAZE':'CENTER_GAZE',
        'FOVEATE_NEXT_OBJECT_LEFT':'FOVEATE_NEXT_OBJECT_LEFT','FOVEATE_NEXT_OBJECT_RIGHT':'FOVEATE_NEXT_OBJECT_RIGHT','FOVEATE_NEXT_OBJECT_UP':'FOVEATE_NEXT_OBJECT_UP','FOVEATE_NEXT_OBJECT_DOWN':'FOVEATE_NEXT_OBJECT_DOWN', 
        'FOVEATE_NEXT_MOTION':'FOVEATE_NEXT_MOTION',
        'HAND1_LEFT':'HAND1_LEFT','HAND1_RIGHT':'HAND1_RIGHT', 'HAND1_UP':'HAND1_UP', 'HAND1_DOWN':'HAND1_DOWN',
        'HAND2_LEFT':'HAND2_LEFT', 'HAND2_RIGHT':'HAND2_RIGHT', 'HAND2_UP':'HAND2_UP', 'HAND2_DOWN':'HAND2_DOWN',
        'HAND1_FINE_LEFT':'HAND1_FINE_LEFT', 'HAND1_FINE_RIGHT':'HAND1_FINE_RIGHT', 'HAND1_FINE_UP':'HAND1_FINE_UP', 'HAND1_FINE_DOWN':'HAND1_FINE_DOWN',
        'HAND2_FINE_LEFT':'HAND2_FINE_LEFT', 'HAND2_FINE_RIGHT':'HAND2_FINE_RIGHT', 'HAND2_FINE_UP':'HAND2_FINE_UP', 'HAND2_FINE_DOWN':'HAND2_FINE_DOWN',
        'HAND1_GRASP':'HAND1_GRASP', 'HAND1_UNGRASP':'HAND1_UNGRASP',
        'HAND2_GRASP':'HAND2_GRASP', 'HAND2_UNGRASP':'HAND2_UNGRASP',
        'HAND1_WELD':'HAND1_WELD', 'HAND2_WELD':'HAND2_WELD',
	    'HAND1_UNWELD':'HAND1_UNWELD', 'HAND2_UNWELD':'HAND2_UNWELD',
	    'HAND1_HOME':'HAND1_HOME', 'HAND2_HOME':'HAND2_HOME'
    }
    

   

    def __init__(self, stage, name, index, type = Type.HAND1_GRASP):
        #when the schema is activated
        self.last_activated_at = -1000
        self.stage = stage
        self.index = index
        self.type = type
        self.controller = ActionController(self)
        #shemas that use this action
        self.schemas = []



    '''
    Function that activates the action
    '''
    #FIX STAGE
    def activate(self, val):
        if val:
            self.last_activated_at = self.stage.clock

    # 
    def __str__(self):
        print("Action ", self.index, ": ", self.name, " ", self.type )
        print("activated ", self.activated)
        print("Schemas containing this action: ")
        for schema in self.stage.schemas:
            if schema.action == self:
                print(schema.__str__())
            

   



   




    



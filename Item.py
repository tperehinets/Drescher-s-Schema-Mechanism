'''
Item is a state element. It represents the proposition about the world (On or Off). Context is a set of items. Result of the event is also 
represented by an item 
'''

class Item:
    ItemType = {
        'PRIMITIVE':'PRIMITIVE', 'SYNTHETIC':'SYNTHETIC', 'CONTEXT_CONJUNCTION':'CONTEXT_CONJUNCTION'
    }

    def __init__(self, stage, name, index, value, type = ItemType.PRIMITIVE):
        self.predicted_positive_transition = None
        self.predicted_negative_transition = None

        '''
        Section 4.1.2 pp 73. We need to indicate if these value transitions were 'explained'
        by a schema which was just activated and predicted they would occur.
        '''

        self.last_pos_transition =  -1000
        self.last_neg_transition =  -1000


        #Synthetic items may be in an unknown state 
        self.known_state = True
        self.prev_known_state = True

        self.stage = stage
        self.name = name
        self.index = index
        self.value = value
        self.type = type

    def set_known_state(self, v):
        self.known_state =v

    def set_value(self,v):
        self.value =v

    #ADD A FUCNCTION TO TURN INTO HTML and to string

   
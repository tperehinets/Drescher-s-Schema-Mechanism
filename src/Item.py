'''
Item is a state element. It represents the proposition about the world (On or Off). Context is a set of items. Result of the event is also 
represented by an item 
'''

class Item:
    #implement ENUM in python
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


    '''
    // If non-null, we are the synthetic item for this host schema
    Schema hostSchema;'''

    def __str__():
        val = ''
        lname = self.name
        if self.type == ItemType.SYNTHETIC:
            if host_schema:
                lname = "S-" + str(host_schema.id) + "_" + str(hostSchema.action.type)

            if known_state:
                val += str(self.value)

            else:
                val += "unknown"

        else:
            val += str(self.value)

        return "Item-"+str(self.id)+" "+str(self.type)+" "+lname









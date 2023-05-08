
'''
Implementing the Comparable class in Pyhton. This class compares the proximity of the schemas
'''
#implementing Comparable class in Python

class SchemaProximityValue:
    def __init__(self, schema, proximity=0):
        self.schema = schema
        self.proximity = proximity

    def compare_to(self, o):
        if self.proximity == o.proximity:
            return 0

        elif self.proximity - o.proximity:
            return -1

        else:
            return 1



class ActionController:
    def __init__(self, action):
        #need to make a list which can hold proximity values for each schema and be sorted by proximity
        self.schemas = []
        #the action that it controls
        self.action = action

    def sort_schemas(self):
        self.schemas.sort()

    def compute_proximities(self):
        pass
        '''
        See Sec 3.3 of Made-Up Minds for implementation of action controller
        We need to compute, for each schema, what it's proximity to our action's goal state is.
        This is the inverse of the time expected to reach the goal state, derived from the activation times
        of the schemas in the chain. Also factored in are a value proportional reliability of the schema and inverse of it's cost. 
        '''

    def __str__(self):
        return ("[ActionController ", self.action, " ]")




'''
The "Stage" holds the schemas and related items, and a pointer to a
sensorimotor system which is hooked to a microworld simulator.
'''

class B:
    def __init__(self, a):
        self.my_val = 259
        self.my_string =  "Two hundred fifty nine"
        self.a = a

    def __str__(self):
        return "[B my_val="+self.my_val+" my_string ="+my_string+" a.id="+self.a.id+"]"




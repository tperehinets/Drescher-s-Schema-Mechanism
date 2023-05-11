#Context is a set of items. When a bare schema it created, it's created for every action with empty context
import logging
from Bitset import Biteset
import defaultdict

#to implement Fisher's test
import scipy.stats as stats


#Holds the extended context or result array
class ExtendedResult:
    logger = logging.getLogger(__name__)
    ignore_items_pos = Bitset()
    ignore_items_neg = Bitset()

    P_THRESHOLD = 0.2 #20% significance for Fisher exact test

    #implementing TDoubleArrayList()

    pos_transition_action_taken = defaultdict(double)
    pos_transition_action_not_taken = defaultdict(double)

    neg_transition_action_taken = defaultdict(double)
    neg_transition_action_not_taken = defaultdict(double)

    num_trials_action_taken = 0
    num_trials_action_not_taken = 0

    #need to figure out if these are important
    # remained_on_action_taken = defaultdict(double)
    # remained_on_action_not_taken = defaultdict(double)

    # remained_off_action_taken = defaultdict(double)
    # remained_off_action_not_taken = defaultdict(double)

    '''
    Made Up Minds Section 4.1.2  pp. 73
    
    @param actionTime the most recent time the action was taken
    Update transition statistics with respect to whether the our schema's action was taken or not.
    '''

    def update_result_item(stage, shema, item, action_taken, action_time):
        id = item.id

        #Was there a transition since the action was taken?
        pos_transition = item.last_pos_transition >= action_time
        neg_transition = item.last_neg_transition >= action_time

        known_state = item.known_state

        if pos_transition and ignore_items_pos[id]:
            #ignore
            pass

        elif neg_transition and ignore_items_neg[id]:
            pass #ignore

        else:
            #read out the existing statistics on the probablity of result transition with/without the action
            positive_transitions_a = int(pos_transition_action_taken[id] * stage.x_result_recency_bias)
            positive_transitions_na = int(pos_transition_action_not_taken[id]  * stage.x_result_recency_bias)

            negative_transitions_a = int(neg_transition_action_taken[id]  * stage.x_result_recency_bias)
            negative_transitions_na = int(neg_transition_action_not_taken[id]  * stage.x_result_recency_bias)

            #Update the item state transition counters 

            '''
            A synthetic item may be in an unknown state, in which case we do not want
            to update stats on it. 
            '''

            if known_state:
                if pos_transition and not item.predicted_positive_transition: # 0->1 transition
                    if action_taken:
                        positive_transitions_a+=1
                        logger.debug("POS-transition-AT {} {} {}".format(item, schema, positive_transitions_a))
                        pos_transition_action_taken.set[id] = positive_transitions_a

                    else:
                        positive_transitions_na+=1
                        logger.debug("POS-transition-NAT {} {} {}".format(item, schema, positive_transitions_na))
                        pos_transition_action_not_taken.set[id] = positive_transitions_na
               
                elif neg_transition and not item.predicted_negative_transition: # 1->0 transition
                    if action_taken:
                        negative_transitions_a+=1
                        logger.debug("NEG-transition-AT {} {} {}".format(item, schema, negative_transitions_a))
                        neg_transition_action_taken.set[id] = negative_transitions_a
                    else:
                        negative_transitions_na+=1
                        logger.debug("NEG-transition-NAT {} {} {}".format(item, schema, negative_transitions_na))
                        negTransitionActionNotTaken.set[id] = negative_transitions_na
                    

            '''
            TODO [hqm 2014-03] implement this optimization
            Section 4.1.2
            "The machinery's sensitivity to relevant results is amplified by an embellishment
            of marginal attribution: when a given schema is idle (i.e., it has not just completed
            an activation), the updating of its extended result data is suppressed for any
            state transition which is explained--meaning that the transition is predicted as the
            result of a reliable schema whose activation has just completed. Consequently, a
            given schema whose activation is a less frequent cause of some result needn't
            compete with other, more frequent causes, once those causes have been identified;
            in order for the result to be deemed relevant to the given schema, that schema need
            only bring about the result more often than the result's other unexplained occurrences."
            '''

            '''
            per GLD: "My implementation used an ad hoc method that was tied to its
            space-limited statistics collection method. But the real way to do it
            is to use a threshold of statistical significance. So just pre-compute
            a lookup table that says what the minimum correlation is that can be
            supported by a given sample size."

            '''

            pPos = compute_pos_probabilities(int(positive_transitions_na), int(positive_transitions_a),
                                                  num_trials_action_taken, num_trials_action_not_taken)

            pNeg = compute_neg_probabilities(int(negative_transitions_na), int(negative_transitions_a),
                                                  num_trials_action_taken, num_trials_action_not_taken)

            if positive_transitions_a > stage.result_spinoff_min_trials:
                if pPos < P_THRESHOLD:
                    schema.result_spinoff_min_trials(item, true, pPos, num_trials_action_taken)

                          
            if negative_transitions_a > stage.result_spinoff_min_trials:
                if pNeg < P_THRESHOLD:
                    schema.result_spinoff_min_trials(item, false, pNeg, num_trials_action_taken)

            '''
                       no-action  action
            transition     n11          n21
            no-transition  n12          n22  


                              (placebo)
                            ACTION NOT TAKEN                          ACTION TAKEN

            POS TRANSITION    pos_transitions_na                          pos_transitions_a

            NO-TRANSITION     (num_trials_action_not_taken-pos_transitions_na)  (num_trials_action_taken -pos_transitions_a)
            '''

    def compute_probabilities(positive_transitions_na, positive_transitions_a, num_trials_action_taken, num_trials_action_not_taken):
        p11 = int(positive_transitions_na)
        p21 = int(num_trials_action_not_taken - positive_transitions_na)
        p12 = int(positive_transitions_a)
        p22 = int(num_trials_action_taken - positive_transitions_a)

       
        pPos = stats.fisher_exact([p11, p12], [p21, p22])[0]
        return pPos

    def compute_neg_probabilities(negative_transitions_na, negative_transitions_a, num_trials_action_taken, num_trials_action_not_taken):
        n11 = int(negative_transitions_na)
        n21 = int(num_trials_action_not_taken - negative_transitions_na)
        n12 = int(negative_transitions_a)
        n22 = int(num_trials_action_taken - negative_transitions_a)

        pNeg = FishersExactTest.fishersExactTest([n11, n12], [n21, n22])[0]
        return pNeg

    def reset_counters():
        neg_transition_action_not_taken = [0] * len(neg_transition_action_not_taken)
        neg_transition_action_taken = [0] * len(neg_transition_action_taken)
        pos_transition_action_not_taken = [0] * len(pos_transition_action_not_taken)
        pos_transition_action_taken = [0] * len(pos_transition_action_taken)
    

    #implement toHTML function

    def clear_negative_items(item_id):
        neg_transition_action_not_taken[item_id] = 0
        neg_transition_action_taken[item_id] = 0

    def creal_positive_items(item_id):
        pos_transition_action_not_taken[item_id] = 0
        pos_transition_action_taken[item_id] = 0



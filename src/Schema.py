import logging
from Stage import Stage
from Action import Action
from ExtendedContext import ExtendedContext
from ExtendedResult import ExtendedResult

class Schema:
    #__name__ = Shema.class
    #think how to implement this
    logger = logging.getLogger((__name__))

   

    def __init__(self, stage, action, index=0):
        self.stage = stage
        self.action = action

        #action.schemas.add(this);

        #Numerical id of this schema
        self.id = index

        self.creation_time = stage.clock()

        #newly creates schema with empty context and result
        self.bare = True

        #The items in this schema's context list (HashSet)
        self.pos_context = {}
        self.neg_context = {}

        #The items in this schema's result list (HashSet)
        self.pos_result = {}
        self.neg_result = {}

        # The synthetic item which is controlled by this schema's successful activation.
        # Also known as the 'reifier' item
        #F.e. if we know that OpenDoor will work only if the door is not locke, we need a verifier for that

        self.synthetic_item = None

        #Was this action taken recently (within the last time window) (False by default)
        self.action_taken = False

        '''
        When our extended context has more than one item in it, we make a 'conjunct' item for it
        that can be included as a result in a new schema by marginal attribution.
        '''
        self.conjunct_item = None

        self.succeeded = False
        self.applicable = False

        #reliability statistics

        '''How many times did this schema achieve it's predicted result when activated?'''
        self.succeeded_with_activation   = 0

        '''How many times did this schema achieve it's predicted result when not activated?'''
        self.succeeded_without_activation = 0

        ''' How many times did this schema fail to achieve it's predicted results when activated?'''
        self.failed_with_activation = 0 #number of times activation failed

        '''How many times was this schema activated? '''
        self.activations = 0

        #Parent schema from which we were spun off
        self.parent = None

        #List of child schemas which we have spun off
        self.children = []
        self.value = 0

        #See pp. 55
        #correlation, reliability, duration, cost
        ''' How long this schema typically remains applicable. Used to maintain the default on time of the synthetic item. '''
        self.duration = 30
        self.cost = 0
        self.last_time_activated = -1000
        self.last_time_succeeded = -1000
        self.creation_time = 0

        #Extended Context Counters
        self.xcontext = ExtendedContext()

        #Extended Result Counters
        xresult = ExtendedResult()

        #List of schemas who override this schema;
        #defer to these more specific schemas when they are also applicable (implementing TIntArrayList)
        XOverride = defaultdict(int)

        self.action = None
        self.stage = None


    def correlation(self):
        ''' ratio of the probability that a transition to the result state happens
        when our action is taken, to the probability that the result state happens
        when our context is satisfied but the action is not taken (i.e., we are applicable but not activated)
        '''

        return self.succeeded_with_activation / self.succeeded_without_activation

    def make_synthetic_item(self):
        self.synthetic_item = self.stage.make_synthetic_item(self)
        self.synthetic_item.set_known_state(False)

    def clear_predicted_transitions(self):
        if self.pos_result:
            self.pos_result.predicted_positive_transition = None
        if self.neg_result:
            self.neg_result.predicted_negative_transition = None

    #Perform designated action
    def activate(self):
        logger.info("Activated schema: ", self)
        self.activations +=1
        self.action.activate(True)
        self.action_taken = True
        self.last_time_activated = stage.clock

    #Schema's action was taken, and it's predicted results set was satisfied
    def handle_successful_activation(self):
        if self.synthetic_item:
            self.synthetic_item.set_value(True)

        self.last_time_succeeded = stage.clock

        ''' Section 4.1.2 pp 73
           We need to 'publish' our 'prediction' of items that we assert will transition
           due to our activation.

           This is so that the marginal attribution algorithm can
           allow idle schemas to not have to tally up "explained" transitions in their
           extended results "action not taken" counters. The schema need only bring about the
           result item transition more often than the results other "unexplained" occurences.

         '''

        if self.pos_result:
            self.pos_result.predicted_positive_transition = self

        if self.neg_result:
            self.neg_result.predicted_negative_transition = self

    def update_results_counters(self, last_activity_time):
        #Run the marginal attribution heuristics to decide whether to spin off 
        # a new schema with new results

        if self.action_taken:
            xresult.num_trials_action_taken +=1

        else:
            self.xresult.num_trials_action_not_taken+=1

        nitems = len(stage.items)
        items = stage.items

        for i in range(nitems):
            if items[i]:
                xresult.update_result_item(stage, self, items.get(i), self.action_taken, last_activity_time)

    #Checks if the context is satisfied. 
    def update_applicable_flag(self):
        self.applicable = True

        for item in self.pos_context:
            if not item.known_state:
                self.applicable = False
            else:
                self.applicable = self.applicable and item.value

        for item in neg_context:
            if not item.known_state:
                self.applicable = False
            else:
                self.applicable = self.applicable and item.value
    
    '''
    Assumes 'applicable' has already been calculated. If 'applicable == true' it means the
    context must be satisfied, i.e., the conjunction of items in the context must be true.
    There is a 'conjunctItem' that we maintain, and we need to update it's pos and neg transition info.
    We do that here, by computing if its prior value differs from the current value.
    '''

    def update_conjunct_item(self):
         #Update the conjunct-item value transitions, if there is one, which is tracking our context's value
        #If 'applicable' is true, that means the value of the context must be true. I'll refer to this as 'newval'

        new_val = self.applicable
        old_val = self.conjunct_item.value

        if not old_val and new_val:
            #conjunction item made a Postitive Transition: new lastPosTransition is max transition time of any of the context items
            for item in self.pos_context:
                self.conjunct_item.last_pos_transition = max(self.conjunct_item.last_pos_transition, item.last_pos_transition)

            for item in self.neg_context:
                self.conjunct_item.last_pos_transition = max(self.conjunct_item.last_pos_transition, item.last_pos_transition)

            logger.info("updateConjunctItem POS {} lastPosTransition = {}, clock={} delta={}".
            format(self.conjunct_item, self.conjunct_item.last_pos_transition, stage.clock, stage.clock-self.conjunct_item.last_pos_transition))

        elif  old_val and not new_val:
            #conjunct item made a Negative Transition time: new lastNegTransition is max transition time of any of the context items
            for item in self.pos_context:
                self.conjunct_item = max(self.conjunct_item.last_neg_transition, item.last_pos_transition)
            for item in self.neg_context:
                self.conjunct_item.last_neg_transition = max(self.conjunct_item.last_neg_transition, item.last_neg_transition)

            logger.info("updateConjunctItem NEG %s lastNegTransition = %d, clock=%d delta=%d".
            format(self.conjunct_item, self.conjunct_item.last_neg_transition, stage.clock, stage.clock-self.conjunct_item.last_neg_transition))

        self.conjunct_item.value = new_val
        self.conjunct_item.prev_value = old_val

    


'''
public class Schema {


    /**
     * Update our statistics on success and failure
     *
     // if schema's context satisfied, and action taken, it is considered 'activated'
     // special case, if context is empty, then just taking action considered activated.

     * 
     */
    public void handleActivation() {
        // Absent evidence to the contrary, we deactivate this schema after it's duration has expired
        if (stage.clock > (lastTimeActivated + duration)) {
            if (syntheticItem != null) {
                syntheticItem.setValue(false);
                syntheticItem.setKnownState(false);
                logger.info("handleActivation "+this+" timed out synthetic item "+syntheticItem);
            }
        }

        // schemas succeeded if context was satisfied, action taken, and results obtained

        // If we have empty results list, then we only update results stats, and look for
        // potential spinoff condition (prob. that some item transitions more with action than without)


        if (applicable) {

            succeeded = true;
            if (posResult != null) {
                if (!posResult.knownState) {
                    succeeded = false;
                } else {
                    succeeded &= posResult.value;
                }
            }
            if (negResult != null) {
                if (!negResult.knownState) {
                    succeeded = false;
                } else {
                    succeeded &= !negResult.value;
                }
            }





            /* See 4.1.3 Suppressing redundant attribution, to avoid exponential spinoffs.
               We check our lists of  "ignoreItems", to see if any item listed there has the specified value,
               and if so we do not do marginal attribution. Some child schema that we spun off
               will do the marginal attribution.
            */

            ArrayList<Item> items = stage.items;
            boolean updateExtendedContext = true;
            int nitems = items.size();
            for (int id = 0; id < nitems; id++) {
                Item item = items.get(id);
                if (item != null && item.prevKnownState) {
                    boolean val = item.prevValue;
                    // Section 4.1.3 supressing redundant attribution 
                    if ( (val && xcontext.ignoreItemsOn.get(item.id)) ||
                         (!val && xcontext.ignoreItemsOff.get(item.id)) ) {
                        updateExtendedContext = false;
                        break;
                    }
                }
            }

            if (updateExtendedContext) {
                xcontext.updateContextItems(stage, this, succeeded, lastTimeActivated);
            }

            logger.info("handleActivation "+this+" applicable=true, succeeded="+succeeded);


            // Did we just perform our specified action, within the valid time window?
            // NEED TO ALSO BE APPLICABLE???
            if (actionTaken && succeeded) {
                // TODO [hqm 2013-07] Need to bias this statistic towards more recent activations
                succeededWithActivation++;
                handleSuccessfulActivation();
            }

            if (actionTaken && !succeeded) {
                // TODO [hqm 2013-07] Need to bias this statistic towards more recent activations
                failedWithActivation++;
                if (syntheticItem != null) { syntheticItem.setValue(false); }
            }

            // TODO [hqm 2013-08] ?? What should we do with synthetic item in this case?
            // TODO case currently will never happen because handleActivation is only called when actionTaken=true
            // Do we need to call handleActivation on all schemas whenever any action is taken?? 
            if (!actionTaken && succeeded ) {
                succeededWithoutActivation++;
            }

        } else {
            logger.info("handleActivation "+this+" applicable=false");
        }

        // Set this back to false so we don't trip on it in some later step when we're activated
        // but not applicable
        succeeded = false;

    }

    // We use these to do a fast lookup to see if we ever spun off a schema with this result item before
    public HashSet<Item> posResultItemSpinoffs = new HashSet<Item>();
    public HashSet<Item> negResultItemSpinoffs = new HashSet<Item>();

    /*  Create a new spinoff schema, adding this item to the positive (or negative) result set

        We want to be careful not to spin off a result item that is our own synthetic item.
     */
    public void spinoffWithNewResultItem(Item item, boolean sense, double prob, int ntrials) {
        // check if this item is already in the result of a child schema
        if ((sense && posResultItemSpinoffs.contains(item)) ||
            (!sense && negResultItemSpinoffs.contains(item))) {
            return;
        }

        if (sense) {
            xresult.ignoreItemsPos.set(item.id);
            posResultItemSpinoffs.add(item);
        } else {
            xresult.ignoreItemsNeg.set(item.id);
            negResultItemSpinoffs.add(item);
        }


        // print out the extended result table for logging purposes
        logger.info("SPINNING OFF RESULT SCHEMA from "+this+" for "+item+", sense="+sense);
        logger.info(this.toHTML());
        if (sense) {
            logger.info(String.format("Spinning off positive-transition result %s %s pos-transition-correlation=%f #trials=%s", item, this, prob, ntrials));
        } else {
            logger.info(String.format("Spinning off neg-transition result %s %s neg-transition-correlation=%f #trials=%s", item, this, prob, ntrials));
        }


        Schema schema = spinoffNewSchema();
        schema.bare = false;
        children.add(schema);
        if (sense) {
            schema.posResult = item;
        } else {
            schema.negResult = item;
        }

        // break point in simulation to allow me to examine state
        //        stage.sms.multiStep = true;
        //        stage.sms.run = false;

    }

    public void spinoffWithNewContextItem(Item item, boolean sense) {
        // Don't spinoff a new schema with this item in it's context if we've already spun one off that has this item
        if (sense && xcontext.ignoreItemsOn.get(item.id)) {
            logger.info("ignoreItemsOn set in %s for %s, suppressing spinoff");
            return;
        } else if (!sense && xcontext.ignoreItemsOff.get(item.id)) {
            logger.info("ignoreItemsOff set in %s for %s, suppressing spinoff");
            return;
        }


        if (!sense) {
            logger.info("****SPINOFF NEG ITEM "+item+", for schema "+this);
        }

        logger.info("spinoffWithNewContextItem: "+this+ "sense="+sense+ ":= "+xcontext.describeContextItem(item));
        logger.info(this.toHTML());

        if (sense == true) { // positive value
            xcontext.ignoreItemsOn.set(item.id);
        } else {
            xcontext.ignoreItemsOff.set(item.id);
        }
        Schema child = spinoffNewSchema();

        // Section 4.1.3 supressing redundant attribution
        xcontext.clearAllCounters();

        child.bare = false;
        children.add(child);
        if (sense) {
            child.posContext.add(item);
            logger.info("clearOnItems "+child+" item "+item);
        } else {
            child.negContext.add(item);
            logger.info("clearOffItems "+child+" item "+item);
        }

        // If more than one item in the context, create a pseudo-item for the conjunction of the items,
        // so that schemas can consider using it as the result for a new spin-off schema.
        /*
        if ((child.posContext.size() + child.negContext.size()) > 1) {
            // Create a new conjunct item for our context items. This will be
            // a candidate for inclusion in result of a new schema.
            int nitems = stage.items.size();
            String name = String.format("%s-%s-~%s", Integer.toString(nitems), child.posContext, child.negContext);
            Item citem = new Item(stage, name, nitems, false, Item.ItemType.CONTEXT_CONJUNCTION);
            child.conjunctItem = citem;
            stage.items.add(citem);
            stage.conjunctItems.add(citem);
            stage.ensureXCRcapacities();
        }
        */
    }

    /**
       copies the context, action, and result lists
     */
    Schema spinoffNewSchema() {
        Schema child = new Schema(stage, stage.schemas.size(), action);
        child.parent = this;
        // Copy the context and result into the new child schema
        child.posContext.addAll(posContext);
        child.negContext.addAll(negContext);
        child.posResult = posResult;
        child.negResult = negResult;

        // TODO verify if we need to do this or something like it
        //child.xcontext.ignoreItems.or(xcontext.ignoreItems);

        if (stage.enableSyntheticItems) {
            child.makeSyntheticItem();
            // ignore child's synthetic item
            xresult.ignoreItemsPos.set(child.syntheticItem.id);
            xresult.ignoreItemsNeg.set(child.syntheticItem.id);
            child.xresult.ignoreItemsPos.or(xresult.ignoreItemsPos);
            child.xresult.ignoreItemsNeg.or(xresult.ignoreItemsNeg);
        }

        stage.schemas.add(child);
        stage.ensureXCRcapacities();
        
        logger.debug("spun off new schema "+child);
        return child;
    }

    // Initialize this schema, for this stage
    public void initialize() {
        // create extended context, result arrays
    }

    public String toString() {
        return String.format("[Schema %d %s:~%s/%s/%s:~%s]",id, posContext, negContext, action, posResult, negResult);
    }

   
'''
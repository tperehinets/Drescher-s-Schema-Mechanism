#Context is a set of items. When a bare schema it created, it's created for every action with empty context
import logging
from Bitset import Biteset
import defaultdict

#to implement Fisher's test
import scipy.stats as stats
  

#Holds the extended context or result arrays
class ExtendedContext:
    #in java version the name is ExtendedContext.class --> need to figure out
    logger = logging.getLogger(__name__)

    '''Ignore these items when doing marginal attribution'''
    ignore_items_on = Bitset()
    ignore_items_off = Bitset()

    '''Use python arrays instead of TIntArrayList'''
    on_when_action_succeeds = defaultdict(int)
    on_when_action_fails = defaultdict(int)
    off_when_action_succeeds = defaultdict(int)
    off_when_action_fails = defaultdict(int)


    P_THRESHOLD = 0.10 #10% significance for Fisher exact test

    '''
    Made Up Minds Section 4.1.2  
   

    @param the schema was activated 
    @params whether the action succeeded or failed on last activation
    take statistics on which items were on/off right before the action was initiated
    Update transition statistics with respect to whether the our schema's action was taken or not.
    '''

    def update_context_items(stage: Stage, schema: Schema, succeeded: bool, action_time:long):
        items = stage.items

        logger.info("*********************")
        logger.info("updateContextItems Schema {schema} succeeded={succ}".format(schema = schema, succ = succeeded))

        items = len(items)

        '''Map over all items, tabulating their state vs schema's success/failure'''
        for id in range(len(items)):
            item = items[id]
            if items[0] and items[0].type != Item.ItemType.CONTEXT_CONJUNCTION and ((not items[0] in schema.posContext or items[0] in schema.negContext)):
                on_succeeded = on_when_action_succeeds[id]
                on_failed = on_when+action_fails[id]

                off_succeeded = off_when_action_succeeds[id]
                off_failed = off_when_action_fails[id]

                logger.info("   {item} pval={prevValue} pknownstate={prevKnownState}".format(item = item, prevValue = item.prevValue, prevKnownState = item.prevKnownState))
       
                if item.prevKnownState:
                    if item.prevValue:
                        if succeeded:
                            on_succeeded += 1
                            onWhenActionSucceeds.set[id] = on_succeeded
                            logger.info("increment onWhenActionSucceeds "+item+" "+on_succeeded)
                        else:
                            on_failed += 1
                            on_when_action_fails[id] = on_failed
                            logger.info("increment onWhenActionfails "+item+" "+on_failed)
            else:   #item prev value was off
                if succeeded:
                    off_succeeded += 1
                    off_when_action_succeeds[id] = off_succeeded
                    logger.info("increment offWhenActionSucceeds "+item+" "+off_succeeded)
                else:
                    off_failed += 1
                    off_when_action_fails[id] = off_failed
                    logger.info("increment offWhenActionFails "+item+" "+off_failed)

                    '''
                                ITEM WAS ON           ITEM WAS OFF
                    SUCCEED     n11                   n21
                    FAILED      n12                   n22


                           ITEM WAS ON           ITEM WAS OFF
                    SUCCEED     on_succeeded          off_succeeded
                    FAILED      on_failed             off_failed
                    '''

                '''Implementing the Fishers Exact Test with the data of success and failures'''
                #mkae sure if it works
                data = [[on_succeeded, off_succeeded], [on_failed, off_failed]]
                 
                odd_ratio, p_value = stats.fisher_exact(data)

                '''
                double fresult[] = FishersExactTest.fishersExactTest(on_succeeded, on_failed, off_succeeded, off_failed);
                double pPos = fresult[2];
                double pNeg = fresult[1];

                In Henry's version
                '''

                p_success_x_on = 0
                p_success_x_off = 0

                if on_failed + on_succeeded>0:
                    p_success_x_on = on_succeeded/(on_succeeded + on_failed)

                if off_succeeded + off_failed > 0:
                    p_success_x_off = off_succeeded / (off_succeeded + off_failed)

                if schema.id ==1 and (id ==0 or id ==6):
                    logger.info("DEBUG schema 1, item 0|6 item {} pPos={}, pNeg={}, PsuccOn={} pSuccOff={}, on_succeeded {}, off_succeeded {}, on_failed {}, off_failed {}"
                    .format(item, pPos, pNeg, pSuccessXOn, pSuccessXOff,  on_succeeded, off_succeeded, on_failed, off_failed))

                if schema.activations >= stage.context_spinoff_min_trials:
                    '''
                    TODO need to adjust this for number of trials; as number of trials increases
                    we should lower the threshold. Need a statistics expert to say what the formula is.
                    '''
                    if pPos < P_THRESHOLD:
                        logger.info("spinning-off ON CONTEXT item ", item, " ", schema)
                        logger.info("item {item} pPos={pPos}, pNeg={pNeg}, PsuccOn={pSuccessXOn} pSuccOff={pSuccessXOff}, on_succeeded {on_succeeded}, off_succeeded {off_succeeded}, on_failed {on_failed}, off_failed {off_failed}, activations: {schema.activations}"
                        .format(item, pPos, pNeg, pSuccessXOn, pSuccessXOff,  on_succeeded, off_succeeded, on_failed, off_failed, schema.activations))
                        schema.spinoff_with_new_context_item(item, True)

                    elif pNeg <P_THRESHOLD:
                        logger.info("spinning-off OFF CONTEXT item ", item, " ",schema)
                        logger.info("item {item} pPos={pPos}, pNeg={pNeg}, PsuccOn={pSuccessXOn} pSuccOff={pSuccessXOff}, on_succeeded {on_succeeded}, off_succeeded {off_succeeded}, on_failed {on_failed}, off_failed {off_failed}, activations: {schema.activations}"
                        .format(item, pPos, pNeg, pSuccessXOn, pSuccessXOff,  on_succeeded, off_succeeded, on_failed, off_failed, schema.activations))
                        
                        schema.spinoff_with_new_context_item(item, False)

    def clear_counter_for_item(item_number):
        off_when_action_fails[item_number] = 0
        off_when_action_succeeds[item_number] = 0
        off_when_action_succeeds[item_number] = 0
        on_when_action_fails[item_number] = 0

    def clear_all_counters():
        off_when_action_fails = [0] * len(off_when_action_fails)
        off_when_action_succeeds = [0] * len(off_when_action_succeeds)
        on_when_action_succeeds = [0] * len(on_when_action_succeeds)
        on_when_action_fails = [0] * len(on_when_action_fails)

    #implement an to_HTML() function

    def describe_context_item_bar_graph(item, max_val):
        n = item.id
        reliability_when_on = on_when_action_succeeds[n] /  (on_when_action_fails[n] + on_when_action_succeeds[n])
        reliability_when_off = off_when_action_succeeds[n] / (off_when_action_fails[n] + off_when_action_succeeds[n]); 

        #return an HTML code
        # return ("<span class=ecxtext>{} {} </span> <td>On {}<td><span class=\"chart1\" style=\"width: {}px;\">{}</span><td><span class=\"chart2\" style=\"width: {}px;\">{}</span>"+
        #                     "<td><span class=ecxtext>Off %.2f</span><td><span class=\"chart1\" style=\"width: %dpx;\">%d</span><td><span class=\"chart2\" style=\"width: %dpx;\">%d</span><td><span class=ecxtext> 1/0 %f<td> 0/1 %f <b>%s</b> <b>%s</b></span>"
        #                     .format(
        #                     n, item.makeLink(),
        #                     reliabilityWhenOn,
        #                     Math.max(10, onWhenActionSucceeds.get(n)*4), onWhenActionSucceeds.get(n),
        #                     Math.max(10, onWhenActionFails.get(n)*4), onWhenActionFails.get(n),
        #                     reliabilityWhenOff,
        #                     Math.max(10, offWhenActionSucceeds.get(n)*4), offWhenActionSucceeds.get(n),
        #                     Math.max(10, offWhenActionFails.get(n)*4), offWhenActionFails.get(n),
        #                     reliabilityWhenOn / reliabilityWhenOff,
        #                     reliabilityWhenOff / reliabilityWhenOn,
        #                     ignoreItemsOn.get(n) ? "IGNORE ON" : "",
        #                     ignoreItemsOff.get(n) ? "IGNORE OFF" : ""
        #                     ))


        #implement the other toHTML functions

    


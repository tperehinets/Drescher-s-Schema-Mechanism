'''
package com.beartronics.jschema;

import gnu.trove.list.TIntList;
import gnu.trove.list.array.TIntArrayList;
import gnu.trove.list.TDoubleList;
import gnu.trove.list.array.TDoubleArrayList;

import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.BitSet;
import java.io.*;

import edu.northwestern.at.utils.math.statistics.FishersExactTest;

import org.apache.log4j.Logger;

// Holds the extended context or result arrays
public class ExtendedResult {

    static Logger logger = Logger.getLogger(ExtendedResult.class);

    /* Ignore these items when doing marginal attribution */
    public BitSet ignoreItemsPos = new BitSet();
    public BitSet ignoreItemsNeg = new BitSet();

    static double P_THRESHOLD = (double) 0.20; //  20% significance for Fisher exact test

    TDoubleArrayList posTransitionActionTaken = new TDoubleArrayList();
    TDoubleArrayList posTransitionActionNotTaken = new TDoubleArrayList();

    TDoubleArrayList negTransitionActionTaken = new TDoubleArrayList();
    TDoubleArrayList negTransitionActionNotTaken = new TDoubleArrayList();

    public int numTrialsActionTaken = 0;
    public int numTrialsActionNotTaken = 0;

    /* need to figure out if these are important
    TDoubleArrayList remainedOnActionTaken = new TDoubleArrayList();
    TDoubleArrayList remainedOnActionNotTaken = new TDoubleArrayList();

    TDoubleArrayList remainedOffActionTaken = new TDoubleArrayList();
    TDoubleArrayList remainedOffActionNotTaken = new TDoubleArrayList();
    */

    /**
     * Made Up Minds Section 4.1.2  pp. 73
     *
     * @param actionTime the most recent time the action was taken
     * Update transition statistics with respect to whether the our schema's action was taken or not.
     */
    void updateResultItem(Stage stage, Schema schema, Item item, boolean actionTaken, long actionTime) {
        int id = item.id;

        // Was there a transition since the action was taken?
        boolean posTransition = item.lastPosTransition >= actionTime;
        boolean negTransition = item.lastNegTransition >= actionTime;
        
        boolean knownState = item.knownState;

        if (posTransition && ignoreItemsPos.get(id)) {
            // ignore
        } else if (negTransition && ignoreItemsNeg.get(id)) {
            // ignore
        } else {

            // read out the existing statistics on the probablity of result transition with/without the action
            
            int positiveTransitionsA = (int) (posTransitionActionTaken.get(id) * stage.xresultRecencyBias);
            int positiveTransitionsNA = (int) (posTransitionActionNotTaken.get(id)  * stage.xresultRecencyBias);

            int negativeTransitionsA = (int) (negTransitionActionTaken.get(id)  * stage.xresultRecencyBias);
            int negativeTransitionsNA = (int) (negTransitionActionNotTaken.get(id)  * stage.xresultRecencyBias);

            // Update the item state transition counters 

            // A synthetic item may be in an unknown state, in which case we do not want
            // to update stats on it. 
            if (knownState) {
                if (posTransition && item.predictedPositiveTransition == null) { // 0->1 transition
                    if (actionTaken) {
                        positiveTransitionsA++;
                        logger.debug(String.format("POS-transition-AT %s %s %d", item, schema, positiveTransitionsA));
                        posTransitionActionTaken.set(id,  positiveTransitionsA);
                    } else {
                        positiveTransitionsNA++;
                        logger.debug(String.format("POS-transition-NAT %s %s %d", item, schema, positiveTransitionsNA));
                        posTransitionActionNotTaken.set(id, positiveTransitionsNA);
                    }
                } else if (negTransition && item.predictedNegativeTransition == null) { // 1->0 transition
                    if (actionTaken) {
                        negativeTransitionsA++;
                        logger.debug(String.format("NEG-transition-AT %s %s %d", item, schema, negativeTransitionsA));
                        negTransitionActionTaken.set(id, negativeTransitionsA);
                    } else {
                        negativeTransitionsNA++;
                        logger.debug(String.format("NEG-transition-NAT %s %s %d", item, schema, negativeTransitionsNA));
                        negTransitionActionNotTaken.set(id, negativeTransitionsNA);
                    }
                }
                /* code for taking stats on items which remain in their state, with no transition

                   } else if (val && prevValue) {
                   if (actionTaken) {
                   remainedOnActionTaken.set(n, remainedOnActionTaken.get(n) + 1);
                   } else {
                   remainedOnActionNotTaken.set(n, remainedOnActionNotTaken.get(n) + 1);
                   }
                   } else if (val && prevValue) {
                   if (actionTaken) {
                   remainedOnActionTaken.set(n, remainedOnActionTaken.get(n) + 1);
                   } else {
                   remainedOnActionNotTaken.set(n, remainedOnActionNotTaken.get(n) + 1);
                   }
                   }
                */
            }
            /* TODO [hqm 2014-03] implement this optimization
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
            */



            /** per GLD: "My implementation used an ad hoc method that was tied to its
                space-limited statistics collection method. But the real way to do it
                is to use a threshold of statistical significance. So just pre-compute
                a lookup table that says what the minimum correlation is that can be
                supported by a given sample size."
            */
            double pPos = computePosProbabilities((int) positiveTransitionsNA, (int) positiveTransitionsA,
                                                  numTrialsActionTaken, numTrialsActionNotTaken);

            double pNeg = computeNegProbabilities((int) negativeTransitionsNA, (int) negativeTransitionsA,
                                                  numTrialsActionTaken, numTrialsActionNotTaken);

            if (positiveTransitionsA > stage.resultSpinoffMinTrials) {
                if (pPos < P_THRESHOLD) {
                    schema.spinoffWithNewResultItem(item, true, pPos, numTrialsActionTaken);
                }
            }
                
            if (negativeTransitionsA > stage.resultSpinoffMinTrials) {
                if (pNeg < P_THRESHOLD) {
                    schema.spinoffWithNewResultItem(item, false, pNeg, numTrialsActionTaken);
                }
            }
        }
    }



            //             no-action  action
            // transition     n11          n21
            // no-transition  n12          n22  


            //                   (placebo)
            //                   ACTION NOT TAKEN                          ACTION TAKEN

            // POS TRANSITION    posTransitionsNA                          posTransitionsA

            // NO-TRANSITION     (numTrialsActionNotTaken-posTransitionsNA)  (numTrialsActionTaken -posTransitionsA)


            /*public static double[] fishersExactTest(int n11,
                                        int n12,
                                        int n21,
                                        int n22)
                                        Calculate Fisher's exact test from the four cell counts.
                                        Parameters:
                                        n11 - Frequency for cell(1,1).
                                        n12 - Frequency for cell(1,2).
                                        n21 - Frequency for cell(2,1).
                                        n22 - Frequency for cell(2,2).
                                        Returns:
                                        double vector with three entries. [0] = two-sided Fisher's exact test. [1] = left-tail Fisher's exact test. [2] = right-tail Fisher's exact test.
            */

    public double computePosProbabilities(int positiveTransitionsNA, int positiveTransitionsA, int numTrialsActionTaken, int numTrialsActionNotTaken) {
            int p11 = (int) positiveTransitionsNA;
            int p21 = (int) numTrialsActionNotTaken - positiveTransitionsNA;
            int p12 = (int) positiveTransitionsA;
            int p22 = (int) numTrialsActionTaken - positiveTransitionsA;

            double pPos = FishersExactTest.fishersExactTest(p11,p12,p21,p22)[0];
            return pPos;
    }

    public double computeNegProbabilities(int negativeTransitionsNA, int negativeTransitionsA, int numTrialsActionTaken, int numTrialsActionNotTaken) {
            int n11 = (int) negativeTransitionsNA;
            int n21 = (int) numTrialsActionNotTaken - negativeTransitionsNA;
            int n12 = (int) negativeTransitionsA;
            int n22 = (int) numTrialsActionTaken - negativeTransitionsA;

            double pNeg = FishersExactTest.fishersExactTest(n11,n12,n21,n22)[0];
            return pNeg;
    }

    public void resetCounters() {
        resetCounters(negTransitionActionNotTaken);
        resetCounters(negTransitionActionTaken);
        resetCounters(posTransitionActionNotTaken);
        resetCounters(posTransitionActionTaken);
    }

    public void resetCounters(TDoubleArrayList a) {
        for (int i = 0; i < a.size(); i++) {
            a.set(i, 0);
        }
    }

    public void clearNegativeItems(int itemId) {
        negTransitionActionNotTaken.set(itemId, 0);
        negTransitionActionTaken.set(itemId, 0);
    }

    public void clearPositiveItems(int itemId) {
        posTransitionActionNotTaken.set(itemId, 0);
        posTransitionActionTaken.set(itemId, 0);
    }

    public String toHTML(Stage stage, Schema schema) {
        StringWriter s = new StringWriter();
        PrintWriter p = new PrintWriter(s);
        
        ArrayList<Item> items = stage.items;
        //growArrays(stage.nitems);
        for (int n = 0; n < items.size(); n++) {
            Item item = items.get(n);
            if (item != null) {


                int positiveTransitionsA = (int) posTransitionActionTaken.get(n);
                int positiveTransitionsNA = (int) posTransitionActionNotTaken.get(n);

                int negativeTransitionsA = (int) negTransitionActionTaken.get(n);
                int negativeTransitionsNA = (int) negTransitionActionNotTaken.get(n);


                double pPos = computePosProbabilities(positiveTransitionsNA, positiveTransitionsA, numTrialsActionTaken, numTrialsActionNotTaken);
                double pNeg = computeNegProbabilities(negativeTransitionsNA, negativeTransitionsA, numTrialsActionTaken, numTrialsActionNotTaken);



                // Compute Chi-squared value  = Sum (o-e)^2 / e
                p.println(String.format("<tr><td align=left>%d %s "
                                        +"<td><b>+</b> %.2f <td><span class=\"chart1\" style=\"width: %dpx;\">%d/%d</span> "
                                        +"<td><span class=\"chart2\" style=\"width: %dpx;\">%d/%d</span>"
                                        +"<td><b>-</b> %.2f <td><span class=\"chart1\" style=\"width: %dpx;\">%d/%d</span>"
                                        +"<td><span class=\"chart2\" style=\"width: %dpx;\">%d/%d</span></td></tr>",
                                        n, item.makeLink(),
                                        pPos,
                                        Math.max(10, positiveTransitionsA*4), positiveTransitionsA, numTrialsActionTaken,
                                        Math.max(10, positiveTransitionsNA*4), positiveTransitionsNA,  numTrialsActionNotTaken,
                                        pNeg,
                                        Math.max(10, negativeTransitionsA*4), negativeTransitionsA, numTrialsActionTaken,
                                        Math.max(10, negativeTransitionsNA*4), negativeTransitionsNA, numTrialsActionNotTaken));
            }
        }

        return s.toString();
    }


    /**
       Makes sure array a can be indexed up to n-1
     */
    void growArray(TDoubleArrayList a, int n) {
        int delta = n - a.size();
        for (int i = 0; i < delta; i++) {
            a.add(0);
        }
    }

    void growArrays(int n) {
        growArray(posTransitionActionTaken,n);
        growArray(posTransitionActionNotTaken,n);
        growArray(negTransitionActionTaken,n);
        growArray(negTransitionActionNotTaken,n);
        /*
          growArray(remainedOnActionTaken,n);
          growArray(remainedOnActionNotTaken,n);
          growArray(remainedOffActionTaken,n);
          growArray(remainedOffActionNotTaken,n);
        */
    }

}
'''
#!/usr/bin/env python
"""
Class for Yahtzee widget, and related functions.
"""

#-----------------------                                                        
#Imports                                                                        
#-----------------------
from numpy import *
import sys
from collections import Counter
from math import factorial

#-----------------------                                                        
#Globals
#-----------------------
combos=['three of a kind','four of a kind','full house','small straight','large straight','yahtzee','chance','ones','twos','threes','fours','fives','sixes']
combos_weighted=[]
for combo in combos:
    combos_weighted.append(combo+' weighted')

#-----------------------                                                        
#Classes                                                                        
#-----------------------
class Widget:
    """
    Allows you to specify points for each roll at the end
    of the turn, and then has all the tools to calculate
    the optimal strategy, (strategy that maximizes expected
    number of points), and the expected number of points
    given the strategy.  It is also possible to give a string
    like 'yahtzee' which will give 1 point to all rolls considered
    to be yahtzees (all numbers the same), and 0 points to
    everything else.
    """
    def __init__(self,points,n_dice=5,n_faces=6,n_rolls=3):
        """
        points is either a string giving a type of yahtzee
        combination (e.g. 'yahtzee', 'four of a kind'), or
        a dictionary giving point values for each possible
        roll (specified as a tuple) on the last turn.

        n_dice = number of dice; 5 is the default value as
        in the ordinary game of Yahtzee.

        n_faces = number of faces; 6 is the default value as
        with ordinary dice.

        n_rolls = number of rolls allowed (first roll plus
        re-rolls); 3 is the default value as in the ordinary
        game of Yahtzee.
        """
        self.n_dice=parse_int(n_dice,"n_dice",1)
        self.n_faces=parse_int(n_faces,"n_faces",1)
        self.n_rolls=parse_int(n_rolls,"n_rolls",1)

        #self.values is a list of n_rolls dictionaries.
        #The elements of the list correspond to successive
        #rolls, and they are dictionaries giving the
        #expected number of points for each roll at that
        #turn. self.values[-1] is therefore the dictionary
        #input by the user via the "points" argument to
        #__init__, specifying the point values of each
        #possible roll after the last turn.  The keys of
        #the dictionaries are rolls, which are represented
        #by sorted tuples of integers.  For now,
        #initialize self.values to a list of n_rolls
        #empty dictionaries.
        self.values=[]
        for i in range(self.n_rolls):
            self.values.append({})

        #self.strategy is a list of n_rolls-1 dictionaries.
        #The elements of the list correspond to successive rolls
        #(except the last one), and they are dictionaries
        #that tell which numbers to keep (and not re-roll)
        #for each possible roll on that turn.  Thus the keys
        #of the dictionaries are sorted tuples representing
        #the rolls, and the values are lists of sorted tuples
        #of a subset of the integers in the roll, which are the
        #numbers to be kept and not re-rolled.  The values are
        #lists of tuples because there may be more than one
        #optimal choice of numbers to keep, and the list will
        #contain them all.  For now, initialize self.strategy
        #to a list of n_rolls-1 empty dictionaries.
        self.strategy=[]
        for i in range(self.n_rolls-1):
            self.strategy.append({})
        
        if type(points)==str:
            self.parse_points_str(points)
        elif type(points)==dict:
            self.parse_points_dict(points)
        else:
            print >> sys.stderr, "Error in Widget.__init__: points must be a string or dictionary."
            exit()

        #Compute the optimal strategy and expected scores.
        self.compute_strategy()

    def parse_points_str(self,points):
        """
        Takes a string describing a combination, such
        as 'yahtzee', or 'four of a kind', creates a dictionary
        called points_dict which gives a point value of 1 to
        rolls of that type and 0 to rolls not of that type,
        and passes points_dict to self.parse_points_dict.
        Can also add the word 'weighted' on the end, e.g.
        'four of a kind weighted', to weight rolls by the actual
        number of points you would score with that roll, rather
        than just 1.
        """
        numbers=['ones','twos','threes','fours','fives','sixes']
        numbers_weighted=[]
        for combo in numbers:
            numbers_weighted.append(combo+' weighted')

        combo=points.lower()

        if combo not in combos and combo not in combos_weighted:
            print >> sys.stderr, "Error in Widget.parse_points_str:", points, "not a valid combination.  Must be one of:"
            for c in combos:
                print >> sys.stderr, c, "[weighted]"
            exit()

        #Checked that combo is a valid combination, now big if
        #statement to create points_dict for each combination.
        points_dict={}

        #Begin big if statement
        #-----------------------------------------------------
        if combo=='three of a kind' or combo=='three of a kind weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                #c.most_common(1)[0] gives an order pair:
                #(most common number,its frequency)
                #Thus c.most_common(1)[0][1] is the frequency
                #of the most common number.
                if c.most_common(1)[0][1]>=3:
                    if combo=='three of a kind':
                        points_dict[roll]=1.
                    else:
                        points_dict[roll]=float(sum(roll))
                else:
                    points_dict[roll]=0.
            
        elif combo=='four of a kind' or combo=='four of a kind weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                #c.most_common(1)[0] gives an order pair:
                #(most common number,its frequency)
                #Thus c.most_common(1)[0][1] is the frequency
                #of the most common number.
                if c.most_common(1)[0][1]>=4:
                    if combo=='four of a kind':
                        points_dict[roll]=1.
                    else:
                        points_dict[roll]=float(sum(roll))
                else:
                    points_dict[roll]=0.
            
        elif combo=='full house' or combo=='full house weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                #For an arbitary number of dice, I define a full
                #house to be only two different numbers appearing
                #in the roll, and n_dice/2 of each for n_dice even,
                #but (n_dice+1)/2 of one and (n_dice-1)/2 of the
                #other for n_dice odd.
                #
                #To treat both cases at the same time, let
                #
                #freq1=c.most_common(2)[0][1]
                #freq2=c.most_common(2)[1][1]
                #
                #i.e. freq1 and freq2 are the frequencies of the
                #two most common numbers.  For a full house, must
                #have freq1+freq2=n_dice, and freq1, freq2 >= n_dice/2
                #(integer division).
                #
                #The case of n_dice=1 must be treated separately;
                #for that case, everything is a full house.
                if self.n_dice==1:
                    points_dict[roll]=1.
                else:
                    mc=c.most_common(2)
                    freq1=mc[0][1]
                    if len(mc)<2:
                        freq2=0
                    else:
                        freq2=mc[1][1]
                    if freq1+freq2==self.n_dice and freq1>=self.n_dice/2 and freq2>=self.n_dice/2:
                        points_dict[roll]=1.
                    else:
                        points_dict[roll]=0.

                if combo=='full house weighted':
                    points_dict[roll]*=25.  #25 is the point value of any full house

        elif combo=='small straight' or combo=='small straight weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                #A small straight means that n_dice-1 of the
                #numbers on the dice are in consecutive order,
                #and the remaining die can show any number.
                #We can split this into two cases:
                #(i) the remaining die shows a number different
                #than any of the other dice.
                #(ii) the remaining die shows a number the
                #same as one of the other dice.
                #Thus we have (i) all dice show different values
                #and (ii) two dice show the same values but all
                #the rest are different.  Therefore, we can look at
                #
                #freq1=c.most_common(2)[0][1]
                #freq2=c.most_common(2)[1][1]
                #
                #which are the frequencies of the most and second
                #most common number.  If freq1>2 then we definitely
                #can't have a small straight.  If freq1=2 and freq2=2,
                #then this is not a small straight either.  If freq1=2,
                #and freq2=1, then we can use the fact that roll is
                #sorted and test for case (ii) by checking if
                #roll[-1]-roll[0]=n_dice-2.  
                #If freq1=1 then all dice show different values, and
                #we can check for case(i) by checking if
                #roll[-2]-roll[0]=n_dice-2 or roll[-1]-roll[1]=n_dice-2.
                #
                #n_dice<=2 must be treated separately; in this case
                #everything is a small straight.
                if self.n_dice<=2:
                    points_dict[roll]=1.
                else:
                    mc=c.most_common(2)
                    freq1=mc[0][1]
                    if len(mc)<2:
                        freq2=0
                    else:
                        freq2=mc[1][1]
                    if freq1>2:
                        points_dict[roll]=0.
                    elif freq1==2:
                        if freq2==1 and roll[-1]-roll[0]==self.n_dice-2:
                            points_dict[roll]=1.
                        else:
                            points_dict[roll]=0.
                    else:
                        if roll[-2]-roll[0]==self.n_dice-2 or roll[-1]-roll[1]==self.n_dice-2:
                            points_dict[roll]=1.
                        else:
                            points_dict[roll]=0.
                
                if combo=='small straight weighted':
                    points_dict[roll]*=30.  #30 is the point value of any small straight

        elif combo=='large straight' or combo=='large straight weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                #A large straight is when all dice show numbers
                #in consecutive order.  Since roll is sorted, can
                #test for this by checking that all numbers in
                #the roll are different (c.most_common(1)[0][1]=1),
                #and that roll[-1]-roll[0]=n_dice-1.
                if c.most_common(1)[0][1]==1 and roll[-1]-roll[0]==self.n_dice-1:
                    points_dict[roll]=1.
                else:
                    points_dict[roll]=0.

                if combo=='large straight weighted':
                    points_dict[roll]*=40.  #40 is the point value of any large straight

        elif combo=='yahtzee' or combo=='yahtzee weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                if c.most_common(1)[0][1]==self.n_dice:
                    points_dict[roll]=1.
                else:
                    points_dict[roll]=0.

                if combo=='yahtzee weighted':
                    points_dict[roll]*=50.  #50 is the point value of any yahtzee

        elif combo=='chance' or combo=='chance weighted':
            for roll in rolls(self.n_dice,self.n_faces):
                if combo=='chance':
                    points_dict[roll]=1.
                else:
                    points_dict[roll]=float(sum(roll))

        elif combo in numbers or combo in numbers_weighted:
            if combo in numbers:
                num=numbers.index(combo)+1
            else:
                num=numbers_weighted.index(combo)+1
            for roll in rolls(self.n_dice,self.n_faces):
                c=Counter(roll)
                if combo in numbers:
                    if c[num]>0:
                        points_dict[roll]=1.
                    else:
                        points_dict[roll]=0.
                else:
                    points_dict[roll]=float(c[num]*num)

        #-----------------------------------------------------
        #End of big if statement to create points_dict for
        #each combination.  Now pass points_dict to
        #self.parse_points_dict.
        self.parse_points_dict(points_dict)

    def parse_points_dict(self,points):
        """
        Uses the dictionary points to initialize
        self.values[-1].  Checks that the keys
        of points correspond to unique rolls
        before copying to self.values[-1].
        """

        #Clear self.values[-1]
        self.values[-1]={}

        #Run through the key, value pairs of points, check that
        #the keys are valid rolls, then add the key, value pair
        #to self.values[-1].
        for key, value in points.iteritems():
            
            if type(key)!=tuple:
                print >> sys.stderr, "Error in Widget.parse_points_dict: keys in points dictionary must be tuples."
                exit()

            if len(key)!=self.n_dice:
                print >> sys.stderr, "Error in Widget.parse_points_dict: keys in points must be tuples of length", self.n_dice
                exit()

            #Check that each element of the tuple representing the roll
            #is an integer between 1 and self.n_faces.
            for i in key:
                if i<1 or i>self.n_faces:
                    print >> sys.stderr, "Error in Widget.parse_points_dict: numbers in rolls must be between 1 and", self.n_faces
                    exit()
                if type(i)!=int:
                    print >> sys.stderr, "Error in Widget.parse_points_dict: numbers in rolls must be integers."
                    exit()

            #key is a valid tuple representing a roll if you get
            #to this point, however, we only want to deal with sorted
            #tuples as rolls.
            roll=tuple(sort(key))

            #If this roll already has a point value assigned to it
            #in self.values[-1], different than that of "value",
            #then this is an error.
            if roll in self.values[-1].keys() and self.values[-1][roll]!=value:
                print >> sys.stderr, "Error in Widget.parse_points_dict: multiple, inconsistent point values given for roll", roll
                exit()
            #Otherwise we can assign a point value of "value" to
            #this roll in self.values[-1].
            self.values[-1][roll]=value

        #For any rolls for which point values have not yet
        #been specified in self.values[-1], give them point
        #values of 0.
        for roll in rolls(self.n_dice,self.n_faces):
            if roll not in self.values[-1].keys():
                self.values[-1][roll]=0.

    def compute_strategy(self):
        """
        Compute which dice to keep for a given roll at a given
        turn (self.strategy), and the expected number of points
        after a given roll (self.values).
        """
        for turn in range(self.n_rolls-2,-1,-1):
            #For each possible set of kept dice at this turn,
            #calculate the expected value of the points you'll
            #get after you roll (i.e. at the beginning of the
            #next turn).  Number of kept dice can be from 0
            #to self.n_dice.  (For self.n_dice kept dice, can
            #read off the "expected" values from self.values[turn+1].)
            #Store this in the dictionary "expected_pts", where
            #the keys are the values of the dice kept and the values
            #are the expected number of points after rolling.
            expected_pts={}
            for n_kept in range(0,self.n_dice+1):
                for kept in rolls(n_kept,self.n_faces):
                    expected_pts[kept]=self.expected_given_kept(kept,turn)
            #Want to sort expected_pts by values so that it
            #is easier to find maxima.  (Sort in reverse order
            #so that max value is first.)
            expected_pts_sorted=[(key,expected_pts[key]) for key in sorted(expected_pts.keys(),key=lambda k:expected_pts[k],reverse=True)]
            #expected_pts_sorted is a list of (key,value) pairs
            #from expected_pts that are sorted by value from max
            #value to min value.
            
            
            #Now go through all possible rolls for this turn,
            #see which set(s) of dice are the optimal ones to keep,
            #(in that they lead to the highest expected number of
            #points), and record the sets in self.strategy[turn],
            #and the expected number of points in self.values[turn].
            for roll in rolls(self.n_dice,self.n_faces):
                #First set self.values[turn][roll] to None, and
                #self.strategy[turn][roll] to [], so that we know
                #that we haven't yet found the max value yet.
                self.values[turn][roll]=None
                self.strategy[turn][roll]=[]
                #Now we go through the (kept,value) pairs in
                #expected_pts_sorted in order.
                for kept, value in expected_pts_sorted:
                    #We can ignore 'kept' if it is not a possible
                    #set of dice to keep from this roll, (e.g.
                    #if kept=(1,2,3) and roll=(1,2,4,5,6), then
                    #it's not possible to keep 'kept' from this
                    #roll).  Test whether we continue to examine
                    #'kept' in the following if statement:
                    if subroll(kept,roll):
                        #Is this the first 'kept' we have encountered
                        #that it is possible to keep from 'roll'?
                        if self.values[turn][roll]==None:
                            #Yes, thus value is the max possible
                            #value we can get since expected_pts_sorted
                            #is sorted.  Therefore record it in
                            #self.values[turn][roll], (and also this will
                            #stop us from reaching this branch of the
                            #if statement in the future), and record
                            #'kept' as one possible optimal strategy
                            #in self.strategy[turn][roll].
                            self.values[turn][roll]=value
                            self.strategy[turn][roll].append(kept)
                        elif eql_float(value,self.values[turn][roll]):
                            #No, but this 'kept' has the same expectation
                            #value of points as the optimal one we already
                            #found.  Thus add this 'kept' to
                            #self.strategy[turn][roll] as another possible
                            #optimal strategy.
                            self.strategy[turn][roll].append(kept)
                        else:
                            #No, and in fact this value of 'kept' has a
                            #smaller number of expected points than the
                            #optimal one, thus we can end the for loop
                            #since there will be no more optimal strategies.
                            break
                    #If we have a value recorded for self.values[turn][roll],
                    #we can check if the current 'value' is less than it, in
                    #which case we can break out of the for loop right away,
                    #even if 'kept' is not a possible keep for this roll.
                    if self.values[turn][roll]!=None and not eql_float(value,self.values[turn][roll]):
                        break

        #We have now computed the optimal strategy and expectation
        #values for each turn.  The last thing we want to compute
        #is the a priori expected number of points, i.e. the average
        #over all possible rolls of self.values[0][roll].
        self.expected=0
        denom=0
        for roll in rolls(self.n_dice,self.n_faces):
            mult=multiplicity(roll)
            self.expected+=mult*self.values[0][roll]
            denom+=mult
        self.expected=float(self.expected)/float(denom)

    def expected_given_kept(self,kept,turn):
        """
        Calculate the expected number of points if you keep
        dice 'kept' at turn 'turn', (given that you use optimal
        strategy after that).
        """
        n_kept=len(kept)
        tot=0
        denom=0
        for rolled in rolls(self.n_dice-n_kept,self.n_faces):
            roll=tuple(sort(kept+rolled))
            mult=multiplicity(rolled)
            #Note that it's the probability of getting the values
            #in 'rolled' that we care about, since we have already
            #obtained the values in 'kept' at this turn.  Thus
            #we used multiplicity(rolled) and not multiplicity(roll).
            tot+=mult*self.values[turn+1][roll]
            denom+=mult
        return float(tot)/float(denom)

    def advise(self,turn,roll):
        """
        Gives you the optimal strategy and expected number
        of points given a roll on a given turn.  This is
        just a nicer way to display self.strategy[turn][roll]
        and self.values[turn][roll].
        NOTE:  For the input here, we assume turn numbers
        start at 1, and then subtract 1 before using it,
        because this is a more 'user facing' function.
        """
        #Let's assume the user gives turn numbers starting
        #at 1 rather than 0.
        turn=parse_int(turn,"turn",1,self.n_rolls)-1

        #Parse roll
        r=tuple(sort(roll))
        if len(r)!=self.n_dice:
            print >> sys.stderr, "Error in Widget.advise: roll must consist of", self.n_dice, "dice."
            exit()
        if r not in self.values[0].keys():
            print >> sys.stderr, "Error in Widget.advise:", roll, "not a valid roll."
            exit()

        #Print the optimal strategy
        if turn==self.n_rolls-1:
            print "Score:", self.values[turn][r]
        else:
            print "Possible dice to keep:"
            for keep in self.strategy[turn][r]:
                print keep
            print ""
            print "Expected number of points:", self.values[turn][r]


#-----------------------                                                        
#Functions                                                                      
#-----------------------

def parse_int(n,name,lower=None,upper=None):
    """
    Checks that n is a type int, and that it is in
    the bounds [lower,upper] if provided.  Return n
    if it meets these conditions.
    """
    if type(n)!=int:
        print >> sys.stderr, "Error:", name, "not type int."
        exit()

    if lower!=None and n<lower:
        print >> sys.stderr, "Error:", name, "must be >=", lower
        exit()

    if upper!=None and n>upper:
        print >> sys.stderr, "Error:", name, "must be <=", upper
        exit()

    return n

def rolls(n_dice,upper,lower=1):
    """
    This generator returns an iterator over all
    possible rolls of n_dice dice, where each die
    has the integer values from lower to upper
    (inclusive) exactly once on different faces.
    It returns each roll as a sorted tuple of length
    n_dice for which each entry is an integer from
    lower to upper.

    Ex.  3 dice, upper=6, lower=1, returns
    (1,1,1)
    (1,1,2)
    .
    .
    .
    (5,6,6)
    (6,6,6)
    """
    if n_dice==0:
        yield ()
    else:
        for first_die in range(lower,upper+1):
            for rest_die in rolls(n_dice-1,upper,first_die):
                yield (first_die,)+rest_die

def multiplicity(roll):
    """
    Returns the number of ways you can get a given roll,
    (i.e. treating the dice as distinguishable).
    """
    c=Counter(roll)
    return factorial(len(roll))/product([factorial(n) for n in c.values()])

def subroll(sr,roll):
    """
    Returns True if sr is a subroll of roll, and False
    if it isn't.  A subroll is a set of dice values that
    can be taken out of roll.  For example if
    roll=(1,1,2,3,3), then (1,2,3,3) is a subroll of roll,
    but (1,2,2,3) and (1,5) are not.
    """
    r_list=list(roll)
    sr_list=list(sr)
    for d in sr_list:
        try:
            r_list.pop(r_list.index(d))
        except ValueError:
            return False
    return True

def eql_float(x,y):
    """
    Tests if x and y are equal within a relative
    error of eps.
    """
    eps=1.E-10
    #If both of the values are exactly 0, then they
    #are equal.
    if x==0 and y==0:
        return True
    #Otherwise, if they average to 0, then use relative
    #error with respect to one of the values (doesn't
    #matter which because x=-y in this case).
    if x+y==0:
        return float(abs(x-y))/float(abs(x))<eps
    #Otherwise use relative error with respect to
    #average.
    return 2.*float(abs(x-y))/float(abs(x+y))<eps


#-----------------------                                                        
#Test Cases
#-----------------------

if __name__ == "__main__":
    #YAHTZEE
    w=Widget('yahtzee')
    print "Probability of getting a yahtzee =", w.expected
    for i in range(1,7):
        for turn in range(3):
            assert(w.values[turn][(i,)*5]==1.0)
    assert(w.values[2][(1,1,2,2,3)]==0.0)
    assert(w.values[2][(1,2,3,5,6)]==0.0)
    assert(w.values[2][(3,4,4,5,6)]==0.0)
    for i in range(2,7):
        assert(w.values[1][(1,1,1,1,i)]==1./6.)
    for i in range(5,7):
        assert(w.values[1][(4,4,4,4,i)]==1./6.)
    assert(w.values[1][(3,3,3,5,5)]==1./36.)
    assert(w.values[1][(2,3,4,4,4)]==1./36.)
    assert(w.values[1][(2,2,5,5,6)]==1./6.**3)
    assert(w.values[1][(1,2,3,3,5)]==1./6.**3)
    assert(w.values[1][(1,2,3,4,5)]==1./6.**4)
    assert(w.values[1][(1,2,4,5,6)]==1./6.**4)

    #Keep all for five of a kind
    assert(w.strategy[1][(1,)*5]==[(1,)*5])
    assert(w.strategy[1][(5,)*5]==[(5,)*5])
    assert(w.strategy[0][(1,)*5]==[(1,)*5])
    assert(w.strategy[0][(5,)*5]==[(5,)*5])

    #Keep four for four of a kind
    assert(w.strategy[1][(2,)*4+(3,)]==[(2,)*4])
    assert(w.strategy[1][(2,)+(5,)*4]==[(5,)*4])
    assert(w.strategy[0][(2,)*4+(3,)]==[(2,)*4])
    assert(w.strategy[0][(2,)+(5,)*4]==[(5,)*4])

    #Keep three for three of a kind
    assert(w.strategy[1][(1,2,3,3,3)]==[(3,3,3)])
    assert(w.strategy[1][(2,2,6,6,6)]==[(6,6,6)])
    assert(w.strategy[1][(4,4,4,5,6)]==[(4,4,4)])
    assert(w.strategy[0][(1,2,3,3,3)]==[(3,3,3)])
    assert(w.strategy[0][(2,2,6,6,6)]==[(6,6,6)])
    assert(w.strategy[0][(4,4,4,5,6)]==[(4,4,4)])

    #Keep any two for two of a kind
    assert(w.strategy[1][(2,2,3,5,6)]==[(2,2)])
    assert(sorted(w.strategy[1][(1,1,4,4,5)])==sorted([(1,1),(4,4)]))
    assert(sorted(w.strategy[1][(3,3,5,6,6)])==sorted([(3,3),(6,6)]))
    assert(sorted(w.strategy[1][(1,2,2,4,4)])==sorted([(2,2),(4,4)]))
    assert(w.strategy[0][(2,2,3,5,6)]==[(2,2)])
    assert(sorted(w.strategy[0][(1,1,4,4,5)])==sorted([(1,1),(4,4)]))
    assert(sorted(w.strategy[0][(3,3,5,6,6)])==sorted([(3,3),(6,6)]))
    assert(sorted(w.strategy[0][(1,2,2,4,4)])==sorted([(2,2),(4,4)]))

    #Keep any one, or re-roll all for all dice different
    assert(sorted(w.strategy[1][(1,2,3,4,5)])==sorted([(),(1,),(2,),(3,),(4,),(5,)]))
    assert(sorted(w.strategy[1][(1,2,3,5,6)])==sorted([(),(1,),(2,),(3,),(5,),(6,)]))
    assert(sorted(w.strategy[0][(1,2,3,4,5)])==sorted([(),(1,),(2,),(3,),(4,),(5,)]))
    assert(sorted(w.strategy[0][(1,2,3,5,6)])==sorted([(),(1,),(2,),(3,),(5,),(6,)]))

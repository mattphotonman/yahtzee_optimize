yahtzee_optimize
==============

Code to find the optimal strategy for getting a certain combination (e.g. Yahtzee, four of a kind, full house) in a turn of Yahtzee, and to calculate the probability of getting it if you follow the optimal strategy.  The desired combination is encoded by specifying point values for each possible roll of the dice at the end of the turn, and the code finds the strategy that maximizes the expectation value of the number of points.  The expectation value of the number of points with the optimal strategy is also returned.  If you want to know a probability of a certain combination, you can set the points for rolls belonging to that combination to 1, and set the points to 0 for all other rolls.

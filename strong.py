import itertools
import csv
import sys
import random
import copy
import numpy as np
import GS
from copy import deepcopy
import math


def factorial(x):
    if x == 0:
        return 1
    return x * factorial(x - 1)


def randomise_selection(distribution):
    """
    Returns a position in the probability distribution, that
    indicates the pure strategy a player chooses.
    """

    selection = random.random()
    strategy = 0
    count = 0
    for i in range(len(distribution)):
        count += distribution[i]
        if selection < count:
            strategy = i
            break
    return strategy


class STRONG(object):
    def __init__(self, call_svd, services, no_objects, data, attacker_flag):
        """
        Class constructor.
        """

        self.call_svd = call_svd
        self.no_objects = no_objects
        self.objects = []
        self.attacker_flag = attacker_flag

        for i in range(self.no_objects):
            self.objects.append(i + 1)

        self.sec_levels = []  # Stores all security levels
        self.k = services  # Number of objects that the user wants to get connected to
        self.data_value = data  # In dollars
        self.no_subsets = factorial(self.no_objects) / (factorial(self.k) * factorial(self.no_objects - self.k))

        print 'self.no_subsets:', self.no_subsets

        self.subsets_set = []
        self.risks = []
        self.total_risks = 0
        self.subsets = []
        self.user_matrix = [[0] * self.no_objects for i in range(self.no_subsets)]
        self.att_matrix = [[0] * self.no_objects for i in range(self.no_subsets)]
        self.user_np_matrix = []
        self.att_np_matrix = []
        self.nash_user_selection = []
        self.nash_attack_plan = []
        self.margin_prob = []
        self.uniform_attack_dist = []
        self.uniform_user_dist = []
        self.weighted_user_dist = []
        self.weighted_attack_dist = []

        if call_svd == 1:
            self.epsilon_svd = int(raw_input('Enter epsilon SVD: '))
        else:
            self.epsilon_svd = 0

    def init_sec_levels(self):

        for i in range(self.no_objects):
            self.sec_levels.append(random.uniform(0, 1))

        print '\nself.sec_levels:', self.sec_levels

    def set_sec_levels(self):

        for i in range(self.no_objects):
            i += 1
            self.sec_levels.append(i * 0.2)

        print '\nself.sec_levels:', self.sec_levels

    def tft_sec_levels(self):

        for i in range(self.no_objects):
            T = [0.3, 0.6, 0.9]
            self.sec_levels.append(random.choice(T))
        print '\nself.sec_levels:', self.sec_levels

    def ct_sec_levels(self):

        for i in range(self.no_objects):
            T = [0.45903868385409985, 0.7371754671998441, 0.6676242672881497, 0.7538678105061125, 0.2811773064524299, 0.19154419668506983, 0.3861111154873823, 0.3906000917635587, 0.43374891851646413, 0.19176892148048952, 0.6884897167963834, 0.6841221981752692, 0.2455405198527275, 0.3004114463226747, 0.23342427450070213]
            self.sec_levels.append(T[i])
        print '\nself.sec_levels:', self.sec_levels

    def compute_risks(self):
        """
        Computes the risks of all objects.
        """

        for i in range(self.no_objects):
            curr_risk = (1 - self.sec_levels[i]) * self.data_value
            self.total_risks += curr_risk
            self.risks.append(curr_risk)

    def compute_subsets(self):
        """
        Computes all possible subsets.
        """
  
        # Returns all subsets of size k of O, with objects ID
        self.subsets_set = set(itertools.combinations(self.objects, self.k))
        if self.no_subsets != len(self.subsets_set):
            print 'Error....'
        self.subsets = list(self.subsets_set)
        print '\nsubsets_list:', self.subsets
        return self.subsets

    def solve_game(self):

       #omitted due to classificatio, but any game solver can be inserted

    def compute_marginal_prob(self):

        for i in range(self.no_objects):
            prob = 0
            for subset in range(self.no_subsets):
                for obj in range(self.k):
                    if self.subsets[subset][obj] == i + 1:
                        prob += self.nash_user_selection[subset]
            self.margin_prob.append(prob)
        print 'self.margin_prob:', self.margin_prob

    def simulator(self):
        """
        Simulates StRONG.
        """
        print 'risks:', self.risks

        total_NUOS_damage = 0
        total_uniform_damage = 0
        total_css_damage = 0

        sample_size = 500

        for obj in range(self.no_objects):
            self.uniform_attack_dist.append(float(1) / self.no_objects)

        for subset in range(self.no_subsets):
            self.uniform_user_dist.append(float(1) / self.no_subsets)

        temp_list = deepcopy(self.sec_levels)
        temp_list.sort()
        temp_list.reverse()

        css_list = []
        css_strat = []

        subsets_risks = []  
        total_subsets_risks = 0

        for i in range(len(self.subsets)):
            curr_subset_risk = 0
            for j in range(self.k):
                curr_subset_risk += self.risks[self.subsets[i][j] - 1]
            total_subsets_risks += curr_subset_risk
            subsets_risks.append(curr_subset_risk)

        for i in range(len(subsets_risks)):
            self.weighted_user_dist.append(subsets_risks[i] / total_subsets_risks)

        print 'self.weighted_user_dist:', self.weighted_user_dist

        for i in range(self.no_objects):
            self.weighted_attack_dist.append(self.risks[i] / self.total_risks)

        print 'self.weighted_attack_dist:', self.weighted_attack_dist

        sum_weights = 0
        for i in range(len(self.weighted_attack_dist)):
            sum_weights += self.weighted_attack_dist[i]

        print 'sum_weights:', sum_weights
        css_user_pure_strat = 0
        for i in range(self.k):
            css_list.append(temp_list[i])

        for i in range(len(css_list)):
            for j in range(len(self.sec_levels)):
                if self.sec_levels[j] == css_list[i]:
                    css_strat.append(j)
                    break
            if len(css_strat) == self.k:
                break

        for i in range(len(self.subsets)):
            if list(self.subsets[i]) == css_strat:
                css_user_pure_strat = i
                break

        att_pure_strat = - 1

        for sample in range(sample_size):
            nash_user_pure_strat = randomise_selection(self.nash_user_selection)  # Randomize NUOS
            uniform_user_pure_strat = randomise_selection(self.uniform_user_dist)  # Randomize Uniform user

            if self.attacker_flag == 1:  # Uniform attacker
                uniform_att_pure_strat = randomise_selection(self.uniform_attack_dist)  # Randomize Uniform attack
                att_pure_strat = uniform_att_pure_strat
                print 'uniform_user_pure_strat:', uniform_user_pure_strat
            elif self.attacker_flag == 2:  # Weighted attacker
                weighted_att_pure_strat = randomise_selection(self.weighted_attack_dist)  # Randomize Weighted attack
                att_pure_strat = weighted_att_pure_strat
                print 'att_pure_strat:', att_pure_strat
                print 'weighted_att_pure_strat: ', weighted_att_pure_strat
            elif self.attacker_flag == 3:  # Nash attacker
                nash_att_pure_strat = randomise_selection(self.nash_attack_plan)  # Randomize Nash attack
                att_pure_strat = nash_att_pure_strat
                print '\nnash_user_pure_strat:', nash_user_pure_strat

            # Calculate the User's Damage for a pair of pure strategies.
            total_NUOS_damage += self.user_matrix[nash_user_pure_strat][att_pure_strat]
            total_uniform_damage += self.user_matrix[uniform_user_pure_strat][att_pure_strat]
            total_css_damage += self.user_matrix[css_user_pure_strat][att_pure_strat]

        print '\nTotal damage when using NUOS:', total_NUOS_damage
        print '\nTotal damage when uniform:', total_uniform_damage
        print '\nTotal damage when using css:', total_css_damage

if __name__ == '__main__':
    call_svd = int(raw_input('Press 1 to call svd, 0 otherwise: '))
    k = int(raw_input('Enter number of services: '))
    o = int(raw_input('Enter number of objects: '))
    d = int(raw_input('Enter data value: '))
    at = int(raw_input('Press 1 for Uniform, 2 for Weighted or 3 for Nash attacker:'))
    strong = STRONG(call_svd, k, o, d, at)
    sl = strong.compute_subsets()
    strong.ct_sec_levels()   
    strong.compute_risks()
    strong.solve_game()
    strong.simulator()




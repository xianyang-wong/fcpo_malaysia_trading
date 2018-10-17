# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 16:52:22 2018

@author: XY
"""
import itertools
import numpy as np
import random
import operator

def generate_rule(rule_choices):
    
    rule = []
    for i in range(0,len(rule_choices.keys())):
        rule.insert(i,random.choice(rule_choices[list(rule_choices.keys())[i]]))
    if rule[(len(rule_choices.keys())-1)] in [0,1,2]:
        rule.insert(len(rule_choices.keys()),random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0]))
    elif rule[(len(rule_choices.keys())-1)] in [4,5,6]:
        rule.insert(len(rule_choices.keys()),random.choice([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]))
    else:
        rule.insert(len(rule_choices.keys()),random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]))
    
    #rule = np.array(rule)    
        
    return rule

def generate_ruleset(n_rules, rule_choices):
    
    ruleset = []
    for i in range(0, n_rules):
        ruleset.insert(i,generate_rule(rule_choices))
        
    #ruleset = np.array(ruleset)    
    
    return ruleset

def generate_collection(n_rulesets, n_rules, rule_choices):
    
    collection = []
    for i in range(0, n_rulesets):
        collection.insert(i,generate_ruleset(n_rules, rule_choices))
        
    #collection = np.array(collection)    
        
    return collection

def roulette_wheel(collection, fitness, topn):
    total_fit = float(sum(fitness))
    relative_fitness = [f / total_fit for f in fitness]

    dictionary = dict(zip(range(0,20),relative_fitness))
    dictionary = dict(sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True))

    chosen = []
    for n in range(topn):
        r = random.random()
        current = 0
        for key, value in dictionary.items():
            current += value
            if current > r:
                chosen.append(key)
                break

    chosen_collection = []
    for choice in chosen:
        chosen_collection.append(collection[choice])

    return chosen_collection

def crossover(iteration_best80pct, crossover_pct):
    
    crossover_list = []
    collection_cross = iteration_best80pct.copy()
    
    for i in range(0, len(iteration_best80pct)):
        if random.uniform(0,1) <= crossover_pct:
            crossover_list.append(i)
            
    for cross in crossover_list:
        ruleset = iteration_best80pct[cross]
        partner_choice = random.choice([elem for elem in crossover_list if elem != cross])
        partner = iteration_best80pct[partner_choice]
        
        crossover_point = random.choice(range(1, len(ruleset) - 1))
        ruleset_a = ruleset[:crossover_point]
        ruleset_b = ruleset[crossover_point:]
        partner_a = partner[:crossover_point]
        partner_b = partner[crossover_point:]
        
        ruleset_cross = ruleset_a + partner_b
        partner_cross = partner_a + ruleset_b
        
        collection_cross[cross] = ruleset_cross
        collection_cross[partner_choice] = partner_cross
     
    return collection_cross
      
def mutation(iteration_best80pct, mutation_pct, rule_choices):

    #print('List of Mutations')
    collection_mutate = iteration_best80pct.copy()
    for i in range(0,len(iteration_best80pct)):
        for j in range(0,len(iteration_best80pct[i])):
            for k in range(0,len(iteration_best80pct[i][j])):
                if random.uniform(0,1) <= mutation_pct:
                    # Carrying out individual rule choice randomization
                    if k in range(0,len(rule_choices.keys())):
                        collection_mutate[i][j][k] = random.choice(rule_choices[list(rule_choices.keys())[k]])
                    else:
                        if iteration_best80pct[i][j][(k-1)] in [0,1,2]:
                            collection_mutate[i][j][k] = random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0])
                        elif iteration_best80pct[i][j][(k-1)] in [4,5,6]:
                            collection_mutate[i][j][k] = random.choice([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
                        else:
                            collection_mutate[i][j][k] = random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])

                    # Crossover amongst rules within ruleset
                    partner_list = [0,1,2,3,4,5,6,7,8,9]
                    partner_list2 = [partner for partner in partner_list if partner != j]
                    crossover_point = random.choice(range(1, len(collection_mutate[i][j]) - 1))
                    partner_choice = random.choice(partner_list2)

                    ruleset_a = collection_mutate[i][j][:crossover_point]
                    ruleset_b = collection_mutate[i][j][crossover_point:]
                    partner_a = collection_mutate[i][partner_choice][:crossover_point]
                    partner_b = collection_mutate[i][partner_choice][crossover_point:]

                    ruleset_cross = ruleset_a + partner_b
                    partner_cross = partner_a + ruleset_b

                    collection_mutate[i][j] = ruleset_cross
                    collection_mutate[i][partner_choice] = partner_cross

    return collection_mutate

def evolve(collection, rule_choices, fitness, crossover_pct, mutation_pct):
    
    # Select best two rulesets from last iteration
    iteration_collection = roulette_wheel(collection, fitness, 2)
    # Randomly generate two new rulesets
    iteration_collection.extend(generate_collection(2, 10, rule_choices))
    # Select best 16 from original 20 rulesets
    iteration_best80pct = roulette_wheel(collection, fitness, 16)
    # Carry out crossover
    iteration_best80pct = crossover(iteration_best80pct, crossover_pct)
    # Carry out mutation
    iteration_best80pct = mutation(iteration_best80pct, mutation_pct, rule_choices)
    
    iteration_collection.extend(iteration_best80pct)

    return iteration_collection

def generate_rule_choices(switch, ma_type_choices, long_moving_average_choices, short_moving_average_choices):
    if switch == 'same':
        ma_type_combinations = [list(tup) for tup in itertools.product(ma_type_choices, ma_type_choices)]
        filter_combinations = [combi[0] == combi[1] for combi in ma_type_combinations]
        ma_type_combinations = list(itertools.compress(ma_type_combinations, filter_combinations))
    elif switch == 'different':
        ma_type_combinations = [list(tup) for tup in itertools.product(ma_type_choices, ma_type_choices)]
        
    ma_combinations = [list(tup) for tup in itertools.product(long_moving_average_choices, short_moving_average_choices)]
    filter_combinations = [combi[0] > combi[1] for combi in ma_combinations]
    ma_combinations = list(itertools.compress(ma_combinations, filter_combinations))

    rule_choices = {
        'moving_average_choices': ma_type_combinations,
        'ma_combinations': ma_combinations,
        'membership_choices': [0, 1, 2, 3, 4, 5, 6],
    }

    return rule_choices

### Running the functions
# Defining rule choices
long_moving_average_choices = [10,20,50,100,150,200]
short_moving_average_choices = [1,3,5,10,15,20]
ma_type_choices = [0,1,2,3]

# Create collection of 20 different ruleset consisting of 10 rules each
#rule_choices = generate_rule_choices('same', ma_type_choices, long_moving_average_choices, short_moving_average_choices)
#collection = generate_collection(20, 10, rule_choices)

# Simulated fitness values
#fitness = np.array(range(0,20))

# Evolving collection based on fitness values, crossover rate of 70%, and mutation rate of 1%
#collection_evolve = evolve(collection, rule_choices, fitness, 0.7, 0.01)

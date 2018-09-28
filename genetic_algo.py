# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 16:52:22 2018

@author: XY
"""
import numpy as np
import random

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
        
    rule = np.array(rule)    
        
    return rule

def generate_ruleset(n_rules, rule_choices):
    ruleset = []
    for i in range(0, n_rules):
        ruleset.insert(i,generate_rule(rule_choices))
        
    ruleset = np.array(ruleset)    
    
    return ruleset

def generate_collection(n_rulesets, n_rules, rule_choices):
    collection = []
    for i in range(0, n_rulesets):
        collection.insert(i,generate_ruleset(n_rules, rule_choices))
        
    collection = np.array(collection)    
        
    return collection

def roulette_wheel(collection, fitness, topn):

    total_fit = float(sum(fitness))
    relative_fitness = [f/total_fit for f in fitness]
    probabilities = [sum(relative_fitness[:i+1]) 
                     for i in range(len(relative_fitness))]

    chosen = []
    for n in range(topn):
        r = random.random()
        for (i, ruleset) in enumerate(collection):
            if r <= probabilities[i]:
                chosen.append(list(ruleset))
                break
    return np.array(chosen)

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
        
        ruleset_cross = np.concatenate((ruleset_a, partner_b), axis=0)
        partner_cross = np.concatenate((partner_a, ruleset_b), axis=0)
        
        collection_cross[cross] = ruleset_cross
        collection_cross[partner_choice] = partner_cross
     
    return collection_cross
      
def mutation(iteration_best80pct, mutation_pct, rule_choices):
    
    collection_mutate = iteration_best80pct.copy()
    for i in range(0,len(iteration_best80pct)):
        for j in range(0,len(iteration_best80pct[i])):
            for k in range(0,len(iteration_best80pct[i][j])):
                if random.uniform(0,1) <= mutation_pct:
                    print(i,j,k)
                    if k in range(0,len(rule_choices.keys())):
                        collection_mutate[i][j][k] = random.choice(rule_choices[list(rule_choices.keys())[k]])
                    else:
                        if iteration_best80pct[i][j][(k-1)] in [0,1,2]:
                            collection_mutate[i][j][k] = random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0])
                        elif iteration_best80pct[i][j][(k-1)] in [4,5,6]:
                            collection_mutate[i][j][k] = random.choice([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
                        else:
                            collection_mutate[i][j][k] = random.choice([-1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    
    return collection_mutate

def evolve(collection, rule_choices, fitness, crossover_pct, mutation_pct):
    
    # Select best two rulesets from last iteration
    iteration_collection = roulette_wheel(collection, fitness, 2)
    # Randomly generate two new rulesets
    iteration_collection = np.append(iteration_collection, generate_collection(2, 10, rule_choices), axis=0)
    # Select best 16 from original 20 rulesets
    iteration_best80pct = roulette_wheel(collection, fitness, 16)
    # Carry out crossover
    iteration_best80pct = crossover(iteration_best80pct, crossover_pct)
    # Carry out mutation
    iteration_best80pct = mutation(iteration_best80pct, mutation_pct, rule_choices)
    
    iteration_collection = np.append(iteration_collection, iteration_best80pct, axis=0)

    return iteration_collection

# Create collection of 20 different ruleset consisting of 10 rules each
rule_choices = {
    'moving_average_choices' : [0,1,2,3],
    'long_moving_average_choices' : [10,20,50,100,150,200],
    'short_moving_average_choices' : [1,3,5,10,15,20],
    'membership_choices' : [0,1,2,3,4,5,6],        
        }
collection = generate_collection(20, 10, rule_choices)

fitness = np.array(range(0,20))
collection_evolve = evolve(collection, rule_choices, fitness, 0.7, 0.01)

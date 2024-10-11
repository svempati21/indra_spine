from indra_cogex.sources.odinson.grammars import Rule
from indra_cogex.sources.odinson.client import process_rules
import gilda
import pandas as pd
from collections import defaultdict
from gilda.process import normalize
from tqdm.auto import tqdm
from pyobo.gilda_utils import get_gilda_terms
import numpy as np

import textwrap
import random
import difflib

import indra_cogex
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

def spine_grounder():
    # Create grounder with spine terms
    import spine_ner
    grounder = spine_ner.grounder
    return grounder

def rule_set():
    import rule_gen
    rules = rule_gen.permutations()
    return rules

def stop_words():
    sw_nltk = stopwords.words('english')
    with open('exclude_words.txt', 'r') as file:
        exclude_words = [line.strip() for line in file if line.strip()]
    with open('false_phrases.txt', 'r') as file:
        false_phrases = [line.strip() for line in file if line.strip()]

    excluded = {'stopwords': sw_nltk, 'exclude': exclude_words,
                'false': false_phrases}
    return excluded

def br_rules():
    br_rules = rule_set()['br']

    sw_nltk = stop_words()['stopwords']
    exclude_words = stop_words()['exclude']

    grounder = spine_grounder()

    relations = []

    # Go through each rule and make it a rule object
    for rule_text in tqdm(br_rules):
        rule = Rule("anatomical connection", "Exp", "basic", rule_text)
        # Make sure it is a functional Odinson rule
        try:
            rule_output = process_rules([rule], "http://localhost:9000")

        except Exception as e:
            print('failed', rule)
            print(e)

        # Get the start and end characters for each term pulled out by the rule
        for sentence in rule_output['mentions']:
            relation = ()
            words = sentence['words']
            string_words = ' '.join(words)
            for element in sentence['match']:
                for entity in element['namedCaptures']:
                    start = entity['capturedMatch']['start']
                    end = entity['capturedMatch']['end']
                    # Remove stop words
                    processed_term = [word for word in words[start:end] if
                                      word.lower() not in sw_nltk]
                    word = ' '.join(processed_term)
                    if word.lower() not in exclude_words:
                        # Create tuples with curies for terms that can be grounded
                        spine_scored_match = grounder.ground(word)
                        gilda_scored_match = gilda.ground(word)

                        if len(spine_scored_match) > 0:
                            best_curie = spine_scored_match[0].term.get_curie()
                        elif len(gilda_scored_match) > 0:
                            best_curie = gilda_scored_match[0].term.get_curie()
                        else:
                            best_curie = None

                        if word != '' and best_curie != None:
                            relation += ((best_curie, word),)
            if len(relation) > 1 and relation not in relations and relation[0][
                1] != relation[1][1]:
                relations.append(relation)

    return relations

def br_ph_rules():
    ph_rules = rule_set()['ph']

    sw_nltk = stop_words()['stopwords']
    exclude_words = stop_words()['exclude']

    grounder = spine_grounder()

    ph_relations = []

    # Go through each rule and make it a rule object
    for rule_text in tqdm(ph_rules):
        rule = Rule("phenotype", "Exp", "basic", rule_text)
        # Make sure it is a functional Odinson rule
        try:
            rule_output = process_rules([rule], "http://localhost:9000")

        except Exception as e:
            print('failed', rule)
            print(e)

        # Get the start and end characters for each term pulled out by the rule
        for sentence in rule_output['mentions']:
            relation = ()
            words = sentence['words']
            string_words = ' '.join(words)
            for element in sentence['match']:
                for entity in element['namedCaptures']:
                    start = entity['capturedMatch']['start']
                    end = entity['capturedMatch']['end']
                    # Remove stop words
                    processed_term = [word for word in words[start:end] if
                                      word.lower() not in sw_nltk]
                    word = ' '.join(processed_term)
                    if word.lower() not in exclude_words:
                        # Create tuples with curies for terms that can be grounded
                        spine_scored_match = grounder.ground(word)
                        gilda_scored_match = gilda.ground(word)

                        if len(gilda_scored_match) > 0:
                            best_curie = gilda_scored_match[0].term.get_curie()
                        elif len(spine_scored_match) > 0:
                            best_curie = spine_scored_match[0].term.get_curie()
                        else:
                            best_curie = None

                        if word != '' and best_curie != None:
                            relation += ((best_curie, word),)
            if len(relation) > 1 and relation not in ph_relations and \
                    relation[0][1] != relation[1][1]:
                ph_relations.append(relation)
    return ph_relations

def main():
    '''

    Returns
    -------

    '''

    relations = br_rules()
    print(len(relations))

    ph_relations = br_ph_rules()
    print(len(ph_relations))

if __name__ == "__main__":
    main()


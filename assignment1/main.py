#!usr/bin/env python3
import json
import sys
import os
from difflib import SequenceMatcher
import numpy as np

INPUT_FILE = 'testdata.json' # Constant variables are usually in ALL CAPS

class User:
    def __init__(self, name, gender, preferences, grad_year, responses):
        self.name = name
        self.gender = gender
        self.preferences = preferences
        self.grad_year = grad_year
        self.responses = responses


# Takes in two user objects and outputs a float denoting compatibility
def compute_score(user1, user2):
    demo = dict()# In this dict, I will store information I collect that can impact the score between two people. For instance, 
    # one's gender/gender preferences should somewhat impact their compatibility scores--namely, the score between a pair should be lower if they 
    # do not prefer the other's gender. This will be used ultimately to scale the scores generated from processing the responses. 

    # people who are far apart in grad years may similarly be far apart in age, which decreases compatiblity. Should not find a senior and freshman 
    # compatible. If they are closer in age, I will save it for later!
    if abs(user1.grad_year - user2.grad_year) > 2: 
        return 0
    else:
        demo["age"] = abs(user1.grad_year - user2.grad_year)

    # If the two do not match in gender/gender preferences, then note this in our dict. It is possible that one person's gender does match another's preferences,
    # but the other person's gender does not match the first person's preferences. For this reason, I store gender compatibility for each person separately. 
    if user1.gender == user2.preferences[0]: 
        demo["genderCompat1"] = 1
    else: 
        demo["genderCompat1"] = 0
    if user2.gender == user1.preferences[0]: 
        demo["genderCompat2"] = 1
    else: 
        demo["genderCompat2"] = 0

    # A lot of those "love tester" or "love meter" online games just give a score based on the similarity between names! 
    # I wanted to incorporate that into my scoring function as well using a function called SequenceMatcher which determines similarities between names. 
    demo["nameSim"] = SequenceMatcher(user1.name, user2.name)

    # Now onto the meat of the problem: scoring by the responses. We are asked to normalize our scores across some defined scale. So, I will use cosine 
    # similarity, since it is a similarity metric that scales rom 0 to 1, to score the responses.
    ans1 = user1.responses 
    ans2 = user2.responses
    demo["responses"] = np.dot(ans1,ans2)/(np.linalg.norm(ans1)*np.linalg.norm(ans2))

    # Now, we need to combine all of the information we gathered to provide a general score for the compatibility between two users. 
    demo["finalScore"] = 0

    # We check to see if the two are completely gender incompatible, in which case we return 0; they shouldn't be matched. If one of them is gender compatible, however, 
    # we can continue to provide them a score. The additions to score due to gender compatibility range from 0 to 0.25 
    if demo["genderCompat1"] + demo["genderCompat2"] == 0:
        return 0
    elif demo["genderCompat1"] + demo["genderCompat2"] == 1: 
        demo["finalScore"] += 0.125
    else:
        demo["finalScore"] += 0.25
    
    # We can now incorporate the age differences: Since the largest year gap at a 4-year institution is 3, we can scale the impact of age by 0.1. This factor
    # will range from 0 to 0.03
    demo["finalScore"] += demo["age"]*.01

    # I now incorporate name similarity: the ratio between 0 and 1, and I multiply by 0.2, so it will now range from 0 to 0.8. 
    demo["finalScore"] += demo["nameSim"].ratio()*0.2

    # I now incorporate the responses of the users. The resopnses range from 0 to 1. 
    demo["finalScore"] += demo["responses"]

    # Based on this analysis of the scaling of each of the elements which are used in the score function, my scoring function ranges from 0 to 1.75. 
    return demo["finalScore"]


if __name__ == '__main__':
    # Make sure input file is valid
    if not os.path.exists(INPUT_FILE):
        print('Input file not found')
        sys.exit(0)

    users = []
    with open(INPUT_FILE) as json_file:
        data = json.load(json_file)
        for user_obj in data['users']:
            new_user = User(user_obj['name'], user_obj['gender'],
                            user_obj['preferences'], user_obj['gradYear'],
                            user_obj['responses'])
            users.append(new_user)

    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            user1 = users[i]
            user2 = users[j]
            score = compute_score(user1, user2)
            print('Compatibility between {} and {}: {}'.format(user1.name, user2.name, score))

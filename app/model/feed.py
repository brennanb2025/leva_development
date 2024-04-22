from app.input_sets.models import User, EducationTag, InterestTag, CareerInterestTag, Select, UserFeedWeights
from app import app, db

import app.model.AWS as AWS
import app.model.admin as admin

import json

#search other users heuristic constants
heuristicVals = {} #how much to weight matching attributes
heuristicVals["education"] = 20     #2 matching schools - weight at +10
heuristicVals["career"] = 45       #career interest
heuristicVals["interest"] = 15      #personal interest
heuristicVals["personality"] = 10
#heuristicVals["division_pref"] = 0
heuristicVals["gender_pref"] = 10 


class match_suggestion:
    def __init__(self):
        self.mentor = None
        self.mentorInterestMatches = []
        self.mentorCareerMatches = []
        self.mentorEducationMatches = []
        self.mentorGenderPreferenceMatching = False
        self.personalityMatches = []
        self.score = None

class match_suggested_response:
    def __init__(self):
        self.userId = None
        self.matches = [] #list of match_suggestions


#OBJECT VERSION (NOT WORKING)
#TODO test for >1 pairing (changed, not tested)
def feedMenteeNew(userId):
    """
    Comment about efficiency:
    Right now how this works is it:
    1. Gets all the users with a matching school
    2. Gets all the users with a matching interest
    3. Gets all the users with a matching career interest
    4. Sorts based on how many times the user shows up in steps 1,2,3 (with heuristic weights)
    5. Returns all of the users from that sorted list.
    There's not really a point in returning only the top 10 users instead of all of them. 
    It appears that I can't avoid getting the users from all 3 of the columns, since I can't rule out any users before I see how 
        many matches they have in EACH column. Like what if one user does not go to the same school but has 100 of the same interests?
        I have to look at the interest column in order to determine that.
    """
    
    user = User.query.filter_by(id=userId).first()
    if user == None:
        return

    userDict = {} #user : number match.
    matches = {} #for data logging
    #matches["division_pref"] = 0
    matches["personality"] = 0
    matches["education"] = 0
    matches["career"] = 0
    matches["interest"] = 0

    #get all mentors in the same business as the user. is_student should remove the user themself from the query.
    potentialUsers = User.query.filter_by(business_id=user.business_id).filter_by(is_student=False).all()

    users = []
    for u in potentialUsers:
        if mentorAvailable(u.id): #only select users that have not already been chosen.
            users.append(u)

    for u in users: #initialize user dictionary
        userDict[u] = 0
        #initialize as 0

    #check gender preference/identity
    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #only check if flag for gender/identity is "True"
        for u in users: #initialize user dictionary
            if (user.mentor_gender_preference == "male" and u.gender_identity == "male") or (user.mentor_gender_preference == "female" and u.gender_identity == "female"):
                #matching gender preference / gender
                userDict[u] = heuristicVals["gender_pref"]
            #ignore case mentor gender preference == "noPreference".


    #Commented out division preferences
    """
    #division preferences
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #only check if flag for division preference is "True"
        for u in users:
            if (u.division_preference == "same" and user.division == u.division) or u.division_preference == "noPreference":
                #other user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
            if (user.division_preference == "same" and user.division == u.division) or user.division_preference == "noPreference":
                #this user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
    """

    #personality
    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        for u in users:
            #match in any personality trait - separate to add to the value per each match.
            if u.personality_1 in user.personality_1 or user.personality_1 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_1 in user.personality_2 or user.personality_2 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_1 in user.personality_3 or user.personality_3 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_2 in user.personality_2 or user.personality_2 in u.personality_2:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_2 in user.personality_3 or user.personality_3 in u.personality_2:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_3 in user.personality_3 or user.personality_3 in u.personality_3:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
    

    schoolDict = {} #contains all the matching schools for each user (user : [school])
    thisUserEducationTagIDs = user.rtn_education()
    thisUserEducationTagIDs = [edu.id for edu in thisUserEducationTagIDs] #get the ids

    for u in users:
        for educ in u.rtn_education(): #cycle thru each user education
            educationTags = EducationTag.query.filter_by(educationID=educ.educationID).all()
            for edTag in educationTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if edTag.id in thisUserEducationTagIDs:
                    if u in schoolDict: #add user to the dict
                        schoolDict[u].append(edTag.entered_name)
                    else:
                        sArr = [edTag.entered_name] #not already in the dict --> add a new array
                        schoolDict[u] = sArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["education"]
                    matches["education"] += 1


    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    thisUserInterestTagIDs = user.rtn_interests()
    thisUserInterestTagIDs = [intrst.id for intrst in thisUserInterestTagIDs] #get the ids

    for u in users:
        for intrst in u.rtn_interests(): #cycle thru each user education
            interestTags = InterestTag.query.filter_by(interestID=intrst.interestID).all()
            for intT in interestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if intT.id in thisUserInterestTagIDs:
                    if u in interestTitleDict: #add user to the dict
                        interestTitleDict[u].append(intT.entered_name)
                    else:
                        iArr = [intT.entered_name] #not already in the dict --> add a new array
                        interestTitleDict[u] = iArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["interest"]
                    matches["interest"] += 1


    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    thisUserCareerInterestIDs = user.rtn_career_interests()
    thisUserCareerInterestIDs = [cInt.id for cInt in thisUserCareerInterestIDs] #get the ids

    for u in users:
        for cInt in u.rtn_career_interests(): #cycle thru each user education
            careerInterestTags = CareerInterestTag.query.filter_by(careerInterestID=cInt.careerInterestID).all()
            for cInt in careerInterestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if cInt.id in thisUserCareerInterestIDs:
                    if u in careerDict: #add user to the dict
                        careerDict[u].append(cInt.entered_name)
                    else:
                        cArr = [cInt.entered_name] #not already in the dict --> add a new array
                        careerDict[u] = cArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["career"]
                    matches["career"] += 1


    #sortedDict = sorted(userDict.items(), key=lambda item: item[1], reverse=True) #is now a list of tuples
    #sort userDict by value (the number of matches it got in the db.)

    #userDictUsefulInfo = {} # { user : { match name : [ matches for this user ] } }
    
    resp = match_suggested_response()
    matchSuggestions = []
    for u in userDict.keys():

        matchSuggestion = match_suggestion()
        matchSuggestion.mentor = u
        matchSuggestion.mentorInterestMatches = interestTitleDict[u] if u in interestTitleDict else []
        matchSuggestion.mentorCareerMatches = careerDict[u] if u in careerDict else []
        matchSuggestion.mentorEducationMatchesMatches = schoolDict[u] if u in schoolDict else []
        matchSuggestion.score = userDict[u]

        matchSuggestions.append(matchSuggestion)


    resp.userId = user.id
    resp.matches = matchSuggestions
    return resp


#TESTING, make it work w/ objects!
#TODO make work for >1 pairing (changed, not tested)
def feedMentee(userId):
    """
    Comment about efficiency:
    Right now how this works is it:
    1. Gets all the users with a matching school
    2. Gets all the users with a matching interest
    3. Gets all the users with a matching career interest
    4. Sorts based on how many times the user shows up in steps 1,2,3 (with heuristic weights)
    5. Returns all of the users from that sorted list.
    There's not really a point in returning only the top 10 users instead of all of them. 
    It appears that I can't avoid getting the users from all 3 of the columns, since I can't rule out any users before I see how 
        many matches they have in EACH column. Like what if one user does not go to the same school but has 100 of the same interests?
        I have to look at the interest column in order to determine that.
    """
    
    user = User.query.filter_by(id=userId).first()
    if user == None:
        return

    thisUserWeights = UserFeedWeights.query.filter_by(user_id=user.id).first()
    # apply weights.
    # high-high = normal weight.
    # high-low = 0.75x
    # low-low = 0.5x
    potentialUserWeights = {}

    userDict = {} #user : number match.
    matches = {} #for data logging
    #matches["division_pref"] = 0
    matches["personality"] = 0
    matches["education"] = 0
    matches["career"] = 0
    matches["interest"] = 0

    #get all mentors in the same business as the user. is_student should remove the user themself from the query.
    potentialUsers = User.query.filter_by(business_id=user.business_id).filter_by(is_student=False).all()

    users = []
    for u in potentialUsers:
        if mentorAvailable(u.id): #only select users that have not already been chosen.
            users.append(u)

    for u in users: #initialize user dictionary
        userDict[u] = 0 #initialize as 0
        uWeights = UserFeedWeights.query.filter_by(user_id=u.id).first()
        if uWeights:
            potentialUserWeights[u.id] = uWeights

    #check gender preference/identity
    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #only check if flag for gender/identity is "True"
        for u in users: #initialize user dictionary
            if (user.mentor_gender_preference == "male" and u.gender_identity == "male") or (user.mentor_gender_preference == "female" and u.gender_identity == "female"):
                #matching gender preference / gender
                if thisUserWeights and thisUserWeights.mentor_gender_preference:
                    if thisUserWeights.mentor_gender_preference == 0: # low
                        userDict[u] = 0.5 * heuristicVals["gender_pref"]
                    elif thisUserWeights.mentor_gender_preference == 1: # indifferent
                        userDict[u] = 0.75 * heuristicVals["gender_pref"]
                    else: # high
                        userDict[u] = heuristicVals["gender_pref"]
                else:
                    userDict[u] = heuristicVals["gender_pref"]
            #ignore case mentor gender preference == "noPreference".


    #division preferences
    """
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #only check if flag for division preference is "True"
        for u in users:
            if (u.division_preference == "same" and user.division == u.division) or u.division_preference == "noPreference":
                #other user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
            if (user.division_preference == "same" and user.division == u.division) or user.division_preference == "noPreference":
                #this user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
    """

    #TODO Added u.personality_n and before all to test if None before asking if in. Update the above to do the same.
    #personality
    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        for u in users:
            sumPersonalityMatches = 0
            #match in any personality trait - separate to add to the value per each match.
            if (u.personality_1 and user.personality_1) and (u.personality_1 in user.personality_1 or user.personality_1 in u.personality_1):
                sumPersonalityMatches += 1
                matches["personality"] += 1
            if (u.personality_1 and user.personality_2) and (u.personality_1 in user.personality_2 or user.personality_2 in u.personality_1):
                sumPersonalityMatches += 1
                matches["personality"] += 1
            if (u.personality_1 and user.personality_3) and (u.personality_1 in user.personality_3 or user.personality_3 in u.personality_1):
                sumPersonalityMatches += 1
                matches["personality"] += 1
            if (u.personality_2 and user.personality_2) and (u.personality_2 in user.personality_2 or user.personality_2 in u.personality_2):
                sumPersonalityMatches += 1
                matches["personality"] += 1
            if (u.personality_2 and user.personality_3) and (u.personality_2 in user.personality_3 or user.personality_3 in u.personality_2):
                sumPersonalityMatches += 1
                matches["personality"] += 1
            if (u.personality_3 and user.personality_3) and (u.personality_3 in user.personality_3 or user.personality_3 in u.personality_3):
                sumPersonalityMatches += 1
                matches["personality"] += 1

            weights = potentialUserWeights.get(userId, None)
            if (thisUserWeights and weights) and thisUserWeights.personality and weights.personality:
                if weights.personality == thisUserWeights.personality == 0: # low-low: 0.5x points
                    userDict[u] += 0.5 * (sumPersonalityMatches / 6) * heuristicVals["personality"]
                elif weights.personality != thisUserWeights.personality: # high-low: 0.75x points
                    userDict[u] += 0.75 * (sumPersonalityMatches / 6) * heuristicVals["personality"]
            else:
                userDict[u] += (sumPersonalityMatches / 6) * heuristicVals["personality"]

                # divided by 6 because 6 personality traits total.

    
    schoolDict = {} #contains all the matching schools for each user (user : [school])
    thisUserEducationTagIDs = user.rtn_education()
    thisUserEducationTagIDs = [edu.id for edu in thisUserEducationTagIDs] #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserEducation = u.rtn_education()
        totalNumberOfEducation = len(thisUserEducationTagIDs) + len(potentialUserEducation)
        numberOfEducationMatches = 0
        
        for educ in potentialUserEducation: #cycle thru each user education
            educationTags = EducationTag.query.filter_by(educationID=educ.educationID).all()
            for edTag in educationTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if edTag.id in thisUserEducationTagIDs:
                    if u in schoolDict: #add user to the dict
                        schoolDict[u].append(edTag.entered_name)
                    else:
                        sArr = [edTag.entered_name] #not already in the dict --> add a new array
                        schoolDict[u] = sArr

                    numberOfEducationMatches += 1

        educationPercentMatches = numberOfEducationMatches / totalNumberOfEducation
        #now update match amount in user dict
        if (thisUserWeights and weights) and thisUserWeights.education and weights.education:
            if weights.education == thisUserWeights.education == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * educationPercentMatches * heuristicVals["education"]
            elif weights.education != thisUserWeights.education: # high-low: 0.75x points
                userDict[u] += 0.75 * educationPercentMatches * heuristicVals["education"]
        else:
            userDict[u] += educationPercentMatches * heuristicVals["education"]
        matches["education"] += numberOfEducationMatches


    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    thisUserInterestTagIDs = user.rtn_interests()
    thisUserInterestTagIDs = [intrst.id for intrst in thisUserInterestTagIDs] #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserInterests = u.rtn_interests()
        totalNumberOfInterests = len(thisUserInterestTagIDs) + len(potentialUserInterests)
        numberOfInterestMatches = 0
        for intrst in potentialUserInterests: #cycle thru each user interest
            interestTags = InterestTag.query.filter_by(interestID=intrst.interestID).all()
            for intT in interestTags: #go thru all the interestTags (the ones related to each user ans unique to each input)
                if intT.id in thisUserInterestTagIDs:
                    if u in interestTitleDict: #add user to the dict
                        interestTitleDict[u].append(intT.entered_name)
                    else:
                        iArr = [intT.entered_name] #not already in the dict --> add a new array
                        interestTitleDict[u] = iArr

                    numberOfInterestMatches += 1 
                    
        interestPercentMatches = numberOfInterestMatches / totalNumberOfInterests
        if (thisUserWeights and weights) and thisUserWeights.interests and weights.interests:
            if weights.interests == thisUserWeights.interests == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * interestPercentMatches * heuristicVals["interest"]
            elif weights.interests != thisUserWeights.interests: # high-low: 0.75x points
                userDict[u] += 0.75 * interestPercentMatches * heuristicVals["interest"]
        else:
            userDict[u] += interestPercentMatches * heuristicVals["interest"]
        
        matches["interest"] += numberOfInterestMatches


    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    thisUserCareerInterestIDs = user.rtn_career_interests()
    thisUserCareerInterestIDs = [cInt.id for cInt in thisUserCareerInterestIDs] #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserCareerInterests = u.rtn_career_interests()
        totalNumberOfCareerInterests = len(thisUserCareerInterestIDs) + len(potentialUserCareerInterests)
        numberOfCareerInterestMatches = 0

        for cInt in potentialUserCareerInterests: #cycle thru each
            careerInterestTags = CareerInterestTag.query.filter_by(careerInterestID=cInt.careerInterestID).all()
            for cInt in careerInterestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if cInt.id in thisUserCareerInterestIDs:
                    if u in careerDict: #add user to the dict
                        careerDict[u].append(cInt.entered_name)
                    else:
                        cArr = [cInt.entered_name] #not already in the dict --> add a new array
                        careerDict[u] = cArr

                    numberOfCareerInterestMatches += 1 
                    
        careerInterestPercentMatches = numberOfCareerInterestMatches / totalNumberOfCareerInterests
        if (thisUserWeights and weights) and thisUserWeights.career_interests and weights.career_interests:
            if weights.career_interests == thisUserWeights.career_interests == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * careerInterestPercentMatches * heuristicVals["career"]
            elif weights.career_interests != thisUserWeights.career_interests: # high-low: 0.75x points
                userDict[u] += 0.75 * careerInterestPercentMatches * heuristicVals["career"]
        else:
            userDict[u] += careerInterestPercentMatches * heuristicVals["career"]

        matches["career"] += numberOfCareerInterestMatches


    sortedDict = sorted(userDict.items(), key=lambda item: item[1], reverse=True) #is now a list of tuples
    #sort userDict by value (the number of matches it got in the db.)

    userDictUsefulInfo = {} # { user : { match name : [ matches for this user ] } }
    
    for u in userDict.keys():

        usefulInfo = {}
        usefulInfo['userFn'] = u.first_name
        usefulInfo['userLn'] = u.last_name
        usefulInfo['userBio'] = u.bio
        usefulInfo['userProfilePicture'] = u.profile_picture
        usefulInfo['userIntroVideo'] = u.intro_video
        usefulInfo['userCurrentOccupation'] = u.current_occupation
        usefulInfo['userIsStudent'] = u.is_student
        usefulInfo['resumeURL'] = AWS.create_resume_link(u)
        usefulInfo['score'] = userDict[u]

        
        #so there is probably a better way of doing this without making two dicts but I'll implement that later
        if interestTitleDict.__contains__(u):
            usefulInfo['interest matches'] = interestTitleDict[u]
        else:
            usefulInfo['interest matches'] = [] #if no matches, empty array.

        if careerDict.__contains__(u):
            usefulInfo['career matches'] = careerDict[u]
        else:
            usefulInfo['career matches'] = [] #if no matches, empty array.

        if schoolDict.__contains__(u):
            usefulInfo['school matches'] = schoolDict[u]
        else:
            usefulInfo['school matches'] = [] #if no matches, empty array.

        userDictUsefulInfo[str(u.id)] = usefulInfo


    rtnUserArr = [] #array of the users (sorted, unlike the dict)
    for tup in sortedDict: #(key,value)
        rtnUserArr.append(tup[0].id)

    dictItems = {}
    dictItems['userDictUsefulInfo'] = userDictUsefulInfo
    dictItems['userArr'] = rtnUserArr
    
    dictLog = {}
    dictLog["numMatches"] = len(userDict.keys())
    dictLog["sortedWeights"] = [tup[1] for tup in sortedDict]
    dictLog["sortedUserIDs"] = [tup[0].id for tup in sortedDict]
    dictLog["matches"] = matches #nested json object

    #admin.logData(13,json.dumps(dictLog)) #log feed get

    return dictItems



def mentorSelected(mentorId): #if this mentor has been selected already
    return Select.query.filter_by(mentor_id=mentorId).first() != None


def mentorAvailable(mentorId): #if this mentor has free spots for mentees (even if already matched)
    mentor = User.query.filter_by(id=mentorId).first()
    if mentor is None:
        return False

    mentorMatches = Select.query.filter_by(mentor_id=mentorId).all()
    if mentorMatches is None: #haven't made a match yet --> must be free
        return True

    if mentor.num_pairings_can_make is None:
        #just in case mentor did not have the option to allow for >1 mentee: can only make 1 
        return mentorMatches == []
    
    #can have 2 mentees, made 1 match, can make 1 more.
    #can have 2 mentees, made 2 matches, can't make another one.
    return len(mentorMatches) < mentor.num_pairings_can_make

def menteeAvailable(menteeId): #if this mentee has free spots for mentors (even if already matched)
    mentee = User.query.filter_by(id=menteeId).first()
    if mentee is None:
        return False
    menteeMatches = Select.query.filter_by(mentee_id=menteeId).all()
    if menteeMatches is None: #haven't made a match yet --> must be free
        return True

    if mentee.num_pairings_can_make is None: 
        #just in case mentor did not have the option to allow for >1 mentee: can only make 1 
        return menteeMatches == []
    
    #can have 2 mentees, made 1 match, can make 1 more.
    #can have 2 mentees, made 2 matches, can't make another one.
    return len(menteeMatches) < mentee.num_pairings_can_make



#TODO test for >1 pairing
def feedPost(userId, userMatchID):
    if not menteeAvailable(userId) or not mentorAvailable(userMatchID):
        return False #one of them is unavailable

    newSelect = Select(mentee_id=userId, mentor_id=userMatchID)
    #selection will only be made by the user logged in - the mentee.

    db.session.add(newSelect)
    db.session.commit()
    print("successfully made new selection with", User.query.filter_by(id=userMatchID).first())

    return True



def get_all_matches(userId):
    """
    Comment about efficiency:
    Right now how this works is it:
    1. Gets all the users with a matching school
    2. Gets all the users with a matching interest
    3. Gets all the users with a matching career interest
    4. Sorts based on how many times the user shows up in steps 1,2,3 (with heuristic weights)
    5. Returns all of the users from that sorted list.
    There's not really a point in returning only the top 10 users instead of all of them. 
    It appears that I can't avoid getting the users from all 3 of the columns, since I can't rule out any users before I see how 
        many matches they have in EACH column. Like what if one user does not go to the same school but has 100 of the same interests?
        I have to look at the interest column in order to determine that.
    """
    
    user = User.query.filter_by(id=userId).first()
    if user == None:
        return

    userDict = {} #user : number match.
    matches = {} #for data logging
    #matches["division_pref"] = 0
    matches["personality"] = 0
    matches["education"] = 0
    matches["career"] = 0
    matches["interest"] = 0

    #get all mentors in the same business as the user. is_student should remove the user themself from the query.
    users = User.query.filter_by(business_id=user.business_id).filter_by(is_student=False).all()
    
    """
    users = []
    for u in potentialUsers:
        if mentorAvailable(u.id): #only select users that have not already been chosen.
            users.append(u)
    """

    for u in users: #initialize user dictionary
        userDict[u] = 0
        #initialize as 0

    #check gender preference/identity
    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #only check if flag for gender/identity is "True"
        for u in users: #initialize user dictionary
            if (user.mentor_gender_preference == "male" and u.gender_identity == "male") or (user.mentor_gender_preference == "female" and u.gender_identity == "female"):
                #matching gender preference / gender
                userDict[u] = heuristicVals["gender_pref"]
            #ignore case mentor gender preference == "noPreference".


    #commented out
    """
    #division preferences
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #only check if flag for division preference is "True"
        for u in users:
            if (u.division_preference == "same" and user.division == u.division) or u.division_preference == "noPreference":
                #other user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
            if (user.division_preference == "same" and user.division == u.division) or user.division_preference == "noPreference":
                #this user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
    """

    #personality
    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        for u in users:
            #match in any personality trait - separate to add to the value per each match.
            if (u.personality_1 and user.personality_1) and (u.personality_1 in user.personality_1 or user.personality_1 in u.personality_1):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if (u.personality_1 and user.personality_2) and (u.personality_1 in user.personality_2 or user.personality_2 in u.personality_1):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if (u.personality_1 and user.personality_3) and (u.personality_1 in user.personality_3 or user.personality_3 in u.personality_1):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if (u.personality_2 and user.personality_2) and (u.personality_2 in user.personality_2 or user.personality_2 in u.personality_2):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if (u.personality_2 and user.personality_3) and (u.personality_2 in user.personality_3 or user.personality_3 in u.personality_2):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if (u.personality_3 and user.personality_3) and (u.personality_3 in user.personality_3 or user.personality_3 in u.personality_3):
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
    

    schoolDict = {} #contains all the matching schools for each user (user : [school])
    thisUserEducationTagIDs = user.rtn_education()
    thisUserEducationTagIDs = [edu.id for edu in thisUserEducationTagIDs] #get the ids

    for u in users:
        for educ in u.rtn_education(): #cycle thru each user education
            educationTags = EducationTag.query.filter_by(educationID=educ.educationID).all()
            for edTag in educationTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if edTag.id in thisUserEducationTagIDs:
                    if u in schoolDict: #add user to the dict
                        schoolDict[u].append(edTag.entered_name)
                    else:
                        sArr = [edTag.entered_name] #not already in the dict --> add a new array
                        schoolDict[u] = sArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["education"]
                    matches["education"] += 1


    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    thisUserInterestTagIDs = user.rtn_interests()
    thisUserInterestTagIDs = [intrst.id for intrst in thisUserInterestTagIDs] #get the ids

    for u in users:
        for intrst in u.rtn_interests(): #cycle thru each user education
            interestTags = InterestTag.query.filter_by(interestID=intrst.interestID).all()
            for intT in interestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if intT.id in thisUserInterestTagIDs:
                    if u in interestTitleDict: #add user to the dict
                        interestTitleDict[u].append(intT.entered_name)
                    else:
                        iArr = [intT.entered_name] #not already in the dict --> add a new array
                        interestTitleDict[u] = iArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["interest"]
                    matches["interest"] += 1


    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    thisUserCareerInterestIDs = user.rtn_career_interests()
    thisUserCareerInterestIDs = [cInt.id for cInt in thisUserCareerInterestIDs] #get the ids

    for u in users:
        for cInt in u.rtn_career_interests(): #cycle thru each user education
            careerInterestTags = CareerInterestTag.query.filter_by(careerInterestID=cInt.careerInterestID).all()
            for cInt in careerInterestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if cInt.id in thisUserCareerInterestIDs:
                    if u in careerDict: #add user to the dict
                        careerDict[u].append(cInt.entered_name)
                    else:
                        cArr = [cInt.entered_name] #not already in the dict --> add a new array
                        careerDict[u] = cArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["career"]
                    matches["career"] += 1


    #sortedDict = sorted(userDict.items(), key=lambda item: item[1], reverse=True) #is now a list of tuples
    #sort userDict by value (the number of matches it got in the db.)

    #userDictUsefulInfo = {} # { user : { match name : [ matches for this user ] } }
    
    resp = match_suggested_response()
    matchSuggestions = []
    for u in userDict.keys():

        matchSuggestion = match_suggestion()
        matchSuggestion.mentor = u
        matchSuggestion.mentorInterestMatches = interestTitleDict[u] if u in interestTitleDict else []
        matchSuggestion.mentorCareerMatches = careerDict[u] if u in careerDict else []
        matchSuggestion.mentorEducationMatchesMatches = schoolDict[u] if u in schoolDict else []
        matchSuggestion.score = userDict[u]

        matchSuggestions.append(matchSuggestion)

    resp.userId = user.id
    resp.matches = matchSuggestions
    return resp


#TESTING, make it work w/ objects!
#TODO make work for >1 pairing (changed, not tested)
def get_all_matches_feedWeights(userId):
    """
    Comment about efficiency:
    Right now how this works is it:
    1. Gets all the users with a matching school
    2. Gets all the users with a matching interest
    3. Gets all the users with a matching career interest
    4. Sorts based on how many times the user shows up in steps 1,2,3 (with heuristic weights)
    5. Returns all of the users from that sorted list.
    There's not really a point in returning only the top 10 users instead of all of them. 
    It appears that I can't avoid getting the users from all 3 of the columns, since I can't rule out any users before I see how 
        many matches they have in EACH column. Like what if one user does not go to the same school but has 100 of the same interests?
        I have to look at the interest column in order to determine that.
    """
    
    user = User.query.filter_by(id=userId).first()
    if user == None:
        return

    thisUserWeights = UserFeedWeights.query.filter_by(user_id=user.id).first()
    # apply weights.
    # high-high = normal weight.
    # high-low = 0.75x
    # low-low = 0.5x
    potentialUserWeights = {}

    userDict = {} #user : number match.
    #matches = {} #for data logging (removed)
    #matches["division_pref"] = 0
    #matches["personality"] = 0
    #matches["education"] = 0
    #matches["career"] = 0
    #matches["interest"] = 0

    #get all mentors in the same business as the user. is_student should remove the user themself from the query.
    users = User.query.filter_by(business_id=user.business_id).filter_by(is_student=False).all()

    for u in users: #initialize user dictionary
        userDict[u] = 0 #initialize as 0
        uWeights = UserFeedWeights.query.filter_by(user_id=u.id).first()
        if uWeights:
            potentialUserWeights[u.id] = uWeights

    hasDesiredGenders = {}

    #check gender preference/identity
    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #only check if flag for gender/identity is "True"
        for u in users: #initialize user dictionary
            if user.mentor_gender_preference == "noPreference" or (user.mentor_gender_preference == "male" and u.gender_identity == "male") or (user.mentor_gender_preference == "female" and u.gender_identity == "female"):
                #matching gender preference / gender (or mentee has no preferece)
                hasDesiredGenders[u] = True
                if thisUserWeights:
                    if thisUserWeights.mentor_gender_preference == 0: # low
                        userDict[u] = 0.5 * heuristicVals["gender_pref"]
                    elif thisUserWeights.mentor_gender_preference == 1: # indifferent
                        userDict[u] = 0.75 * heuristicVals["gender_pref"]
                    else: # high
                        userDict[u] = heuristicVals["gender_pref"]
                else:
                    userDict[u] = heuristicVals["gender_pref"]
            
            #ignore case mentor gender preference == "noPreference".


    #division preferences
    """
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #only check if flag for division preference is "True"
        for u in users:
            if (u.division_preference == "same" and user.division == u.division) or u.division_preference == "noPreference":
                #other user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
            if (user.division_preference == "same" and user.division == u.division) or user.division_preference == "noPreference":
                #this user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
    """

    #TODO Added u.personality_n and before all to test if None before asking if in. Update the above to do the same.
    #personality

    personalityDict = dict((u.id, set()) for u in users) # set - no duplicates

    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        for u in users:
            sumPersonalityMatches = 0
            #match in any personality trait - separate to add to the value per each match.
            if (u.personality_1 and user.personality_1) and (u.personality_1 in user.personality_1 or user.personality_1 in u.personality_1):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_1)
                personalityDict[u.id].add(user.personality_1)
                #matches["personality"] += 1
            if (u.personality_1 and user.personality_2) and (u.personality_1 in user.personality_2 or user.personality_2 in u.personality_1):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_1)
                personalityDict[u.id].add(user.personality_2)
                #matches["personality"] += 1
            if (u.personality_1 and user.personality_3) and (u.personality_1 in user.personality_3 or user.personality_3 in u.personality_1):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_1)
                personalityDict[u.id].add(user.personality_3)
                #matches["personality"] += 1
            if (u.personality_2 and user.personality_2) and (u.personality_2 in user.personality_2 or user.personality_2 in u.personality_2):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_2)
                personalityDict[u.id].add(user.personality_2)
                #matches["personality"] += 1
            if (u.personality_2 and user.personality_3) and (u.personality_2 in user.personality_3 or user.personality_3 in u.personality_2):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_2)
                personalityDict[u.id].add(user.personality_3)
                #matches["personality"] += 1
            if (u.personality_3 and user.personality_3) and (u.personality_3 in user.personality_3 or user.personality_3 in u.personality_3):
                sumPersonalityMatches += 1
                personalityDict[u.id].add(u.personality_3)
                personalityDict[u.id].add(user.personality_3)
                #matches["personality"] += 1

            weights = potentialUserWeights.get(userId, None)
            if thisUserWeights and weights:
                if weights.personality == thisUserWeights.personality == 0: # low-low: 0.5x points
                    userDict[u] += 0.5 * (sumPersonalityMatches / 6) * heuristicVals["personality"]
                elif weights.personality != thisUserWeights.personality: # high-low: 0.75x points
                    userDict[u] += 0.75 * (sumPersonalityMatches / 6) * heuristicVals["personality"]
            else:
                userDict[u] += (sumPersonalityMatches / 6) * heuristicVals["personality"]

                # divided by 6 because 6 personality traits total.

    
    schoolDict = {} #contains all the matching schools for each user (user : [school])
    thisUserEducationTagIDs = set(edu.id for edu in user.rtn_education()) #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserEducation = u.rtn_education()
        totalNumberOfEducation = len(thisUserEducationTagIDs) + len(potentialUserEducation)
        numberOfEducationMatches = 0
        
        for educ in potentialUserEducation: #cycle thru each user education
            educationTags = EducationTag.query.filter_by(educationID=educ.educationID).all()
            for edTag in educationTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if edTag.id in thisUserEducationTagIDs:
                    if u in schoolDict: #add user to the dict
                        schoolDict[u].append(edTag.entered_name)
                    else:
                        sArr = [edTag.entered_name] #not already in the dict --> add a new array
                        schoolDict[u] = sArr

                    numberOfEducationMatches += 1

        educationPercentMatches = numberOfEducationMatches / totalNumberOfEducation
        #now update match amount in user dict

        if thisUserWeights and weights:
            if weights.education == thisUserWeights.education == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * educationPercentMatches * heuristicVals["education"]
            elif weights.education != thisUserWeights.education: # high-low: 0.75x points
                userDict[u] += 0.75 * educationPercentMatches * heuristicVals["education"]
        else:
            userDict[u] += educationPercentMatches * heuristicVals["education"]
        #matches["education"] += numberOfEducationMatches

    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    thisUserInterestTagIDs = user.rtn_interests()
    thisUserInterestTagIDs = [intrst.id for intrst in thisUserInterestTagIDs] #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserInterests = u.rtn_interests()
        totalNumberOfInterests = len(thisUserInterestTagIDs) + len(potentialUserInterests)
        numberOfInterestMatches = 0
        for intrst in potentialUserInterests: #cycle thru each user interest
            interestTags = InterestTag.query.filter_by(interestID=intrst.interestID).all()
            for intT in interestTags: #go thru all the interestTags (the ones related to each user ans unique to each input)
                if intT.id in thisUserInterestTagIDs:
                    if u in interestTitleDict: #add user to the dict
                        interestTitleDict[u].append(intT.entered_name)
                    else:
                        iArr = [intT.entered_name] #not already in the dict --> add a new array
                        interestTitleDict[u] = iArr

                    numberOfInterestMatches += 1 
                    
        interestPercentMatches = numberOfInterestMatches / totalNumberOfInterests
        if thisUserWeights and weights:
            if weights.interests == thisUserWeights.interests == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * interestPercentMatches * heuristicVals["interest"]
            elif weights.interests != thisUserWeights.interests: # high-low: 0.75x points
                userDict[u] += 0.75 * interestPercentMatches * heuristicVals["interest"]
        else:
            userDict[u] += interestPercentMatches * heuristicVals["interest"]
        
        #matches["interest"] += numberOfInterestMatches


    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    thisUserCareerInterestIDs = user.rtn_career_interests()
    thisUserCareerInterestIDs = [cInt.id for cInt in thisUserCareerInterestIDs] #get the ids

    for u in users:
        weights = potentialUserWeights.get(u.id, None)
        potentialUserCareerInterests = u.rtn_career_interests()
        totalNumberOfCareerInterests = len(thisUserCareerInterestIDs) + len(potentialUserCareerInterests)
        numberOfCareerInterestMatches = 0

        for cInt in potentialUserCareerInterests: #cycle thru each
            careerInterestTags = CareerInterestTag.query.filter_by(careerInterestID=cInt.careerInterestID).all()
            for cInt in careerInterestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if cInt.id in thisUserCareerInterestIDs:
                    if u in careerDict: #add user to the dict
                        careerDict[u].append(cInt.entered_name)
                    else:
                        cArr = [cInt.entered_name] #not already in the dict --> add a new array
                        careerDict[u] = cArr

                    numberOfCareerInterestMatches += 1 
                    
        careerInterestPercentMatches = numberOfCareerInterestMatches / totalNumberOfCareerInterests
        if thisUserWeights and weights:
            if weights.career_interests == thisUserWeights.career_interests == 0: # low-low: 0.5x points
                userDict[u] += 0.5 * careerInterestPercentMatches * heuristicVals["career"]
            elif weights.career_interests != thisUserWeights.career_interests: # high-low: 0.75x points
                userDict[u] += 0.75 * careerInterestPercentMatches * heuristicVals["career"]
        else:
            userDict[u] += careerInterestPercentMatches * heuristicVals["career"]

        #matches["career"] += numberOfCareerInterestMatches


    resp = match_suggested_response()
    matchSuggestions = []
    for u in userDict.keys():

        matchSuggestion = match_suggestion()
        matchSuggestion.mentor = u
        matchSuggestion.mentorInterestMatches = interestTitleDict[u] if u in interestTitleDict else []
        matchSuggestion.mentorCareerMatches = careerDict[u] if u in careerDict else []
        matchSuggestion.mentorEducationMatches = schoolDict[u] if u in schoolDict else []
        matchSuggestion.score = userDict[u]
        matchSuggestion.mentorGenderPreferenceMatching = True if u in hasDesiredGenders else False
        matchSuggestion.personalityMatches = list(personalityDict[u.id])

        matchSuggestions.append(matchSuggestion)

    resp.userId = user.id
    resp.matches = matchSuggestions
    return resp
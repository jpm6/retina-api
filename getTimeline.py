from bson import json_util
import pymongo, json, time
from datetime import datetime
from dbco import *

def getKeywordTimeline(keyword, daysLoad, bucketNumber=100):

    startTime = time.time() - int(daysLoad)* 24 * 3600
    endTime = time.time()
    bucketSize = int((endTime - startTime) / bucketNumber)
    
    match = {'$match': {'timestamp': {'$gte': startTime, '$lt': endTime}, 'keywords': keyword}}
    project = {'$project': {'tsMod': {'$subtract': ['$timestamp', {'$mod': ['$timestamp', bucketSize]}]}}}
    
    group = {'$group': {'_id': '$tsMod', 'count': {'$sum': 1}}}
    sort = {'$sort': {'_id': 1}}
    
    pipeline = [match, project, group, sort]
    return returnObj(list(db.qdoc.aggregate(pipeline)), startTime, endTime, bucketSize)

def getKeywordTweetTimeline(keyword, daysLoad, bucketNumber=100):

    startTime = time.time() - int(daysLoad)* 24 * 3600; endTime = time.time()
    bucketSize = int((endTime - startTime) / bucketNumber)

    match = {'$match': {'timestamp': {'$gte': startTime, '$lt': endTime}, 'words': keyword}}
    project = {'$project': {'tsMod': {'$subtract': ['$timestamp', {'$mod': ['$timestamp', bucketSize]}]}}}
    group = {'$group': {'_id': '$tsMod', 'count': {'$sum': 1}}}
    sort = {'$sort': {'_id': 1}}
    
    pipeline = [match, project, group, sort]
    return returnObj(list(db.tweet.aggregate(pipeline)), startTime, endTime, bucketSize)

def topicTimeline(topic, bucketNumber=50):
    topic = int(topic);
    matchTopic = {'$match': {'topic': topic}}

    groupToFindRange = {'$group': {'_id': None, 'minTimestamp': {'$min': '$timestamp'}, 'maxTimestamp': {'$max': '$timestamp'}}}
    timeinfo = list(db.qdoc.aggregate([matchTopic,groupToFindRange]))[0]
    startTime = timeinfo['minTimestamp']; endTime = timeinfo['maxTimestamp']
    bucketSize = int((endTime - startTime) / bucketNumber)
    
    matchTimestamp = {'$match': {'timestamp': {'$gte': startTime, '$lt': endTime}}}
    project = {'$project': {'title': True, 'timestamp': True, 'tsMod': {'$subtract': ['$timestamp', {'$mod': ['$timestamp', bucketSize]}]}}}
    sort1 = {'$sort': {'timestamp': 1}}
    group = {'$group': {'_id': '$tsMod', 'count': {'$sum': 1}, 'headline': {'$first': '$title'}}}
    sort2 = {'$sort': {'_id': 1}}
    
    pipeline = [matchTopic, matchTimestamp, project, sort1, group, sort2]

    return returnObj(list(db.qdoc.aggregate(pipeline)), startTime, endTime, bucketSize)

def returnObj(obj, minTime, maxTime, bucketSize):
    newReturn = []
    minTime = minTime-(minTime%bucketSize); maxTime = maxTime-(maxTime%bucketSize)
    time = minTime; u = 0;
    while time <= maxTime:
        ob = {'_id': 0, 'count':0, 'headline': ''}
        if len(obj) > u:
            ob = obj[u]
        if ob['_id'] == time:
            newReturn.append({'timestamp': int(ob['_id']), 'count': ob['count'], 'headline': ob.get('headline', '')})
            u += 1
        else:
            newReturn.append({'timestamp': int(time), 'count': 0, 'headline': ''})
        time += bucketSize
    return newReturn

if __name__ == "__main__":
    print tweetTimeline("obama", 20)
    # print topicTimeline(293)
import pymongo

client = pymongo.MongoClient(host=['223.2.41.104:27017'])
db = client.Comparison
metricCollection = db.Metric
METRICS = metricCollection.find({})
# print('find %d metrics' % len(METRICS))
print(METRICS)
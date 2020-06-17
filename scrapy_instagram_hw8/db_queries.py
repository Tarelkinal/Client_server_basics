from pymongo import MongoClient

client = MongoClient('localhost', 27017)

collection = client.instagram.instagram

#  запрос к базе, который возвращает список подписчиков пользователя gitarist3099
for x in collection.find({'origin_user_name': 'gitarist3099', 'status': 'follower'}, {'_id': 0, 'user_name': 1}):
    print([t for t in x.values()][0])

print('========================')

#  запрос к базе, который возвращает список профилей, на которые подписан пользователь gitarist3099
for x in collection.find({'origin_user_name': 'gitarist3099', 'status': 'following'}, {'_id': 0, 'user_name': 1}):
    print([t for t in x.values()][0])

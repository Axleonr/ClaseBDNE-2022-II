import redis

# connect to redis
client = redis.Redis(host='172.17.0.2', port=6379)

# set a key
client.set('test-key', 'test-value')

# get a value
value = client.get('test-key')
print(value)
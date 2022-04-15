from cassandra.cluster import Cluster

cluster = Cluster()

print(type(cluster))

cluster2 = Cluster(['127.0.0.1'])

cluster.connect()
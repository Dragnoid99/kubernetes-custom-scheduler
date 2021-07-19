import pickle

dbfile = open('scheduler/files/pod_creation_pickle', 'wb')
a = {}
pickle.dump(a,dbfile)
dbfile.close()

dbfile = open('scheduler/files/deployment_pickle', 'wb')
pickle.dump(a,dbfile)
dbfile.close()

dbfile = open('scheduler/files/deployment_slo', 'wb')
pickle.dump(a,dbfile)
dbfile.close()

dbfile = open('scheduler/files/pods_active_pickle', 'wb')
pickle.dump(a,dbfile)
dbfile.close()


dbfile = open('scheduler/files/pod_deletion_pickle', 'wb')
pickle.dump(a,dbfile)
dbfile.close()



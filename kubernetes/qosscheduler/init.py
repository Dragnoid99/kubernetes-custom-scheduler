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

dbfile = open('scheduler/files/deployment_qos_metric', 'wb')
pickle.dump(a,dbfile)
dbfile.close()

dbfile = open('../files/deployment_run_time', 'wb')
pickle.dump(a, dbfile)
dbfile.close()

dbfile = open('../files/deployment_pause_time', 'wb')
pickle.dump(a, dbfile)
dbfile.close()

dbfile = open('../files/deployment_qos', 'wb')
pickle.dump(a, dbfile)
dbfile.close()

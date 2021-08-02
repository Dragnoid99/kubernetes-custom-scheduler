import pickle

time_limit = 6000
min_users = 60
peak_one_users = 300
peak_two_users = 240

arr = {}
arr['time_limit'] = time_limit
arr['min_users'] = min_users
arr['peak_one_users'] = peak_one_users
arr['peak_two_users'] = peak_two_users

dbfile = open('locust01/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust02/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust11/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust12/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()


dbfile = open('locust13/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()


dbfile = open('locust21/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()


dbfile = open('locust22/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust23/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust24/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()

dbfile = open('locust25/file', 'wb')
pickle.dump(arr, dbfile)
dbfile.close()


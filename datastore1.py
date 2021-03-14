import os, json

class DataStore:
    dpath = '/datastore'
    data = dict()

    def __init__(self, store_freq=5, buckets=['default']):
        if not self.isdir(self.dpath):
            os.mkdir(self.dpath)
        for b in buckets:
            bpath = '/' + self.dpath + '/' + b
            if self.isfile(bpath):
                v = json.load(bpath)
            else:
                v = dict()
            self.data[b] = v
        self.alive_f = True

    def alive(self):
        return self.alive_f

    def isdir(self, path):
        try:
            return os.stat(self.dpath)[0] & 0o40000
        except OSError:
            return False

    def isfile(self, path):
        try:
            return os.stat(self.dpath)[0] & 0o100000
        except OSError:
            return False

    def persist(self, bucket='default', all=False): # XXX needs thread safety
        bpath = '/' + self.dpath + '/' + bucket
        bpath_t = bpath + '.tmp'
        fp = open(bpath_t, 'w')
        json.dump(self.data[bucket], fp)
        fp.flush()
        fp.close()
        os.rename(bpath_t, bpath) # XXX May not be necessary with littlefs

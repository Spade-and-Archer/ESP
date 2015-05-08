# list_of_modules = glob.glob(sys.argv[0][:sys.argv[0].index('/', -1)])
def run():
    print 'hi2'


postArgs = ()


class dummy():
    def __init__(self):
        self.update_period = 100
        self.run = run
        self.post = run
        self.postArgs = postArgs


main = dummy()
# module should have a 'main' object that is an output driver, module, or input driver depending on folder
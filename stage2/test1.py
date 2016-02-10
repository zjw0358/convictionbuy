import os
def some_func():
    print 'in test 1, unproductive'
    os.environ['zackfile'] = 'zack_1.csv'
    print os.environ['zackfile']

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    some_func()
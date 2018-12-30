localhost      = "http://localhost/" # your local host
database       = "mysql://root@localhost/vaticChecker" # server://user:pass@localhost/dbname
min_training   = 2  # the minimum number of training videos to be considered

import os.path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# TODO: remove on server
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp/apache'

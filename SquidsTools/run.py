import os
from html_utils import *


def main():
    this_dir, this_filename = os.path.split(__file__)
    path = os.path.join(this_dir, 'web')
    eel.init(path, allowed_extensions=['.js', '.html'])
    eel.start('index.html')

if __name__ == '__main__':
    main()

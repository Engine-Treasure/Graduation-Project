
#
# Simple Image Converter for some simple usage.
#

__author__ = "Engine"
__date__ = "2017-04-03"


import os
import random
import shutil
import string

import fire


class Toolkit(object):
    """A simple Toolkit for my daily requirement."""

    def random_string(self, length):
        return ''.join(random.SystemRandom().choice(string.letters + string.digits) for _ in range(length))



    def reorganize(self, src, dst, ext, size=250):
        """
        :param src: original directory
        :param dst: destination
        :param ext: file type
        :param size: goal size
        """
        print(src)

        ls = []
        for item in os.listdir(src):
            fn = os.path.join(src, item)
            print(fn)
            if os.path.isdir(fn):
                self.reorganize(fn, dst, ext, size=250)
            elif os.path.isfile(fn) and fn.lower().endswith(ext):
                if len(ls) < size:
                    ls.append(fn)
                else:
                    dirname = os.path.join(dst, self.random_string(16))
                    os.makedirs(dirname)
                    for i in ls:
                        # shutil.copy(i, os.path.join(dirname, fn.split("/")[-1]))
                        shutil.copy(i, dirname)
                    del ls[:]
      
    # todo: add more

if __name__ == "__main__":
    fire.Fire(Toolkit)

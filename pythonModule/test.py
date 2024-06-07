import os

a = 'test.py'

filename_pure, extension = os.path.splitext(a)
print(filename_pure)
print(extension[1:])
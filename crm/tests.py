from django.test import TestCase

# Create your tests here.


print("yuan_alex_egon".split("_", 1))   # 只分一次
print("yuan_alex_egon".split("_", 2))   # 分两次
print("yuan_alex_egon".rsplit("_",1))   # 从右边开始分一次
"""
['yuan', 'alex_egon']
['yuan', 'alex', 'egon']
['yuan_alex', 'egon']
"""
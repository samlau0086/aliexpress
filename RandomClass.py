# coding=utf-8
import random
def randStr(strlist = ['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], charCount = 1):
    return ''.join(random.sample(strlist, charCount))

def randNum(numlist = ['0','1','2','3','4','5','6','7','8','9'], numCount = 1):
    return ''.join(random.sample(numlist, numCount))

def randChoice(strlist = []):#返回多个字符串中其中一个
    return random.choice(strlist)
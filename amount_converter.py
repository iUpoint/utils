# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 23:12:29 2018

@author: epsoft
"""
import numpy as np

#Arabic numerals and numerals in capitals of Chinese characters
def get_number(string):
    #'error'为默认返回值，可自设置
    #'ERROR：{}兑人民币汇率未定义！'.format(s)
    return {
            '零': 0,
            '壹': 1,
            '贰': 2,
            '叁': 3,
            '肆': 4,
            '伍': 5,
            '陆': 6,
            '柒': 7,
            '捌': 8,
            '玖': 9,
            '拾': 10,
            '一': 1,
            '二': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10
    }.get(string, 'error')
    
    
#汇率转换函数
def get_exchange_rate(string):
    money_dict = {
                    '美元': 6.9480,
                    '美金': 6.9480,
                    '美圆': 6.9480,
                    '美院': 6.9480,
                    '美': 6.9480,
                    '$': 6.9480,
                    '＄': 6.9480,
                    'usd': 6.9480,
                    'USD': 6.9480,
                    '日元': 0.06102,
                    '港币': 0.8874,
                    '港元': 0.8874,
                    '港': 0.8874,
                    '欧元': 7.8943,
                    '欧': 7.8943,
                    '英镑': 9.0748,
                    '法郎': 6.9038,
                    '澳元': 5.0359,
                    '澳': 5.0359,
                    '马克': 4.07
                }
    
    #传回去掉外币标识字符串，及对应汇率
    for s in money_dict.keys():
        if string.find(s) > -1:
            return (''.join(string.split(s)), 
                    money_dict.get(s, 'ERROR：{}兑人民币汇率未定义！'.format(s)))
    return (string, 1)


#判断是否为数字，可以包含1个小数点
def is_digit(string):
    '''数值全是数字，且可以进行表达式运算'''
    #
    s = ''.join(string.split('.'))
    if s.isdigit():
        #做一步判断，防止 '012'这种通过了
        #https://www.cnblogs.com/cxchanpin/p/6882451.html
        try:
            eval(string)
            return True
        except:
            return False
    else: return False
    
def count_digit(string):
    #isdigit只统计数字， isnumeric也可统计汉字 
    #解决了 ‘陆建庆’ 和 ‘3三’ 的问题
    return sum([s.isnumeric() for s in string])

def is_len_1_num(string):
    #a = string != '元'
    b = len(string) == 1
    c = string in '壹贰叁肆伍陆柒捌玖一二三四五六七八九123456789'
    return b and c


def Chinese_to_Arabic(string):    
    '''空串等直接传回0'''
    #所以对’拾伍‘等要另外考虑，头尾区别对待，头是乘数，尾是加数
    if string in ['','元','整','元整']: return 0
    '''如果首字符为零，直接踢除'''
    #注意次序，非空串才能索引第一个元素
    if string[0] == '零': string = string[1:]
    '''判断是否全是数字
    str.isnumeric(): True if 只包含数字；otherwise False。 '壹亿玖仟万'这也算数字，服了！！
    注意：此函数只能用于unicode string
    str.isdigit(): True if 只包含数字；otherwise False。
    str.isalpha()：True if 只包含字母；otherwise False。
    str.isalnum()：True if 只包含字母或者数字；otherwise False。''' 
    #如 3三亿这种，亿之前不可出现两种形式的数，要不全汉字要不全数字，否则不好解释
    if is_digit(string): return eval(string)
    
    '''汉字转阿拉伯数字'''
    if get_number(string) != 'error':
        return get_number(string)
    elif string.find('亿') > -1:
        #目前应该只有一个亿字, 如果名字中包含亿、佰等字，也会出错哦
        #可以出现类似 一亿亿 这样的表述，但是一万万等感觉不太合理
        #ind = string.find('亿')
        ind = [i.start() for i in re.finditer('亿', string)][-1]
        a = Chinese_to_Arabic(string[0:ind])
        #防止出现‘壹亿伍’返回 100000005的情况，下同，注意此处是‘仟万’
        #直接按长度为1判断，会导致类似‘壹亿元’不转化
        s = string[(ind+1):]
        b = Chinese_to_Arabic(s+'仟万') if is_len_1_num(s) else Chinese_to_Arabic(s)
        if is_digit(str(a)) and is_digit(str(b)):
            return a*100000000 + b
        else: return string
    elif string.find('万') > -1:
        ind = string.find('万')
        a = Chinese_to_Arabic(string[0:ind])
        #防止出现‘壹万捌’返回 10008的情况，下同，
        #直接按长度为1判断，会导致类似‘壹万元’不转化
        s = string[(ind+1):]
        b = Chinese_to_Arabic(s+'仟') if is_len_1_num(s) else Chinese_to_Arabic(s)
        if is_digit(str(a)) and is_digit(str(b)):
            # 防止出现类似 70000万，可能会出错，下同
            if a%10000 == 0: return string
            return a*10000 + b
        else: return string
    elif string.find('仟') > -1:
        ind = string.find('仟')
        a = Chinese_to_Arabic(string[0:ind])
        s = string[(ind+1):]
        b = Chinese_to_Arabic(s+'佰') if is_len_1_num(s) else Chinese_to_Arabic(s)
        if is_digit(str(a)) and is_digit(str(b)):
            if a%1000 == 0: return string
            return a*1000 + b
        else: return string
    elif string.find('佰') > -1:
        ind = string.find('佰')
        a = Chinese_to_Arabic(string[0:ind])
        s = string[(ind+1):]
        b = Chinese_to_Arabic(s+'拾') if is_len_1_num(s) else Chinese_to_Arabic(s)
        if is_digit(str(a)) and is_digit(str(b)):
            if a%100 == 0: return string
            return a*100 + b
        else: return string
    elif string.find('拾') > -1:
        ind = string.find('拾')
        #防止出现'拾伍'  返回5的情况
        a = 1 if string[0:ind] == '' else Chinese_to_Arabic(string[0:ind])
        b = Chinese_to_Arabic(string[(ind+1):])
        if is_digit(str(a)) and is_digit(str(b)):
            if a%10 == 0: return string
            return a*10 + b
        else: return string
    elif len(string)==1:
        #get_number(string[0]) != 'error' or is_digit(string[0]):
        #这里只要判断长度为1的汉字就可以了，
        #不可以混，要不就是‘2仟’这种，要不就是‘3000’这种，要不就是‘三’这种
        #数字的个数大于1，例如 7000w 这种，直接传回，否则会传回7
        #330元这种，递归string[:-1], 可在外层先剔除【'元整', '元'】
        #if count_digit(string) > 1:
        #    #if string[-1] == '元': return Chinese_to_Arabic(string[:-1])
        #    return string
        if get_number(string[0]) != 'error':
            return get_number(string[0])
        else: return eval(string[0])
    else:
        return string
    
    


#美院50万    美元41万  美元330元  意识  戚荣伟  USD68  9900万美元  
#壹亿伍  壹仟叁佰捌  拾伍  贰仟仟 330元    1亿零8wa  3三亿  陆建庆
#745841183-     71548595-3   700百  400*7  39.8、  250香港  206.万美元
#2000千  800百  1亿零8wa  150、0094   0。3   /20  ***   35,869,608
def amount_converter(string):
    '''备份，防止改不了，要维持原样'''
    #string0 = string
    string = str(string)
    res = {'string': string, 'exchange_rate': 1, 'number': ''}
    
    '''去掉掉一些无用的字符'''
    # ',','*','-','，','。','、','/','[',']','x','w'
    # 先别剔除’零’，后面还有用，如：一百五=150， 一百零五=105
    for s in ['人民币','整','(',')','（','）',' ','[',']',',','，']:
        string = ''.join(string.split(s))
        
    
    '''首先判断为缺失的情况'''
    if string in ['', 'nan']:
        res['number'] = np.NaN
        return res
    
    
    '''将全角字符转换为半角字符
    1. string.replace(f_s, t_s)
    2. re.compile(f_s).sub(t_s, string)'''
    num_dict = {
            '０': '0',
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
            '．': '.'
            }
    for s in num_dict.keys():
        string = string.replace(s, num_dict[s])
    
    '''错别字修正'''
    #拐：捌， 无：伍， 戚：柒
    mistake_dict = {
            '一': '壹',
            '二': '贰',
            '三': '叁',
            '四': '肆',
            '五': '伍',
            '六': '陆',
            '七': '柒',
            '八': '捌',
            '九': '玖',
            '十': '拾',
            '百': '佰',
            '千': '仟',
            '圆': '元',
            '两': '贰',
            '叄': '叁',
            '参': '叁',
            '拐': '捌',
            '伯': '佰',
            '院': '元',
            '无': '元',
            '意识': '壹拾',
            '香港': '港元'
            }    
    for s in mistake_dict.keys():
        string = string.replace(s, mistake_dict[s])
    
    
    '''去除外币标识，并提取汇率乘数'''
    string, res['exchange_rate'] = get_exchange_rate(string)
    
    '''去除元整，元等无关字样'''
    string = ''.join(string.split('元'))
    
    num = Chinese_to_Arabic(string)
    if is_digit(str(num)):
        res['number'] = res['exchange_rate'] * num
    else:
        res['number'] = res['string']
        
    '''返回'''
    return res



if __name__ == "__main__":
    amount_converter('一亿九千三百万6千8')
    
  
 



# '一亿九千万'

# {'5': 34453,
#  '3': 11368,
#  '0': 124270,
#  '1': 32029,
#  '2': 13309,
#  'n': 20740,
#  'a': 10371,
#  '4': 2504,
#  '9': 1686,
#  '壹': 1138,
#  '仟': 407,
#  '6': 4751,
#  '8': 7757,
#  '日': 33,
#  '元': 740,
#  '美': 706,
#  '.': 1722,
#  '7': 2037,
#  '贰': 408,
#  '拾': 1512,
#  '伍': 1757,
#  '万': 576,
#  '佰': 1719,
#  '叁': 313,
#  '亿': 158,
#  '零': 94,
#  '陆': 132,
#  '捌': 189,
#  '五': 47,
#  '十': 43,
#  '百': 44,
#  '叄': 3,
#  '圆': 41,
#  '一': 45,
#  '柒': 29,
#  '九': 4,
#  '玖': 19,
#  ' ': 14,
#  '肆': 36,
#  '参': 4,
#  '六': 8,
#  '(': 16,
#  ')': 17,
#  '港': 36,
#  '金': 23,
#  'x': 3,
#  '（': 19,
#  '）': 16,
#  '１': 8,
#  '０': 26,
#  '拐': 1,
#  '币': 29,
#  '５': 9,
#  '８': 7,
#  '二': 11,
#  '法': 2,
#  '郎': 2,
#  '无': 1,
#  '三': 23,
#  '澳': 1,
#  '人': 20,
#  '民': 20,
#  '八': 9,
#  ',': 7,
#  '-': 2,
#  '伯': 5,
#  '千': 35,
#  '＄': 1,
#  '欧': 22,
#  '[': 1,
#  ']': 1,
#  'u': 2,
#  's': 2,
#  'd': 2,
#  '英': 2,
#  '镑': 2,
#  '２': 4,
#  '戚': 1,
#  '荣': 1,
#  '伟': 1,
#  '*': 4,
#  '$': 38,
#  '４': 1,
#  '．': 1,
#  '３': 1,
#  'U': 6,
#  'S': 6,
#  'D': 6,
#  '葳': 1,
#  '山': 1,
#  '李': 1,
#  '小': 1,
#  '龙': 1,
#  '马': 1,
#  '克': 1,
#  '、': 2,
#  '院': 1,
#  '整': 7,
#  '。': 3,
#  '，': 1,
#  '香': 1,
#  '四': 2,
#  '建': 1,
#  '庆': 1,
#  '意': 1,
#  '识': 1,
#  '两': 1,
#  '/': 1,
#  '何': 1,
#  '成': 1,
#  'w': 1}
































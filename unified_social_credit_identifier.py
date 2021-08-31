# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:04:53 2019

@author: Administrator
"""


import re
import time
import retry
import numpy as np
import pandas as pd
import cx_Oracle
from sqlalchemy import create_engine, types
# 转自：https://blog.csdn.net/warrah/article/details/69338912

#定义一个重试修饰器，默认重试一次
def retry_fun(tries=1, delay=2, random_sec_max=3):
    #用来接收函数
    import time
    import numpy as np
    def wrapper(func):
        #用来接收函数的参数
        def wrapper(*args,**kwargs):
            #为了方便看抛出什么错误定义一个错误变量
            #last_exception =None
            #循环执行包装的函数
            for _ in range(tries):
                try:
                    #如果没有错误就返回包装的函数，这样跳出循环
                    return func(*args, **kwargs)
                except Exception as err:
                    #捕捉到错误不要return，不然就不会循环了
                    #last_exception = e 
                    #np.random.randint(0,random_sec_max+1,size=10)
                    time.sleep(delay + np.random.random()*random_sec_max)
                    print(err)
            else:
				#如果要看抛出错误就可以抛出
				# raise last_exception
                raise 'ERROR: 超过retry指定执行次数！！'
                print('未执行参数为：', *args, **kwargs)
        return wrapper
    return wrapper


#backoff=1, jitter=0, , logger=retry.logging
#@retry_fun(tries=5, delay=2, random_sec_max=5)
@retry.retry(tries=5, delay=5, backoff=1, max_delay=10)
def insert_db(data, orcl_engien, ttb):
    # dtyp = {col:types.VARCHAR(df[col].str.len().max())
    #    for col in df.columns[df.dtypes == 'object'].tolist()}
    # 太慢！！
    #dtyp = {'aac147':types.VARCHAR(18),'score':types.NUMBER(6,2)}
    #return data.to_sql(ttb, con=db, dtype=dtyp, if_exists='append', index=False)
    #output = io.StringIO()
    #data.to_csv(output, sep='\t', index=False, header=False)
    #output.getvalue()
    #output.seek(0)
    db = create_engine(orcl_engien)  #不需要close()
    conn = db.raw_connection()
    #db = cx_Oracle.connect(orcl_engien[9:])
    cursor = conn.cursor()
    #cursor.copy_from(output, ttb, null='')
    col = ', '.join(data.columns.tolist())
    s = ', '.join([':'+str(i) for i in range(1, data.shape[1]+1)])
    sql = 'insert into {}({}) values({})'.format(ttb, col, s)
    #TypeError: expecting float, 
    cursor.executemany(sql, data.values.tolist())
    conn.commit()
    cursor.close()
	#try:
    #except Exception as e:
    #    print(e)
    #finally:


class UnifiedSocialCreditIdentifier(object):
    '''
    统一社会信用代码 + 组织结构代码校验
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # 统一社会信用代码中不使用I,O,S,V,Z
        # ''.join([str(i) for i in range(10)])
        # import string
        # string.ascii_uppercase  # ascii_lowercase |  ascii_letters
        # dict([i for i in zip(list(self.string), range(len(self.string)))])
        # dict(enumerate(self.string))
        # list(d.keys())[list(d.values()).index(10)]
        # chr(97)  --> 'a'
        self.string1 = '0123456789ABCDEFGHJKLMNPQRTUWXY'
        self.SOCIAL_CREDIT_CHECK_CODE_DICT = {
                '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
                'A':10,'B':11,'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 
                'J':18, 'K':19, 'L':20, 'M':21, 'N':22, 'P':23, 'Q':24,
                'R':25, 'T':26, 'U':27, 'W':28, 'X':29, 'Y':30}
        # 第i位置上的加权因子
        self.social_credit_weighting_factor = [1,3,9,27,19,26,16,17,20,29,25,13,8,24,10,30,28]
        
        # GB11714-1997全国组织机构代码编制规则中代码字符集
        self.string2 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.ORGANIZATION_CHECK_CODE_DICT = {
                '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
                'A':10,'B':11,'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17,'I':18, 
                'J':19, 'K':20, 'L':21, 'M':22, 'N':23, 'O':24,'P':25, 'Q':26,
                'R':27,'S':28, 'T':29, 'U':30,'V':31, 'W':32, 'X':33, 'Y':34,'Z':35}
        # 第i位置上的加权因子
        self.organization_weighting_factor = [3,7,9,10,5,8,4,2]
        
    def check_social_credit_code(self, code):
        '''
        统一社会信用代码校验
        国家标准GB32100—2015：18位统一社会信用代码从2015年10月1日正式实行，
        标准规定统一社会信用代码用18位阿拉伯数字或大写英文字母（不使用I、O、Z、S、V）表示，
        分别是1位登记管理部门代码、1位机构类别代码、6位登记管理机关行政区划码、9位主体标识码（组织机构代码）、1位校验码
            
            
        税号 = 6位行政区划码 + 9位组织机构代码
        计算校验码公式:
            C18 = 31-mod(sum(Ci*Wi)，31)
        其中Ci为组织机构代码的第i位字符,Wi为第i位置的加权因子,C18为校验码
        c18=30, Y; c18=31, 0
        '''
        # 主要是避免缺失值乱入
        #if type(code) != str: return False
        # 转大写
        code = code.upper()
        # 1. 长度限制
        if len(code) != 18:
            print('{} -- 统一社会信用代码长度不等18！'.format(code))
            return False
        # 2. 不含IOSVZ -- 组成限制, 非字典表给个非常大的数, 不超过15000
        '''lst = list('IOSVZ')
        for s in lst:
            if s in code:
                print('包含非组成字符：%s' % (s))
                return False'''
            
        # 2. 组成限制
        # 登记管理部门：1=机构编制; 5=民政; 9=工商; Y=其他
        # 机构类别代码: 
        '''
        机构编制=1：1=机关 | 2=事业单位 | 3=中央编办直接管理机构编制的群众团体 | 9=其他 
        民政=5：1=社会团体 | 2=民办非企业单位 | 3=基金会 | 9=其他 
        工商=9：1=企业 | 2=个体工商户 | 3=农民专业合作社 
        其他=Y：1=其他
        '''
        reg = r'^(11|12|13|19|51|52|53|59|91|92|93|Y1)\d{6}\w{9}\w$'
        if not re.match(reg, code):
            print('{} -- 组成错误！'.format(code))
            return False
        
        # 3. 校验码验证
        # 本体代码
        ontology_code = code[:17]
        # 校验码
        check_code = code[17]
        # 计算校验码
        tmp_check_code = self.gen_check_code(self.social_credit_weighting_factor, 
                                             ontology_code, 
                                             31, 
                                             self.SOCIAL_CREDIT_CHECK_CODE_DICT)
        if tmp_check_code == -1:
            print('{} -- 包含非组成字符！'.format(code))
            return False
        
        tmp_check_code = (0 if tmp_check_code==31 else tmp_check_code)
        if self.string1[tmp_check_code] == check_code:
            #print('{} -- 统一社会信用代码校验正确！'.format(code))
            return True
        else:
            print('{} -- 统一社会信用代码校验错误！'.format(code))
            return False

    def check_organization_code(self, code):    
        '''
        组织机构代码校验
        该规则按照GB 11714编制：统一社会信用代码的第9~17位为主体标识码(组织机构代码)，共九位字符
        计算校验码公式:
            C9 = 11-mod(sum(Ci*Wi)，11)
        其中Ci为组织机构代码的第i位字符,Wi为第i位置的加权因子,C9为校验码
        C9=10, X; C9=11, 0
        @param  code: 统一社会信用代码 / 组织机构代码
        '''
        # 主要是避免缺失值乱入
        #if type(code) != str: return False
        # 1. 长度限制
        if len(code) != 9:
            print('{} -- 组织机构代码长度不等9！'.format(code))
            return False
        
        # 2. 组成限制
        reg = r'^\w{9}$'
        if not re.match(reg, code):
            print('{} -- 组成错误！'.format(code))
            return False
        
        # 3. 校验码验证
        # 本体代码
        ontology_code = code[:8]
        # 校验码
        check_code = code[8]
        # 计算校验码
        tmp_check_code = self.gen_check_code(self.organization_weighting_factor, 
                                             ontology_code, 
                                             11, 
                                             self.ORGANIZATION_CHECK_CODE_DICT)
        if tmp_check_code == -1:
            print('{} -- 包含非组成字符！'.format(code))
            return False
        
        tmp_check_code = (0 if tmp_check_code==11 
                          else (33 if tmp_check_code==10 else tmp_check_code))
        if self.string2[tmp_check_code] == check_code:
            #print('{} -- 组织机构代码校验正确！'.format(code))
            return True
        else:
            print('{} -- 组织机构代码校验错误！'.format(code))
            return False
        
    def check_code(self, code, code_type='sc'):
        '''Series类型
        @code_type {org, sc}'''
        #try:
        if type(code) != str: return False
        if code_type == 'sc':
            return self.check_social_credit_code(code)
        elif code_type == 'org':
            return self.check_organization_code(code)
        else:
            if len(code)==18:
                return self.check_social_credit_code(code)
            else:
                return self.check_organization_code(code) if len(code)==9 else False
        #except Exception as err:
        #    print(err)
        #    print('code:', code)

    def gen_check_code(self, weighting_factor, ontology_code, modulus, check_code_dict):
        '''
        @param weighting_factor: 加权因子
        @param ontology_code:本体代码
        @param modulus:  模数(求余用)
        @param check_code_dict: 字符字典
        '''
        total = 0
        for i in range(len(ontology_code)):
            if ontology_code[i].isdigit():
                #print(ontology_code[i], weighting_factor[i])
                total += int(ontology_code[i]) * weighting_factor[i]
            else:
                num = check_code_dict.get(ontology_code[i], -1)
                if num < 0: return -1
                total +=  num * weighting_factor[i]
        diff = modulus - total % modulus
        #print(diff)
        return diff




if __name__ == '__main__':
    # 计时
    t0 = time.time()
    print('开始：', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
	
    # 数据库链接 + 配置信息
    tb_name = 'qmcb_ab01_clear'
    orcl_engien = 'oracle://qmcbrt:qmcbrt@127.0.0.1:1521/tqmcbdb'
    db = create_engine(orcl_engien)  #不需要close()
    
	# 创建表 -- 表名及用户名必须大写
    sql = "select count(*) from all_tables where TABLE_NAME = '{}' and OWNER='QMCBRT'".format(tb_name)
    n = pd.read_sql_query(sql, db).values[0,0]
    if n == 0:
        print('表不存在，创建表...')  #NUMBER
        db.execute('''create table qmcb_ab01_clear (
                AAZ400 VARCHAR2(9) NOT NULL,
                AAB001 VARCHAR2(30) NOT NULL,
                BAB010 VARCHAR2(18),
                AAB003 VARCHAR2(9))''')
    
    # 清空表 -- 感觉不用判断，但老是报错
    sql = "select count(*) from {}".format(tb_name)
    n = pd.read_sql_query(sql, db).values[0,0]
    if n > 0:
        print('表存在数据，清空表...')
        db.execute('truncate table {}'.format(tb_name))
		
	# 查询单位信息数据
    sql = "select AAZ400, AAB001, BAB010, AAB003 from AB01@BEIK_RT"
    qmcb_ab01_data = pd.read_sql_query(sql, db)
    # 爬虫数据
    #qmcb_ls_bab010 = pd.read_csv('....', encoding='uft-8', index=False)
    sql = "select AAB004, BAB010 from QMCB_LS_BAB010"
    qmcb_ls_bab010 = pd.read_sql_query(sql, db)
    
    # 缺失值填充
    qmcb_ab01_data.fillna(np.nan, inplace=True)
    
	# 统一社会信用代码及组织机构代码校验
    u = UnifiedSocialCreditIdentifier()
    #print(u.check_social_credit_code(code='91330382575324831A'))
    #print(u.check_organization_code(code='575324831'))
	# ab01 统一社会信用代码修正
    ind = qmcb_ab01_data.bab010.apply(lambda code: u.check_code(code, code_type=''))
    qmcb_ab01_data.bab010[~ind] = ''
    # ab01 组织机构代码修正
    ind = qmcb_ab01_data.aab003.apply(lambda code: u.check_code(code, code_type=''))
    qmcb_ab01_data.aab003[~ind] = ''
    # 爬虫数据修正
    ind = qmcb_ls_bab010.bab010.apply(lambda code: u.check_code(code, code_type='sc'))
    db.execute('truncate table QMCB_LS_BAB010')  #直接清空爬虫库
    insert_db(qmcb_ls_bab010.loc[ind, :], orcl_engien, 'QMCB_LS_BAB010')
	
	# 清洗结果保存数据库
    insert_db(qmcb_ab01_data, orcl_engien, tb_name)
	
	# 打印
    print('耗时：', time.time() - t0)
	
	
	
	







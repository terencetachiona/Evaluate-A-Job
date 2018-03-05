#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author:lthan
# @Email :terence"ipcconsultants.com
# @Time  :2018/3/3 17:18

import numpy as np
import re
import jieba
import jieba.analyse
from string import punctuation
import os

class DataHelper(object):
    def __init__(self):
        self.my_puctuation = '~·！@#￥%……&*（）｛｝【】、“”；：‘’，。、《》？' + punctuation
    def load_datasets(self,file_name,keywords_file):
        '''
        Load the jobdesc information
        :param file_name:
        :param keywords_file:
        :return:
        '''
        x = []
        y = []
        jieba.load_userdict(keywords_file)
        with open(file_name,'r',encoding='utf-8') as fr:
            for line in fr:
                # read line
                try:
                    line = line.strip().split('\001')
                    city = line[56].strip()
                    jobtype = int(line[31])  # 雇佣类型： 全职 兼职 学生职位
                    if city != '530' or jobtype != 2:
                        continue
                    input_x = line[24] # 职位名称
                    input_x += line[46] # 职位描述
                    input_x = re.sub(pattern='\d\S',repl='',string=input_x)
                    word_list = [word.lower() for word in list(jieba.cut(input_x)) if word not in self.my_puctuation]
                    input_x = " ".join(word_list)
                    input_y = [(float(line[15]) // 1000 + float(line[16]) // 1000) * 0.5]
                except ValueError as err:
                    print('except:{}'.format(err))
                x.append(input_x)
                y.append(input_y)

                #print(input_x, input_y)
        return [x,y]


    def batch_iter(self,data,batch_size,num_epochs,shuffle=True):
        '''
        return split batch of dataSet
        :param data:
        :param batch_size:
        :param num_epochs:
        :param shuffle:
        :return:
        '''
        data = np.array(data)
        data_size = len(data)
        num_batches_per_epoch = int((len(data) - 1) / batch_size) + 1
        for epoch in range(num_epochs):
            # Shuffle the data at each epoch
            if shuffle:
                shuffle_indices = np.random.permutation(np.arange(data_size))
                shuffled_data = data[shuffle_indices]
            else:
                shuffled_data = data
            for batch_num in range(num_batches_per_epoch):
                start_index = batch_num * batch_size
                end_index = min((batch_num+1)*batch_size,data_size)
                yield shuffled_data[start_index:end_index]

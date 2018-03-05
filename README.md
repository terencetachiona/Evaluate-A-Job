# Position-Salary-Forecast
CNN Model : Using the job description data to predict the salary that the company should give.

1.参考论文《Convolutional Neural Networks for Sentence Classification》
论文链接：http://cslt.riit.tsinghua.edu.cn/mediawiki/images/f/fe/Convolutional_Neural_Networks_for_Sentence_Classi%EF%AC%81cation.pdf
文中介绍了CNN在文本分类中的应用。考虑在职位薪资预测中使用其中的CNN-rand模型处理文本语义抽象。

2.将职位名称和职位描述信息当作输入文本，增加技能词关键词进行分词并去除纯数字和标点符号的结果，将文中的CNN分类模型改成回归预测模型。
参考代码：https://github.com/dennybritz/cnn-text-classification-tf

3.随机抽选某城市的7500条职位进行测试，测试结果表明是可以work的，不过由于数据量比较少，造成过拟合严重，正在修改模型和参数，希望下一次结果能够有大的提升
薪资1代表1000，4500次迭代后的均方误差为训练集：3.726测试集：41.92

4.由于数据从公司数据库中取出的，这里就不上传数据了，如果需要可私信联系我


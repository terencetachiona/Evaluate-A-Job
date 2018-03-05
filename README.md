# Grade A Job
CNN Model : Using the job description data to predict the salary that the company should give.

1.Reference Paper "Convolutional Neural Networks for Sentence Classification"
Papers link：http://cslt.riit.tsinghua.edu.cn/mediawiki/images/f/fe/Convolutional_Neural_Networks_for_Sentence_Classi%EF%AC%81cation.pdf
The paper introduces the application of CNN in text classification. Consider using the CNN-rand model in job salary forecasting to process textual semantic abstractions

2.The job title and job description information are taken as input text, the word of skill word is added for word segmentation and the result of pure numbers and punctuation is removed, and the CNN classification model in the text is changed into the regression prediction model. Reference Code：https://github.com/dennybritz/cnn-text-classification-tf

3.Randomly selected 7500 jobs in a city for testing, the test results show that it is workable, but due to the relatively small amount of data, resulting in a serious fit, is modifying the model and parameters, I hope the next result can be greatly improved
Salary 1 represents 1000,400 After the iteration, the mean square error is training set: 3.726 test set：41.92

4.Because the data is taken out of the company database, there is no upload data, if you need to contact me privately

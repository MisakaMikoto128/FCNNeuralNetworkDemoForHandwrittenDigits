#!/usr/bin/python3
# coding:utf-8
# @Author: Lin Misaka
# @File: net.py
# @Data: 2020/11/30
# @IDE: PyCharm
from os import listdir
import numpy as np
import matplotlib.pyplot as plt
import pickle
# 函数img2vector将图像转换为向量
def img2vector(filename):
    returnVect = np.zeros((1, 1024))
    fr = open(filename)
    for i in range(32):
        lineStr = fr.readline()
        for j in range(32):
            returnVect[0, 32 * i + j] = int(lineStr[j])
    return returnVect


# 读取手写字体txt数据
def handwritingData(dataPath):
    hwLabels = []
    FileList = listdir(dataPath)  # 1 获取目录内容
    m = len(FileList)
    np.Mat = np.zeros((m, 1024))
    for i in range(m):
        # 2 从文件名解析分类数字
        fileNameStr = FileList[i]
        fileStr = fileNameStr.split('.')[0]  # take off .txt
        classNumStr = int(fileStr.split('_')[0])
        hwLabels.append(classNumStr)
        np.Mat[i, :] = img2vector(dataPath + '/%s' % fileNameStr)
    return np.Mat, hwLabels



# diff = True求导
def Sigmoid(x, diff=False):
    def sigmoid(x):        # sigmoid函数
        return 1 / (1 + np.exp(-x))
    def dsigmoid(x):
        f = sigmoid(x)
        return f * (1 - f)
    if (diff == True):
        return dsigmoid(x)
    return sigmoid(x)

# diff = True求导
def SquareErrorSum(y_hat, y, diff=False):
    if (diff == True):
        return y_hat - y
    return (np.square(y_hat - y) * 0.5).sum()


class Net():
    def __init__(self):
        # X Input
        self.X =  np.random.randn(1024, 1)
        self.W1 = np.random.randn(16, 1024)
        self.b1 = np.random.randn(16, 1)
        self.W2 = np.random.randn(16, 16)
        self.b2 = np.random.randn(16, 1)
        self.W3 = np.random.randn(10, 16)
        self.b3 = np.random.randn(10, 1)
        self.alpha = 0.01  #学习率
        self.losslist = [] #用于作图

    def forward(self, X, y, activate):
        self.X = X
        self.z1 = np.dot(self.W1, self.X) + self.b1
        self.a1 = activate(self.z1)
        self.z2 = np.dot(self.W2, self.a1) + self.b2
        self.a2 = activate(self.z2)
        self.z3 = np.dot(self.W3, self.a2) + self.b3
        self.y_hat = activate(self.z3)
        Loss = SquareErrorSum(self.y_hat, y)
        return Loss, self.y_hat

    def backward(self, y, activate):
        self.delta3 = activate(self.z3, True) * SquareErrorSum(self.y_hat, y, True)
        self.delta2 = activate(self.z2, True) * (np.dot(self.W3.T, self.delta3))
        self.delta1 = activate(self.z1, True) * (np.dot(self.W2.T, self.delta2))
        dW3 = np.dot(self.delta3, self.a2.T)
        dW2 = np.dot(self.delta2, self.a1.T)
        dW1 = np.dot(self.delta1, self.X.T)
        d3 = self.delta3
        d2 = self.delta2
        d1 = self.delta1
        #update weight
        self.W3 -= self.alpha * dW3
        self.W2 -= self.alpha * dW2
        self.W1 -= self.alpha * dW1
        self.b3 -= self.alpha * d3
        self.b2 -= self.alpha * d2
        self.b1 -= self.alpha * d1

    def setLearnrate(self, l):
        self.alpha = l

    def save(self,path):
        obj = pickle.dumps(self)
        with open(path,"wb") as f:
            f.write(obj)

    def load(path):
        obj = None
        with open(path, "rb") as f:
            try:
                obj = pickle.load(f)
            except:
                print("IOError")
        return obj

    def train(self, trainMat, trainLabels, Epoch=5, bitch=None):
        for epoch in range(Epoch):
            acc = 0.0
            acc_cnt = 0
            label = np.zeros((10, 1))#先生成一个10x1是向量，减少运算。用于生成one_hot格式的label
            for i in range(len(trainMat)):#可以用batch，数据较少，一次训练所有数据集
                X = trainMat[i, :].reshape((1024, 1)) #生成输入

                labelidx = trainLabels[i]
                label[labelidx][0] = 1.0

                Loss, y_hat = self.forward(X, label, Sigmoid)#前向传播
                self.backward(label, Sigmoid)#反向传播

                label[labelidx][0] = 0.0#还原为0向量
                acc_cnt += int(trainLabels[i] == np.argmax(y_hat))

            acc = acc_cnt / len(trainMat)
            self.losslist.append(Loss)
            print("epoch:%d,loss:%02f,accrucy : %02f%%" % (epoch, Loss, acc*100))
        self.plotLosslist(self.losslist, "Loss:Init->randn,alpha=0.01")

    def plotLosslist(self, Loss, title):
        font = {'family': 'simsun',
                'weight': 'bold',
                'size': 20,
                }
        m = len(Loss)
        X = range(m)
        # plt.figure(1)
        plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
        plt.subplot(111)
        plt.title(title, font)
        plt.plot(X, Loss)
        plt.xlabel(r'Epoch', font)
        plt.ylabel(u'Loss', font)
        plt.show()

    def test(self, testMat, testLabels, bitch=None):
        acc = 0.0
        acc_cnt = 0
        label = np.zeros((10, 1))#先生成一个10x1是向量，减少运算。用于生成one_hot格式的label
        if(bitch == None):
            bitch = len(testMat)
        for i in range(bitch):#可以用batch，数据较少，一次训练所有数据集
            X = testMat[i, :].reshape((1024, 1)) #生成输入

            labelidx = testLabels[i]
            label[labelidx][0] = 1.0

            Loss, y_hat = self.forward(X, label, Sigmoid)#前向传播

            label[labelidx][0] = 0.0#还原为0向量
            acc_cnt += int(testLabels[i] == np.argmax(y_hat))
        acc = acc_cnt / bitch
        print("test num: %d, accrucy : %05.3f%%"%(bitch,acc*100))


# 读取训练数据
trainDataPath = "./trainingDigits"
trainMat, trainLabels = handwritingData(trainDataPath)
testDataPath = "./testDigits"
testMat, testLabels = handwritingData(testDataPath)
net = Net()
net.setLearnrate(0.01)
net.train(trainMat, trainLabels, Epoch=200)
net.save("hr.model")
net.test(testMat, testLabels)

newmodel = Net.load("hr.model")
newmodel.test(testMat, testLabels)
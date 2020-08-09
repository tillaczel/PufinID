# Pufin ID

I created this projects durring the preparation to the interview for the Computer Vision Developer role at Pufin ID <img src="https://thehub-io.imgix.net/files/s3/20200624084631-c3012927f77aac1d5d1bad66f466e743.jpg?fit=crop&w=300&h=300&q=60" width="40"/>. The first project is an attack on XOR PUFs and the second is an implementation of a siamese one-shot learning model for PUF recognition.

## A-Machine-Learning-based-Security-Vulnerability-Study-on-XOR-PUFs

The scope of this project is small mainly due to time limitations. This is an implemenation of the paper [A machine learning-based security vulnerability study on xor pufs for resource-constraint internet of things](https://www.researchgate.net/publication/327939053_A_Machine_Learning-Based_Security_Vulnerability_Study_on_XOR_PUFs_for_Resource-Constraint_Internet_of_Things). 

The goal is to predict the PUF response to any challenge. This is achieved by training a neural network on challenge-response pairs. Future work could include different PUFs, which are harder to approximate and require more complex machine learning models.

It would had been more optimal to do a project on pattern recognition on cellphone images of PUFs, but I do not have access to a dataset, and I could not simulate it. 

## Siamese one-shot learning

To my understanding the task of the Computer Vision Developer at Pufin ID will be, to develope a model with which pictures of PUFs can be identified. The main problem is, that the PUF needs to be recognised from just one image. A common sollution for this one-shot learning task are siamese networks. My model is based on the paper [Siamese Neural Networks for One-shot Image Recognition](https://www.cs.cmu.edu/~rsalakhu/papers/oneshot1.pdf). I used the [Omniglot](https://www.kaggle.com/watesoyan/omniglot) dataset from Kaggle.



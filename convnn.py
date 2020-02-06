import math
import numpy as np 
import h5py
import matplotlib.pyplot as plt 
import scipy
from PIL import Image
from scipy import ndimage
import tensorflow as tf 
from tensorflow.python.framework import ops 
from cnn_utils import *

#This is a comment

# %matplotlib inline
np.random.seed(1)

X_train_orig, Y_train_orig, X_test_orig, Y_test_orig, classes = load_dataset()

index = 6
plt.imshow(X_train_orig[index])
plt.show()
print("y = " + str(np.squeeze(Y_train_orig[:, index])))

X_train = X_train_orig/255 # Normalize data
X_test = X_test_orig/255
Y_train = convert_to_one_hot(Y_train_orig, 6).T # Convert output to one hot and transpose
Y_test = convert_to_one_hot(Y_test_orig, 6).T

def create_placeholders(n_H0, n_W0, n_C0, n_y):
	X = tf.keras.Input(shape=(n_H0, n_W0, n_C0), dtype=tf.float32)
	Y = tf.keras.Input(shape=(n_y), dtype=tf.float32)
	return X, Y

def initialize_parameters():
	tf.random.set_seed(1)
	W1 = tf.Variable(tf.keras.initializers.GlorotUniform()((4,4,3,8)), dtype=tf.float32)
	W2 = tf.Variable(tf.keras.initializers.GlorotUniform()((2,2,8,16)), dtype=tf.float32)
	parameters = {"W1":W1, "W2":W2}
	return parameters

def forward_propagation(X, parameters):
	W1 = parameters['W1']
	W2 = parameters['W2']
	Z1 = tf.nn.conv2d(X, W1, strides = [1,1,1,1], padding = "SAME")
	A1 = tf.nn.relu(Z1)
	P1 = tf.nn.max_pool(A1, ksize = [1,8,8,1], strides=[1,8,8,1], padding = "SAME")
	Z2 = tf.nn.conv2d(P1, W2, strides = [9,1,1,1], padding = "SAME")
	A2 = tf.nn.relu(Z2)
	P2 = tf.nn.max_pool(A2, ksize = [1,4,4,1], strides = [1,4,4,1], padding = "SAME")
	F = tf.keras.layers.Flatten()(P2)
	Z3 = tf.keras.layers.Dense(F, activation = None)
	return Z3

def compute_cost(Z3, Y):
	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = Z3, labels = Y))
	return cost

def model(X_train, Y_train, X_test, Y_test, learning_rate = 0.009, num_epochs = 100, minibatch_size = 64, print_cost = True):	
	tf.random.set_seed(1)
	seed = 3
	(m, n_H0, n_W0, n_C0) = X_train.shape
	n_y = Y_train.shape[1]
	costs = []
	X, Y = create_placeholders(n_H0, n_W0, n_C0, n_y)
	parameters = initialize_parameters()
	Z3 = forward_propagation(X, parameters)
	cost = compute_cost(Z3, Y)
	optimizer = tf.train.AdamOptimizer(learning_rate = 0.009).minimize(cost)
	for epoch in range(num_epochs):
		minibatch_cost = 0.
		num_minibatches = int(m/minibatch_size)
		seed = seed + 1
		minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)
		for minibatch in minibatches:
			(minibatch_X, minibatch_Y) = minibatch
			_, temp_cost = f(minibatch_X, minibatch_Y)
			minibatch_cost += temp_cost / num_minibatches
		if print_cost == True and epoch % 5 == 0:
			print("Cost after epoch%i: %f" % (epoch, minibatch_size))
		if print_cost == True and epoch % 1 == 0:
			costs.append(minibatch_cost)
	plt.plot(np.squeeze(costs))
	plt.ylabel('cost')
	plt.xlabel('iterations (per tens)')
	plt.title("Learning rate =" + str(learning_rate))
	plt.show()
	# Calculate the correct predictions
	predict_op = tf.argmax(Z3, 1)
	correct_prediction = tf.equal(predict_op, tf.argmax(Y, 1))
	# Calculate accuracy on the test set
	accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
	print(accuracy)
	train_accuracy = accuracy.eval({X: X_train, Y: Y_train})
	test_accuracy = accuracy.eval({X: X_test, Y: Y_test})
	print("Train Accuracy:", train_accuracy)
	print("Test Accuracy:", test_accuracy)     
	return train_accuracy, test_accuracy, parameters


_, _, parameters = model(X_train, Y_train, X_test, Y_test)


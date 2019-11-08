# TRAINS - Example of tensorflow mnist training model logging
#
# Save and Restore a model using TensorFlow.
# This example is using the MNIST database of handwritten digits
# (http://yann.lecun.com/exdb/mnist/)
#
# Author: Aymeric Damien
# Project: https://github.com/aymericdamien/TensorFlow-Examples/

from __future__ import print_function

from os.path import exists, join
import tempfile

import numpy as np
import tensorflow as tf
from trains import Task

MODEL_PATH = join(tempfile.gettempdir(), "module_no_signatures")
task = Task.init(project_name='examples', task_name='Tensorflow mnist example')

## block
X_train = np.random.rand(100, 3)
y_train = np.random.rand(100, 1)
model = tf.keras.models.Sequential([tf.keras.layers.Dense(1)])
model.compile(loss='categorical_crossentropy',
              optimizer=tf.keras.optimizers.SGD(),
              metrics=['accuracy'])
model.fit(X_train, y_train, steps_per_epoch=1, nb_epoch=1)

with tf.Session(graph=tf.Graph()) as sess:
    if exists(MODEL_PATH):
        try:
            tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], MODEL_PATH)
            m2 = tf.saved_model.load(sess, [tf.saved_model.tag_constants.SERVING], MODEL_PATH)
        except Exception:
            pass
    tf.train.Checkpoint
## block end

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

# Parameters
parameters = {
    'learning_rate': 0.001,
    'batch_size': 100,
    'display_step': 1,
    'model_path': join(tempfile.gettempdir(), "model.ckpt"),

    # Network Parameters
    'n_hidden_1': 256,  # 1st layer number of features
    'n_hidden_2': 256,  # 2nd layer number of features
    'n_input': 784,  # MNIST data input (img shape: 28*28)
    'n_classes': 10,  # MNIST total classes (0-9 digits)
}
# TRAINS: connect parameters with the experiment/task for logging
parameters = task.connect(parameters)

# tf Graph input
x = tf.placeholder("float", [None, parameters['n_input']])
y = tf.placeholder("float", [None, parameters['n_classes']])


# Create model
def multilayer_perceptron(x, weights, biases):
    # Hidden layer with RELU activation
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    layer_1 = tf.nn.relu(layer_1)
    # Hidden layer with RELU activation
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_2 = tf.nn.relu(layer_2)
    # Output layer with linear activation
    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    return out_layer

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([parameters['n_input'], parameters['n_hidden_1']])),
    'h2': tf.Variable(tf.random_normal([parameters['n_hidden_1'], parameters['n_hidden_2']])),
    'out': tf.Variable(tf.random_normal([parameters['n_hidden_2'], parameters['n_classes']]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([parameters['n_hidden_1']])),
    'b2': tf.Variable(tf.random_normal([parameters['n_hidden_2']])),
    'out': tf.Variable(tf.random_normal([parameters['n_classes']]))
}

# Construct model
pred = multilayer_perceptron(x, weights, biases)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=parameters['learning_rate']).minimize(cost)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# 'Saver' op to save and restore all the variables
saver = tf.train.Saver()

# Running first session
print("Starting 1st session...")
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    # Training cycle
    for epoch in range(3):
        avg_cost = 0.
        total_batch = int(mnist.train.num_examples/parameters['batch_size'])
        # Loop over all batches
        for i in range(total_batch):
            batch_x, batch_y = mnist.train.next_batch(parameters['batch_size'])
            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, cost], feed_dict={x: batch_x,
                                                          y: batch_y})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if epoch % parameters['display_step'] == 0:
            print("Epoch:", '%04d' % (epoch+1), "cost=", \
                "{:.9f}".format(avg_cost))
        save_path = saver.save(sess, parameters['model_path'])

    print("First Optimization Finished!")

    # Test model
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    # Calculate accuracy
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))

    # Save model weights to disk
    save_path = saver.save(sess, parameters['model_path'])
    print("Model saved in file: %s" % save_path)

# Running a new session
print("Starting 2nd session...")
with tf.Session() as sess:
    # Initialize variables
    sess.run(init)

    # Restore model weights from previously saved model
    saver.restore(sess, parameters['model_path'])
    print("Model restored from file: %s" % save_path)

    # Resume training
    for epoch in range(7):
        avg_cost = 0.
        total_batch = int(mnist.train.num_examples / parameters['batch_size'])
        # Loop over all batches
        for i in range(total_batch):
            batch_x, batch_y = mnist.train.next_batch(parameters['batch_size'])
            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, cost], feed_dict={x: batch_x,
                                                          y: batch_y})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if epoch % parameters['display_step'] == 0:
            print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
    print("Second Optimization Finished!")

    # Test model
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    # Calculate accuracy
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    print("Accuracy:", accuracy.eval(
        {x: mnist.test.images, y: mnist.test.labels}))

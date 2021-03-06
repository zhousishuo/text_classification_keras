import sys
import os
import numpy as np
from sklearn.metrics import make_scorer, f1_score, precision_score, accuracy_score, log_loss, classification_report, confusion_matrix
from keras.preprocessing import sequence
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF
from textrnn import TextRNN
sys.path.append('../')
import data_helpers
from gensim.models import KeyedVectors

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
KTF.set_session(sess)

batch_size = 64
embedding_dim = 300
epochs = 100

print('Loading data...')
# get data
x_train, y_train, x_test, y_test, word2index = data_helpers.preprocess()
max_features = len(word2index)
print('max feature', max_features)

maxlen = max(len(x) for x in x_train)

print('Pad sequences...')
x_train = sequence.pad_sequences(x_train, maxlen=maxlen, value=0)
x_test = sequence.pad_sequences(x_test, maxlen=maxlen, value=0)


def load_word2vec(word2vec_model, vocab_sz, word2index):
    print('Load Word2vec...')
    word2vec1 = KeyedVectors.load_word2vec_format(word2vec_model, binary=True)
    embed_size = 300
    embedding_weight = np.zeros((vocab_sz, embed_size))
    for word, index in word2index.items():
        try:
            embedding_weight[index, :] = word2vec1[word]
        except KeyError:
            pass
    del word2vec1
    return embedding_weight


word2vec_path = '../../../../Ek/GoogleNews-vectors-negative300.bin'
embedding_weights = load_word2vec(word2vec_path, len(word2index), word2index)

print('Build model...')
model = TextRNN(maxlen, embedding_dim, batch_size=batch_size, class_num=2, max_features=max_features, epochs=epochs,
                embedding_weights=embedding_weights)

print('Train...')
model.fit(x_train, x_test, y_train, y_test)

print('Test...')
result = model.predict(x_test)
result = np.argmax(np.array(result), axis=1)
y_test = np.argmax(np.array(y_test), axis=1)

print('f1:', f1_score(y_test, result, average='macro'))
print('accuracy:', accuracy_score(y_test, result))
print('classification report:\n', classification_report(y_test, result))
print('confusion matrix:\n', confusion_matrix(y_test, result))

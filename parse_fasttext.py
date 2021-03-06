import re
import numpy as np
import pandas as pd
import h5py
from fastText import load_model
import time

classes = [
    'toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate'
]


def normalize(s):
    """
    Given a text, cleans and normalizes it. Feel free to add your own stuff.
    """
    s = s.lower()
    # Replace ips
    s = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ' _ip_ ', s)
    # Isolate punctuation
    s = re.sub(r'([\'\"\.\(\)\!\?\-\\\/\,])', r' \1 ', s)
    # Remove some special characters
    s = re.sub(r'([\;\:\|•«\n])', ' ', s)
    # Replace numbers and symbols with language
    s = s.replace('&', ' and ')
    s = s.replace('@', ' at ')
    s = s.replace('0', ' zero ')
    s = s.replace('1', ' one ')
    s = s.replace('2', ' two ')
    s = s.replace('3', ' three ')
    s = s.replace('4', ' four ')
    s = s.replace('5', ' five ')
    s = s.replace('6', ' six ')
    s = s.replace('7', ' seven ')
    s = s.replace('8', ' eight ')
    s = s.replace('9', ' nine ')
    return s


def text_to_vector(text, model, window_length):
    """
    Given a string, normalizes it, then splits it into words and finally converts
    it to a sequence of word vectors.
    """
    text = normalize(text)
    words = text.split()
    window = words[-window_length:]
    n_features = model.get_dimension()
    x = np.zeros((window_length, n_features))

    for i, word in enumerate(window):
        x[i, :] = model.get_word_vector(word).astype('float32')

    return x


def df_to_data(df, model, window_length=200):
    """
    Convert a given dataframe to a dataset of inputs for the NN.
    """
    n_features = model.get_dimension()
    x = np.zeros((len(df), window_length, n_features), dtype='float32')

    for i, comment in enumerate(df['comment_text'].values):
        x[i, :] = text_to_vector(comment, model, window_length)

    return x


ft_model = load_model('data/wiki.en.bin')


def parse_file(filepath, hasy=False):
    print('Reading and preprocessing file', filepath)
    df = pd.read_csv(filepath)  # [0:3000]
    df['comment_text'] = df['comment_text'].fillna('_empty_')
    np_array = df_to_data(df, ft_model)

    if hasy:
        np_y = df[classes].values
        return np_array, np_y
    else:
        return np_array


if __name__ == '__main__':
    print('\nLoading FT model', time.time())

    print('load success', time.time())
    parse_file('data/train.csv', hasy=True)
    parse_file('data/test.csv')

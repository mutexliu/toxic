import keras
from keras.layers import Dense, Input, LSTM, Embedding, Bidirectional
from keras.layers import Dropout, BatchNormalization, GlobalMaxPool1D
from keras.layers import Conv1D, GlobalMaxPooling1D, TimeDistributed
from keras.layers import TimeDistributed, Lambda, GRU
from keras.layers.merge import concatenate

from keras import optimizers as k_opt


def get_optimizer(lr, optim_name):
    optimizer = None
    if optim_name == 'nadam':
        optimizer = k_opt.Nadam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=None,
                                schedule_decay=0.004, clipvalue=1, clipnorm=1)
    elif optim_name == 'sgd':
        optimizer = k_opt.SGD(lr=lr, clipvalue=1, clipnorm=1)
    elif optim_name == 'rms':
        optimizer = k_opt.RMSprop(lr=lr, clipvalue=1, clipnorm=1)
    elif optim_name == 'adam':
        optimizer = k_opt.Adam(lr=lr, clipvalue=1, clipnorm=1)
    return optimizer


class BaseModel:
    def __init__(self, data, batch_size):
        self.data = data
        self.batch_size = batch_size
        self.model = None

    def build_model(self):
        return NotImplemented


class BasicLSTM(BaseModel):
    def __init__(self, data, dense_size=50, embed_trainable=False, lr=0.001,
                 optim_name=None, batch_size=64):
        super().__init__(data, batch_size)
        if optim_name is None:
            optim_name = 'nadam'
        self.lr = lr
        self.embed_trainable = embed_trainable
        self.dense_size = dense_size
        self.optim_name = optim_name
        self.build_model()
        self.description = 'LSTM model'

    def build_model(self):
        data = self.data
        inp = Input(shape=(data.seq_length,))
        embed = Embedding(data.max_feature, data.embed_dim,
                          weights=[data.embed_matrix],
                          trainable=self.embed_trainable)(inp)
        lstm = Bidirectional(LSTM(data.embed_dim, return_sequences=True))(embed)
        pool = GlobalMaxPool1D()(lstm)
        dense = Dense(self.dense_size, activation="relu")(pool)
        output = Dense(6, activation="sigmoid")(dense)
        model = keras.models.Model(inputs=inp, outputs=output)
        optimizer = get_optimizer(self.lr, self.optim_name)
        model.compile(loss='binary_crossentropy', optimizer=optimizer,
                      metrics=['accuracy'])
        self.model = model
        model_descirption = f'''BaseLSTM model
        dense_size: {self.dense_size}
        embed_trainbale: {self.embed_trainable}
        lr: {self.lr}
        optim_name: {self.optim_name}
        batch_size: {self.batch_size}'''
        print(model_descirption)
        print(model.summary())


class Lstm(BaseModel):
    def __init__(self, data, dense_size=50, embed_trainable=False, lr=0.001,
                 optim_name=None, batch_size=128, dropout=0.1):
        super().__init__(data, batch_size)
        if optim_name is None:
            optim_name = 'nadam'
        self.lr = lr
        self.embed_trainable = embed_trainable
        self.dense_size = dense_size
        self.optim_name = optim_name
        self.dropout = dropout
        self.build_model()
        self.description = 'LSTM with dropout'

    def build_model(self):
        data = self.data
        inp = Input(shape=(data.seq_length,))
        embed = Embedding(data.max_feature, data.embed_dim,
                          weights=[data.embed_matrix],
                          trainable=self.embed_trainable)(inp)
        lstm = Bidirectional(LSTM(data.embed_dim, return_sequences=True,
                                  dropout=self.dropout,
                                  recurrent_dropout=self.dropout))(embed)
        pool = GlobalMaxPool1D()(lstm)
        bn = BatchNormalization()(pool)
        dense = Dense(self.dense_size, activation="relu")(bn)
        drop = Dropout(self.dropout)(dense)
        output = Dense(6, activation="sigmoid")(drop)
        model = keras.models.Model(inputs=inp, outputs=output)
        optimizer = get_optimizer(self.lr, self.optim_name)
        model.compile(loss='binary_crossentropy', optimizer=optimizer,
                      metrics=['accuracy'])
        self.model = model
        model_descirption = f'''LSTM model
                dense_size: {self.dense_size}
                embed_trainbale: {self.embed_trainable}
                lr: {self.lr}
                optim_name: {self.optim_name}
                batch_size: {self.batch_size}
                dropout: {self.dropout}'''
        print(model_descirption)
        print(model.summary())


class DoubleGRU(BaseModel):
    def __init__(self, data, dense_size=50, embed_trainable=False, lr=0.001,
                 optim_name=None, batch_size=128, dropout=0.1):
        super().__init__(data, batch_size)
        if optim_name is None:
            optim_name = 'nadam'
        self.lr = lr
        self.embed_trainable = embed_trainable
        self.dense_size = dense_size
        self.optim_name = optim_name
        self.dropout = dropout
        self.build_model()
        self.description = 'Double GRU'

    def build_model(self):
        data = self.data
        input_layer = Input(shape=(data.seq_length,))
        embedding_layer = Embedding(data.max_feature, data.embed_dim,
                                    weights=[data.embed_matrix],
                                    trainable=self.embed_trainable)(input_layer)
        x = Bidirectional(GRU(data.embed_dim, return_sequences=True))(
            embedding_layer)
        x = Dropout(self.dropout)(x)
        x = Bidirectional(GRU(data.embed_dim, return_sequences=False))(x)
        x = Dense(self.dense_size, activation="relu")(x)
        output_layer = Dense(6, activation="sigmoid")(x)

        model = keras.models.Model(inputs=input_layer, outputs=output_layer)
        optimizer = get_optimizer(self.lr, self.optim_name)
        model.compile(loss='binary_crossentropy', optimizer=optimizer,
                      metrics=['accuracy'])
        self.model = model
        model_descirption = f'''Double GRU model
                        dense_size: {self.dense_size}
                        embed_trainbale: {self.embed_trainable}
                        lr: {self.lr}
                        optim_name: {self.optim_name}
                        batch_size: {self.batch_size}
                        dropout: {self.dropout}'''
        print(model_descirption)
        print(model.summary())


class CNNModel(BaseModel):
    def __init__(self, data, batch_size=64, embed_trainable=False,
                 kernel_size=3, filter_count=128, lr=0.001,
                 optim_name=None, dense_size=100):
        super().__init__(data, batch_size)
        if optim_name is None:
            optim_name = 'nadam'
        self.optim_name = optim_name
        self.embed_trainable = embed_trainable
        self.filter_count = filter_count
        self.lr = lr
        self.dense_size = dense_size
        self.kernel_size = 3
        self.build_model()
        self.description = 'CNN Model'

    def build_model(self):
        data = self.data
        inputs = Input(shape=(data.seq_length,), dtype='int32')
        x = Embedding(data.max_feature, data.embed_dim,
                      weights=[data.embed_matrix],
                      trainable=self.embed_trainable)(inputs)
        con1 = Conv1D(self.filter_count, self.kernel_size, activation='relu')(x)
        pool1 = GlobalMaxPooling1D()(con1)

        dense1 = Dense(self.dense_size, activation='relu')(pool1)

        output = Dense(units=6, activation='sigmoid')(dense1)

        model = keras.models.Model(inputs=inputs, outputs=output)
        optimizer = get_optimizer(self.lr, self.optim_name)
        model.compile(loss='binary_crossentropy', optimizer=optimizer,
                      metrics=['accuracy'])
        self.model = model

        model_descirption = f'''CNN model
                dense_size: {self.dense_size}
                embed_trainbale: {self.embed_trainable}
                filter_count: {self.filter_count}
                lr: {self.lr}
                kernel_size: {self.kernel_size}
                optim_name: {self.optim_name}
                batch_size: {self.batch_size}'''
        print(model_descirption)
        print(model.summary())


class RCNNModel(BaseModel):
    def __init__(self, data, batch_size=64, embed_trainable=False,
                 lr=0.001, optim_name=None, dense_size=100, dropout=0.1):
        super().__init__(data, batch_size)
        if optim_name is None:
            optim_name = 'nadam'
        self.optim_name = optim_name
        self.embed_trainable = embed_trainable
        self.lr = lr
        self.dense_size = dense_size
        self.dropout = dropout
        self.build_model()
        self.description = 'RCNN Model'

    def build_model(self):
        data = self.data
        maxlen = data.seq_length
        max_features = data.max_feature
        embed_size = data.embed_dim
        embed_matrix = data.embed_matrix
        drop = self.dropout
        dsize = self.dense_size

        document = Input(shape=(maxlen,), dtype="int32")

        def k_slice(x, start, end):
            return x[:, start:end]

        left_1 = Lambda(k_slice, arguments={'start': maxlen - 1,
                                            'end': maxlen})(document)
        left_2 = Lambda(k_slice, arguments={'start': 0,
                                            'end': maxlen - 1})(document)
        left_context = concatenate([left_1, left_2], axis=1)

        right_1 = Lambda(k_slice, arguments={'start': 1,
                                             'end': maxlen})(document)
        right_2 = Lambda(k_slice, arguments={'start': 0, 'end': 1})(document)
        right_context = concatenate([right_1, right_2], axis=1)

        embedder = Embedding(max_features, embed_size,
                             weights=[embed_matrix], trainable=True)

        doc_embedding = embedder(document)
        l_embedding = embedder(left_context)
        r_embedding = embedder(right_context)

        forward = LSTM(embed_size, return_sequences=True,
                       dropout=0.1, recurrent_dropout=drop)(l_embedding)
        backward = LSTM(embed_size, return_sequences=True, go_backwards=True,
                        dropout=0.1, recurrent_dropout=drop)(r_embedding)

        together = concatenate([forward, doc_embedding, backward], axis=2)
        semantic = TimeDistributed(Dense(dsize, activation="tanh"))(together)
        pool_rnn = GlobalMaxPool1D()(semantic)
        output = Dense(6, activation="sigmoid")(pool_rnn)

        model = keras.models.Model(inputs=document, outputs=output)
        optimizer = get_optimizer(self.lr, self.optim_name)
        model.compile(loss='binary_crossentropy', optimizer=optimizer,
                      metrics=['accuracy'])
        self.model = model
        model_descirption = f'''RCNN model
                        dense_size: {self.dense_size}
                        embed_trainbale: {self.embed_trainable}
                        lr: {self.lr}
                        dropout: {self.dropout}
                        optim_name: {self.optim_name}
                        batch_size: {self.batch_size}'''
        print(model_descirption)
        print(model.summary())


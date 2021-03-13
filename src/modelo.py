
from keras.layers import Dense, Conv2D, Input, MaxPooling2D, Flatten
from keras.models import Model
from keras.preprocessing import image

import numpy as np
import io
import cv2 

class Classificador:
    def __init__(self, h5='base_model.h5', nb_class=2, img_h=64, img_w=64):
        self.nb_class = nb_class
        self.img_h = img_h  
        self.img_w = img_w 
        self._definirModelo()
        self.model.load_weights(h5)
        
    def _conv3x3(self, input_x, nb_filters):
        # Prepara a camada convolucional
        return Conv2D(nb_filters, kernel_size=(3,3), use_bias=False,
            activation='relu', padding="same")(input_x)

    def _definirModelo(self, img_h=64, img_w=64):
            self.inputs = Input(shape=(img_h, img_w, 1))
            x = self._conv3x3(self.inputs, 32)
            x = self._conv3x3(x, 32)
            x = MaxPooling2D(pool_size=(2,2))(x) 
            x = self._conv3x3(x, 64)
            x = self._conv3x3(x, 64)
            x = MaxPooling2D(pool_size=(2,2))(x) 
            x = self._conv3x3(x, 128)
            x = MaxPooling2D(pool_size=(2,2))(x) 
            x = Flatten()(x)
            x = Dense(128, activation="relu")(x)
            self.preds = Dense(self.nb_class, activation='softmax')(x)
            self.model = Model(inputs=self.inputs, outputs=self.preds)

    def _prepararImagem(self, imagem):
        test_image = image.img_to_array(imagem.T)
        test_image = np.expand_dims(test_image, axis = 0)    
        return test_image

    def _mostraCateg(self, resultado):
        categs = ["Tende a ter", "Tende a nao ter"]
        for idx, val in enumerate(resultado[0]):
            if val == 1:
                return categs[idx]

    def _converteBytesToImage(self, data):
        nparr = np.fromstring(data, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img_np

    def predicao(self, image_bytes):
        im = self._converteBytesToImage(image_bytes)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        imres = cv2.resize(gray, (self.img_h, self.img_w), interpolation=cv2.INTER_CUBIC)
        dados = self._prepararImagem(imres)
        ret = self.model.predict(dados, batch_size=1)  
        # print('resultado : ', ret[0][1])
        # print(self._mostraCateg(ret))
        # print('predicao')
        return ret[0][1]

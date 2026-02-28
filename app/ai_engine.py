import numpy as np
from PIL import ImageOps
from keras.models import load_model

class AIEngine:

    def __init__(self):

        self.model = load_model(
            "models/keras_model.h5",
            compile=False
        )

        with open("models/labels.txt") as f:
            self.labels = [x.strip() for x in f]

    def predict(self, image):

        image = ImageOps.fit(image,(224,224))

        arr = np.asarray(image)
        arr = (arr.astype(np.float32)/127.5)-1

        data = np.expand_dims(arr,0)

        prediction = self.model.predict(data, verbose=0)

        index = np.argmax(prediction)

        return {
            "label": self.labels[index],
            "confidence": float(prediction[0][index])
        }

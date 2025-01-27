import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

from pykopt.KerasOptimizer import KerasOptimizer
from pykopt.Strategy import Strategy
from pykopt.operator import crossover, selection

num_classes = 10


def train(model, hyperparams):
    # the data, split between train and test sets
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

    print(hyperparams)

    # Scale images to the [0, 1] range
    x_train = x_train.astype("float32") / 255
    x_test = x_test.astype("float32") / 255
    # Make sure images have shape (28, 28, 1)
    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)
    print("x_train shape:", x_train.shape)
    print(x_train.shape[0], "train samples")
    print(x_test.shape[0], "test samples")

    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    batch_size = hyperparams.batch_size
    epochs = hyperparams.epochs

    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)

    return history.history['val_accuracy']


def run():
    input_shape = (28, 28, 1)

    model = keras.Sequential(
        [
            keras.Input(shape=input_shape),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    optimizer = KerasOptimizer(model=model,
                               max_iteration=2,
                               initial_population=2,
                               mutation_probability=0.01,
                               crossover_prob=0.7,
                               train_function=train,
                               strategy=Strategy.MAXIMIZE,
                               crossover_method=crossover.one_point,
                               selection_method=selection.tournament_selection)

    optimizer.set_hyperparameters(batch_size=[16, 32], epochs=[1, 2], learning_rate=[0.001, 0.01])
    stats = optimizer.run()
    print("Stats: ", stats.best_params)


if __name__ == '__main__':
    run()

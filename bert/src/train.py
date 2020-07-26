import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import lightgbm as lgb
from tensorflow import keras


class Train:
    def __init__(self, path="..\\data\\interim\\df.pkl", input_dim=300):
        self.path = path
        self.input_dim = input_dim
        self.__df = self.__load_df()
        self.X_train, self.X_test, self.y_train, self.y_test = \
            self.__create_data()

    def __load_df(self):
        return pd.read_pickle(self.path)

    def __create_data(self, test_ratio=0.2, seed=2019,
                      col_appeal="AppealPoint",
                      col_vector="Vector"):

        # separate data to train and test data
        __X_train, __X_test, __y_train, __y_test = \
            train_test_split(self.__df[col_vector], self.__df[col_appeal],
                             test_size=test_ratio, random_state=seed)

        __X_train_data = self.__df.iloc[__X_train.index]
        __X_test_data = self.__df.iloc[__X_test.index]
        __y_train_data = self.__df.iloc[__y_train.index]
        __y_test_data = self.__df.iloc[__y_test.index]

        X_train = self.__create_data_x(__X_train_data)
        X_test = self.__create_data_x(__X_test_data)
        y_train = self.__create_data_y(__y_train_data)
        y_test = self.__create_data_y(__y_test_data)

        return X_train, X_test, y_train, y_test

    def __create_data_x(self, data: pd.DataFrame,
                        col_vector="Vector") -> list:
        __X_ = np.array([])
        for vectors in data[col_vector]:
            for vector in vectors.values():
                __X_ = np.append(__X_, vector)
        __X = __X_.reshape(-1, self.input_dim)
        return __X

    def __create_data_y(self, data: pd.DataFrame,
                        col_appeal="AppealPoint",
                        col_length="VideoLength") -> list:
        __y = np.array([])
        for point, length in zip(data[col_appeal], data[col_length]):
            arr = np.zeros(length+1)
            arr[point] = 1
            __y = np.append(__y, arr)
        return __y

    def train_logistic(self):
        model = LogisticRegression()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        return self.__get_score(y_pred, model="logi")

    def train_lgb(self, objective="binary", metric="logloss"):
        lgb_train = lgb.Dataset(self.X_train, self.y_train)
        lgb_eval = lgb.Dataset(self.X_test, self.y_test,
                               reference=lgb_train)
        lgbm_params = {'objective': objective, 'metric': metric}
        model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)
        y_pred_proba = model.predict(self.X_test,
                                     num_iteration=model.best_iteration)
        y_pred = np.where(y_pred_proba > 0.5, 1, 0)
        return self.__get_score(y_pred, model="lgb")

    def train_xgb(self, objective="binary:logistic", eval_metric="logloss"):
        dtrain = xgb.DMatrix(self.X_train, label=self.y_train)
        dtest = xgb.DMatrix(self.X_test, label=self.y_test)
        params = {'objective': objective,
                  'eval_metric': eval_metric}
        model = xgb.train(params, dtrain, num_boost_round=100)
        y_pred_proba = model.predict(dtest)
        y_pred = np.where(y_pred_proba > 0.5, 1, 0)
        return self.__get_score(y_pred, model="xgb")

    def train_nn(self, optimizer="adam", loss="binary_crossentropy",
                 metrics=["accuracy"], epochs=10, batch_size=32):
        # Layers which you could set some parameters, number of nodes etc
        model = keras.Sequential([
                    keras.layers.Dense(128, activation="relu",
                                       input_dim=self.input_dim),
                    keras.layers.Dense(64, activation='relu'),
                    keras.layers.Dense(64, activation='relu'),
                    keras.layers.Dense(1, activation='sigmoid')])
        model.compile(optimizer=optimizer,
                      loss=loss,
                      metrics=metrics)
        model.fit(self.X_train, self.y_train, epochs=epochs,
                  batch_size=batch_size)
        y_pred_proba = model.predict(self.X_test)
        y_pred = np.where(y_pred_proba > 0.5, 1, 0)
        return self.__get_score(y_pred, model="nn")

    def __get_score(self, y_pred, model):
        __tn, __fp, __fn, __tp = \
            confusion_matrix(y_true=self.y_test, y_pred=y_pred).flatten()
        score = {"confusion_matrix": str({"TP": __tp, "FP": __fp,
                                          "TN": __tn, "FN": __fn}),
                 "accuracy": accuracy_score(y_true=self.y_test,
                                            y_pred=y_pred),
                 "precision": precision_score(y_true=self.y_test,
                                              y_pred=y_pred),
                 "recall": recall_score(y_true=self.y_test,
                                        y_pred=y_pred),
                 "f1": f1_score(y_true=self.y_test, y_pred=y_pred)}
        return pd.DataFrame(score, index=[f"{model}"])

    def damp_score(self, df: pd.DataFrame, version="v0.1",
                   path_dir="..\\log\\"):
        filename = f"score_{version}.csv"
        path = path_dir + filename
        df.to_csv(path)

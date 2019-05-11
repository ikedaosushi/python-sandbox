from functools import partial

import optuna
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import pandas as pd


def objective(X, y, trial):
    params = {
        'kernel': trial.suggest_categorical('kernel', ['rbf', 'sigmoid']),
        'C': trial.suggest_loguniform('C', 1e+0, 1e+2),
        'gamma': trial.suggest_loguniform('gamma', 1e-2, 1e+1),
    }

    model = SVC(**params)

    kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    scores = cross_validate(model, X=X, y=y, cv=kf)
    return 1.0 - scores['test_score'].mean()

if __name__ == "__main__":
    # データ読み込み
    data = pd.read_csv("~/.kaggle/competitions/titanic/train.csv")
    X = data[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Cabin', 'Embarked']]
    X = pd.get_dummies(X, columns=['Pclass', 'Sex', 'SibSp', 'Parch', 'Cabin', 'Embarked']).fillna(0)
    y = data['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)

    # デフォルト
    default_model = SVC()
    default_model.fit(X_train, y_train)
    print(default_model.score(X_test, y_test))
    # => 0.69

    # OptunaでHyperParamer探索
    f = partial(objective, X_train, y_train)
    study = optuna.create_study()
    study.optimize(f, n_trials=100)
    # [I 2019-05-11 18:17:09,431] Finished trial#99 resulted in value: 0.47059004326010623. Current best value is 0.18394898478806176 with parameters: {'kernel': 'rbf', 'C': 7.660525691175324, 'gamma': 0.013116664828190997}.

    # 最適化Parameter
    op_model = SVC(**study.best_params)
    op_model.fit(X_train, y_train)
    print(op_model.score(X_test, y_test))
    # => 0.815
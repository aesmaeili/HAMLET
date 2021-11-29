from sklearn.model_selection import train_test_split
from sklearn import datasets
import inspect
from loguru import logger
from sklearn.preprocessing import MinMaxScaler

TEST_SIZE = 0.4


class iris_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def iris(trnORtst="train", return_X_y=False):
    if iris_data.X_train is None:
        data = datasets.load_iris(return_X_y)
        if isinstance(data, tuple):
            iris_data.X_all = data[0]
            iris_data.y_all = data[1]
        else:
            iris_data.X_all = data.data
            iris_data.y_all = data.target
        (
            iris_data.X_train,
            iris_data.X_test,
            iris_data.y_train,
            iris_data.y_test,
        ) = train_test_split(
            iris_data.X_all, iris_data.y_all, test_size=TEST_SIZE, random_state=0
        )
    if trnORtst == "train":
        return iris_data.X_train, iris_data.y_train
    elif trnORtst == "test":
        return iris_data.X_test, iris_data.y_test
    elif trnORtst == "all":
        return iris_data.X_all, iris_data.y_all


class wine_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def wine(trnORtst="train", return_X_y=False):
    if wine_data.X_train is None:
        data = datasets.load_wine(return_X_y)
        if isinstance(data, tuple):
            wine_data.X_all = data[0]
            wine_data.y_all = data[1]
        else:
            wine_data.X_all = data.data
            wine_data.y_all = data.target
        (
            wine_data.X_train,
            wine_data.X_test,
            wine_data.y_train,
            wine_data.y_test,
        ) = train_test_split(
            wine_data.X_all, wine_data.y_all, test_size=TEST_SIZE, random_state=0
        )
    if trnORtst == "train":
        return wine_data.X_train, wine_data.y_train
    elif trnORtst == "test":
        return wine_data.X_test, wine_data.y_test
    elif trnORtst == "all":
        return wine_data.X_all, wine_data.y_all


class digits_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def digits(trnORtst="train", n_class=10, return_X_y=False):
    if digits_data.X_train is None:
        data = datasets.load_digits(n_class, return_X_y)
        if isinstance(data, tuple):
            digits_data.X_all = data[0]
            digits_data.y_all = data[1]
        else:
            digits_data.X_all = data.data
            digits_data.y_all = data.target
        (
            digits_data.X_train,
            digits_data.X_test,
            digits_data.y_train,
            digits_data.y_test,
        ) = train_test_split(
            digits_data.X_all, digits_data.y_all, test_size=TEST_SIZE, random_state=0
        )
    if trnORtst == "train":
        return digits_data.X_train, digits_data.y_train
    elif trnORtst == "test":
        return digits_data.X_test, digits_data.y_test
    elif trnORtst == "all":
        return digits_data.X_all, digits_data.y_all


class breast_cancer_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def breast_cancer(trnORtst="train", return_X_y=False):
    if breast_cancer_data.X_train is None:
        data = datasets.load_breast_cancer(return_X_y)
        if isinstance(data, tuple):
            breast_cancer_data.X_all = data[0]
            breast_cancer_data.y_all = data[1]
        else:
            breast_cancer_data.X_all = data.data
            breast_cancer_data.y_all = data.target
        (
            breast_cancer_data.X_train,
            breast_cancer_data.X_test,
            breast_cancer_data.y_train,
            breast_cancer_data.y_test,
        ) = train_test_split(
            breast_cancer_data.X_all,
            breast_cancer_data.y_all,
            test_size=TEST_SIZE,
            random_state=0,
        )
    if trnORtst == "train":
        return breast_cancer_data.X_train, breast_cancer_data.y_train
    elif trnORtst == "test":
        return breast_cancer_data.X_test, breast_cancer_data.y_test
    elif trnORtst == "all":
        return breast_cancer_data.X_all, breast_cancer_data.y_all


class make_classification_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def make_classification(
    trnORtst="train",
    n_samples=100,
    n_features=20,
    n_informative=2,
    n_redundant=2,
    n_repeated=0,
    n_classes=2,
    n_clusters_per_class=2,
    weights=None,
    flip_y=0.01,
    class_sep=1.0,
    hypercube=True,
    shift=0.0,
    scale=1.0,
    shuffle=True,
    random_state=None,
):
    if make_classification_data.X_train is None:
        data = datasets.make_classification(
            n_samples,
            n_features,
            n_informative,
            n_redundant,
            n_repeated,
            n_classes,
            n_clusters_per_class,
            weights,
            flip_y,
            class_sep,
            hypercube,
            shift,
            scale,
            shuffle,
            random_state,
        )
        if isinstance(data, tuple):
            make_classification_data.X_all = data[0]
            make_classification_data.y_all = data[1]
        else:
            make_classification_data.X_all = data.data
            make_classification_data.y_all = data.target
        scaler = MinMaxScaler()
        make_classification_data.X_all = scaler.fit_transform(
            make_classification_data.X_all
        )
        (
            make_classification_data.X_train,
            make_classification_data.X_test,
            make_classification_data.y_train,
            make_classification_data.y_test,
        ) = train_test_split(
            make_classification_data.X_all,
            make_classification_data.y_all,
            test_size=TEST_SIZE,
            random_state=0,
        )
    if trnORtst == "train":
        return make_classification_data.X_train, make_classification_data.y_train
    elif trnORtst == "test":
        return make_classification_data.X_test, make_classification_data.y_test
    elif trnORtst == "all":
        return make_classification_data.X_all, make_classification_data.y_all


class boston_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def boston(trnORtst="train", return_X_y=False):
    if boston_data.X_train is None:
        data = datasets.load_boston(return_X_y)
        if isinstance(data, tuple):
            boston_data.X_all = data[0]
            boston_data.y_all = data[1]
        else:
            boston_data.X_all = data.data
            boston_data.y_all = data.target
        (
            boston_data.X_train,
            boston_data.X_test,
            boston_data.y_train,
            boston_data.y_test,
        ) = train_test_split(
            boston_data.X_all, boston_data.y_all, test_size=TEST_SIZE, random_state=0
        )
    if trnORtst == "train":
        return boston_data.X_train, boston_data.y_train
    elif trnORtst == "test":
        return boston_data.X_test, boston_data.y_test
    elif trnORtst == "all":
        return boston_data.X_all, boston_data.y_all


class diabetes_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def diabetes(trnORtst="train", return_X_y=False):
    if diabetes_data.X_train is None:
        data = datasets.load_diabetes(return_X_y)
        if isinstance(data, tuple):
            diabetes_data.X_all = data[0]
            diabetes_data.y_all = data[1]
        else:
            diabetes_data.X_all = data.data
            diabetes_data.y_all = data.target
        (
            diabetes_data.X_train,
            diabetes_data.X_test,
            diabetes_data.y_train,
            diabetes_data.y_test,
        ) = train_test_split(
            diabetes_data.X_all,
            diabetes_data.y_all,
            test_size=TEST_SIZE,
            random_state=0,
        )
    if trnORtst == "train":
        return diabetes_data.X_train, diabetes_data.y_train
    elif trnORtst == "test":
        return diabetes_data.X_test, diabetes_data.y_test
    elif trnORtst == "all":
        return diabetes_data.X_all, diabetes_data.y_all


class make_regression_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def make_regression(
    trnORtst="train",
    n_samples=100,
    n_features=100,
    n_informative=10,
    n_targets=1,
    bias=0.0,
    effective_rank=None,
    tail_strength=0.5,
    noise=0.0,
    shuffle=True,
    coef=False,
    random_state=None,
):
    if make_regression_data.X_train is None:
        data = datasets.make_regression(
            n_samples,
            n_features,
            n_informative,
            n_targets,
            bias,
            effective_rank,
            tail_strength,
            noise,
            shuffle,
            coef,
            random_state,
        )
        if isinstance(data, tuple):
            make_regression_data.X_all = data[0]
            make_regression_data.y_all = data[1]
        else:
            make_regression_data.X_all = data.data
            make_regression_data.y_all = data.target
        (
            make_regression_data.X_train,
            make_regression_data.X_test,
            make_regression_data.y_train,
            make_regression_data.y_test,
        ) = train_test_split(
            make_regression_data.X_all,
            make_regression_data.y_all,
            test_size=TEST_SIZE,
            random_state=0,
        )
    if trnORtst == "train":
        return make_regression_data.X_train, make_regression_data.y_train
    elif trnORtst == "test":
        return make_regression_data.X_test, make_regression_data.y_test
    elif trnORtst == "all":
        return make_regression_data.X_all, make_regression_data.y_all


class make_moons_data:
    X_train = None
    X_test = None
    y_train = None
    y_test = None
    X_all = None
    y_all = None


def make_moons(
    trnORtst="train", n_samples=100, shuffle=True, noise=None, random_state=None,
):

    if make_moons_data.X_train is None:
        data = datasets.make_moons(n_samples, shuffle, noise, random_state,)
        if isinstance(data, tuple):
            make_moons_data.X_all = data[0]
            make_moons_data.y_all = data[1]
        else:
            make_moons_data.X_all = data.data
            make_moons_data.y_all = data.target
        scaler = MinMaxScaler()
        make_moons_data.X_all = scaler.fit_transform(make_moons_data.X_all)
        (
            make_moons_data.X_train,
            make_moons_data.X_test,
            make_moons_data.y_train,
            make_moons_data.y_test,
        ) = train_test_split(
            make_moons_data.X_all,
            make_moons_data.y_all,
            test_size=TEST_SIZE,
            random_state=0,
        )
    if trnORtst == "train":
        return make_moons_data.X_train, make_moons_data.y_train
    elif trnORtst == "test":
        return make_moons_data.X_test, make_moons_data.y_test
    elif trnORtst == "all":
        return make_moons_data.X_all, make_moons_data.y_all

from query import *



classification_train_query = CompoundQuery(
    "Classification-Train-" + ID.queryID(),
    typ="train",
    algorithms=[
        {
            "SVC": {
                "params": {("kernel", "linear"),},  
                "kb": "sklearn.svm",
                "role": ModelTypes.CLAS,
            }
        },
        {
            "SVC": {
                "params": {("kernel", "sigmoid"),},
                "kb": "sklearn.svm",
                "role": ModelTypes.CLAS,
            }
        },
        
        {
            "SVC": {
                "params": {("gamma", 0.001),},
                "kb": "sklearn.svm",
                "role": ModelTypes.CLAS,
            }
        },
        {
            "SVC": {
                "params": {("C", 100), ("gamma", 0.001),},
                "kb": "sklearn.svm",
                "role": ModelTypes.CLAS,
            }
        },
        {"NuSVC": {"params": set(), "kb": "sklearn.svm", "role": ModelTypes.CLAS,}},
        {
            "ComplementNB": {
                "params": set(),
                "kb": "sklearn.naive_bayes",
                "role": ModelTypes.CLAS,
            }
        },
        {
            "DecisionTreeClassifier": {
                "params": set(),
                "kb": "sklearn.tree",
                "role": ModelTypes.CLAS,
            }
        },
        {
            "NearestCentroid": {
                "params": set(),
                "kb": "sklearn.neighbors",
                "role": ModelTypes.CLAS,
            }
        },
        
    ],
    data=[
        {"iris": {"params": {}, "kb": "knowledgbase"}},
        {"wine": {"params": {}, "kb": "knowledgbase"}},
        {"digits": {"params": {}, "kb": "knowledgbase"}},
        {"breast_cancer": {"params": {}, "kb": "knowledgbase"}},
        {
            "make_classification": {
                "params": {
                    ("n_samples", 900),
                    ("n_classes", 3),
                    ("n_clusters_per_class", 3),
                    ("n_informative", 5),
                    ("random_state", 0),
                },
                "kb": "knowledgbase",
            }
        },
        {
            "make_moons": {
                "params": {("n_samples", 500), ("noise", 0.2), ("random_state", 0),},
                "kb": "knowledgbase",
            }
        },
    ],
    configs={
        "output": {"eval": ["accuracy_score"]},
        "evals": [
            "roc_auc_score",
            "precision_score",
            "recall_score",
            "average_precision_score",
            "accuracy_score",
            "f1_score",
        ],
    },
)

regression_train_query = CompoundQuery(
    "Regression-Train-" + ID.queryID(),
    typ="train",
    algorithms=[
        {
            "LinearRegression": {
                "params": {},
                "kb": "sklearn.linear_model",
                "role": ModelTypes.REGR,
            }
        },
        {
            "Ridge": {
                "params": {("fit_intercept", False)},
                "kb": "sklearn.linear_model",
                "role": ModelTypes.REGR,
            }
        },
        {
            "Ridge": {
                "params": {("alpha", 0.5)},
                "kb": "sklearn.linear_model",
                "role": ModelTypes.REGR,
            }
        },
        {
            "KernelRidge": {
                "params": {},
                "kb": "sklearn.kernel_ridge",
                "role": ModelTypes.REGR,
            }
        },
        {
            "Lasso": {
                "params": {("alpha", 0.1)},
                "kb": "sklearn.linear_model",
                "role": ModelTypes.REGR,
            }
        },
        
        {"NuSVR": {"params": {}, "kb": "sklearn.svm", "role": ModelTypes.REGR}},
        {
            "NuSVR": {
                "params": {("nu", 0.1)},
                "kb": "sklearn.svm",
                "role": ModelTypes.REGR,
            }
        },
        {
            "ElasticNet": {
                "params": {("random_state", 0)},
                "kb": "sklearn.linear_model",
                "role": ModelTypes.REGR,
            }
        },
    ],
    data=[
        {"boston": {"params": {}, "kb": "knowledgbase"}},
        {"diabetes": {"params": {}, "kb": "knowledgbase"}},
        {
            "make_regression": {
                "params": {
                    ("n_samples", 200),
                    ("noise", 0.1),
                    ("n_features", 20),
                    ("random_state", 0),
                },
                "kb": "knowledgbase",
            }
        },
        
    ],
    configs={
        "output": {"eval": ["mean_squared_error"]},
        "evals": [
            "explained_variance_score",
            "max_error",
            "r2_score",
            "mean_squared_log_error",
            "mean_absolute_error",
            "mean_squared_error",
        ],
    },
)

clustering_query = CompoundQuery(
    "Clustring-" + ID.queryID(),
    typ="train",
    algorithms=[
        {
            "KMeans": {
                "params": {("n_clusters", "auto")},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        {
            "KMeans": {
                "params": {("n_clusters", "auto"), ("algorithm", "full")},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        {
            "MiniBatchKMeans": {
                "params": {},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        {"DBSCAN": {"params": {}, "kb": "sklearn.cluster", "role": ModelTypes.CLUS,}},
        {
            "DBSCAN": {
                "params": {("metric", "cityblock")},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        {
            "DBSCAN": {
                "params": {("metric", "cosine")},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        {"Birch": {"params": {}, "kb": "sklearn.cluster", "role": ModelTypes.CLUS,}},
        {
            "AgglomerativeClustering": {
                "params": {("n_clusters", "auto")},
                "kb": "sklearn.cluster",
                "role": ModelTypes.CLUS,
            }
        },
        
    ],
    data=[
        {"iris": {"params": {("trnORtst", "all")}, "kb": "knowledgbase"}},
        {"wine": {"params": {("trnORtst", "all")}, "kb": "knowledgbase"}},
        {"digits": {"params": {("trnORtst", "all")}, "kb": "knowledgbase"}},
        {"breast_cancer": {"params": {("trnORtst", "all")}, "kb": "knowledgbase"}},
        {
            "make_classification": {
                "params": {
                    ("n_samples", 900),
                    ("n_classes", 3),
                    ("n_clusters_per_class", 3),
                    ("n_informative", 5),
                    ("random_state", 0),
                    ("trnORtst", "all"),
                },
                "kb": "knowledgbase",
            }
        },
        {
            "make_moons": {
                "params": {
                    ("n_samples", 500),
                    ("noise", 0.2),
                    ("random_state", 0),
                    ("trnORtst", "all"),
                },
                "kb": "knowledgbase",
            }
        },
    ],
    configs={
        "output": {"eval": ["fowlkes_mallows_score"]},
        "evals": [
            "adjusted_rand_score",  # Extrinsic when ground true labels are known
            "adjusted_mutual_info_score",  # Extrinsic
            "homogeneity_score",  # Extrinsic
            "completeness_score",  # Extrinsic
            "v_measure_score",  # Extrinsic
            "fowlkes_mallows_score",  # intrinsic, when ground true labels are known
        ],
    },
)


add_data_query = CompoundQuery(
    "Add-Data-" + ID.queryID(),
    typ="add_data",
    algorithms=None,
    data=[
        {"iris": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {"wine": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {"digits": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {
            "make_classification": {
                "params": {
                    ("n_samples", 900),
                    ("n_classes", 3),
                    ("n_clusters_per_class", 3),
                    ("n_informative", 5),
                    ("random_state", 0),
                    ("trnORtst", "test"),
                },
                "kb": "knowledgbase",
            }
        },
        {
            "make_moons": {
                "params": {
                    ("n_samples", 500),
                    ("noise", 0.2),
                    ("random_state", 0),
                    ("trnORtst", "test"),
                },
                "kb": "knowledgbase",
            }
        },
        {"breast_cancer": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {"boston": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {"diabetes": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {
            "make_regression": {
                "params": {
                    ("n_samples", 200),
                    ("noise", 0.1),
                    ("n_features", 20),
                    ("random_state", 0),
                    ("trnORtst", "test"),
                },
                "kb": "knowledgbase",
            }
        },
    ],
    configs=None,
)

test1 = CompoundQuery(
    "Test-Query-1-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": {("kernel", "rbf")}, "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score", "mean_squared_error"]}},
)

test2 = CompoundQuery(
    "Test-Query-2-" + ID.queryID(),
    typ="test",
    algorithms=[{"SVC": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"breast_cancer": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score", "roc_auc_score"]}},
)
test3 = CompoundQuery(
    "Test-Query-3-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"make_moons": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={
        "output": {
            "eval": ["accuracy_score", "mean_squared_error", "homogeneity_score"]
        }
    },
)

test4 = CompoundQuery(
    "Test-Query-4-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={
        "output": {
            "eval": ["accuracy_score", "mean_squared_error", "homogeneity_score"]
        }
    },
)

gen_test_query1 = CompoundQuery(
    "Gen-Test-1-" + ID.queryID(),
    typ="test",
    algorithms=[
        {"SVC": {"params": {("C", 100), ("gamma", 0.001)}, "kb": "sklearn.svm",}},
        {"SVC": {"params": {}, "kb": "sklearn.svm",}},
    ],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}}],
    configs={"output": {"eval": ["accuracy_score"]}},
)

gen_test_query2 = CompoundQuery(
    "Gen-Test-2-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"iris": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score"]}},
)

gen_test_query3 = CompoundQuery(
    "Gen-Test-3-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}}],
    configs={"output": {"eval": ["accuracy_score"]}},
)
gen_test_query4 = CompoundQuery(
    "Gen-Test-4-" + ID.queryID(),
    typ="test",
    algorithms=[{"SVC": {"params": {("C", "*")}, "kb": "sklearn.svm",}},],
    data=[{"iris": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score"]}},
)

gen_test_query5 = CompoundQuery(
    "Gen-Test-5-" + ID.queryID(),
    typ="test",
    algorithms=[{"SVC": {"params": {("C", "*")}, "kb": "sklearn.svm",}},],
    data=[{"iris": {"params": {("trnORtst", "*")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score"]}},
)
gen_test_query6 = CompoundQuery(
    "Gen-Test-6-" + ID.queryID(),
    typ="test",
    algorithms=[
        {"*": {"params": set(), "kb": "sklearn.svm", "role": ModelTypes.CLAS}},
    ],
    data=[{"*": {"params": {("trnORtst", "*")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score", "mean_squared_error"]}},
)

gen_test_query7 = CompoundQuery(
    "Gen-Test-7-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "*")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score", "mean_squared_error"]}},
)

test_query = CompoundQuery(
    "Test-" + ID.queryID(),
    typ="test",
    algorithms=[
        {"SVC": {"params": {("C", 100), ("gamma", 0.001)}, "kb": "sklearn.svm",}},
        {"SVC": {"params": set(), "kb": "sklearn.svm",}},
        {"SVC": {"params": {("C", 20), ("gamma", 0.01)}, "kb": "sklearn.svm",}},
        {"SVC": {"params": {("gamma", 0.1)}, "kb": "sklearn.svm",}},
        {"DecisionTreeClassifier": {"params": set(), "kb": "sklearn.tree",}},
        {"NearestCentroid": {"params": set(), "kb": "sklearn.neighbors",}},
    ],
    data=[
        {"iris": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {"digits": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
        {
            "make_classification": {
                "params": {("trnORtst", "test")},
                "kb": "knowledgbase",
            }
        },
        
        {"breast_cancer": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},
    ],
    configs={"output": {"eval": ["accuracy_score"]}},
)


test_query1 = CompoundQuery(
    "Test-1-" + ID.queryID(),
    typ="test",
    algorithms=[{"SVC": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score",]}},
)

test_query2 = CompoundQuery(
    "Test-2-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": {("kernel", "rbf")}, "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score",]}},
)

test_query3 = CompoundQuery(
    "Test-3-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": {("gamma", 0.001)}, "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score",]}},
)

test_query4 = CompoundQuery(
    "Test-4-" + ID.queryID(),
    typ="test",
    algorithms=[{"*": {"params": set(), "kb": "sklearn.svm",}},],
    data=[{"*": {"params": {("trnORtst", "test")}, "kb": "knowledgbase"}},],
    configs={"output": {"eval": ["accuracy_score",]}},
)

import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt


class Structure:
    G = nx.Graph()
    ig = ig.Graph()
    count = 0
    fig = None
    started = False
    all_agents = []

    @staticmethod
    def plot():
        # Structure.fig = plt.figure(1)
        # plt.ion()
        # plt.show()
        pass


class VConfigs:
    system_node_color = "darkred"
    data_abstract_node_color = "green"
    algorithm_abstract_node_color = "blue"
    algorithm_node_color = "royalblue"
    data_node_color = "limegreen"
    data_node_shape = "s"
    model_node_color = "orange"
    normal_edge_color = "black"
    normal_edge_weight = 1
    normal_edge_style = "solid"
    model_edge_color = "orange"
    model_edge_weight = 1
    model_edge_style = "dotted"
    save_dir = "Plots"
    visualized = False
    plot_style = "seaborn-paper"  # "seaborn-bright"


class DF:
    sys_jid = None


class ID:
    _alg_count = 0
    _atm_alg_count = 0
    _dat_count = 0
    _mod_count = 0
    _query_count = 0

    @staticmethod
    def algID():
        ID._alg_count += 1
        return "ALG" + str(ID._alg_count)

    @staticmethod
    def atmAlgID():
        ID._atm_alg_count += 1
        return "A" + "{:02d}".format(ID._atm_alg_count)

    @staticmethod
    def datID():
        ID._dat_count += 1
        return "DATA" + str(ID._dat_count)

    @staticmethod
    def modID():
        ID._mod_count += 1
        return "MOD" + str(ID._mod_count)

    @staticmethod
    def queryID():
        ID._query_count += 1
        return "Q" + str(ID._query_count)


class Roles:
    SYS = "System"
    DATA = "Data"
    ALG = "Algorithm"
    ABS = "Abstract"


class Addresses:
    SYS = "SYS@localhost"  # the address of the system
    DATA = "DATA@localhost"  # the address of the data sub-system
    ALGS = "ALGS@localhost"  # the address of the algorithms sub-system


class Protocols:
    CNP = "Contract_Net_Protocol"
    VER = "Verification"
    QRY = "Query"
    MIN = "Mining"
    TRN = "Train"
    TST = "Test"
    REQ = "Request"
    RES = "Results"
    VIZ = "Visualization"


class Performatives:
    INF = "inform"
    QRY = "query"
    RES = "result"
    CFP = "call_for_proposal"
    ERR = "error"
    PRF = "perform"
    PRM = "permission"
    ACS = "access"
    CNT = "content"
    VIZ = "visualize"
    RFZ = "refuse"
    NON = "none"
    CHK = "check"
    PPZ = "proposal"
    ADD = "address"
    UPV = "update_value"
    TRN = "train"
    TST = "test"
    DAD = "add_data"
    RSP = "response"
    STR = "structure"


class Comparison:
    LES = -1
    EQU = 0
    GRT = 1


class Constants:
    GENERAL_CHAR = "*"
    ALPHA = 0.5
    BETA = 0.1


class ModelTypes:
    CLAS = "classifier"
    REGR = "regression"
    CLUS = "clustering"

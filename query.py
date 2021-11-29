from helping import *


class Query:
    def __init__(self, qid, typ, algorithms, data, configs):
        """Constructor
        
        Arguments:
            qid {str} -- the if of the query
            algorithms {dic} -- the names and parameters of algorithms in form {name:{params:{(p,v)}, kb:KB}}
            data {dic} -- the names and parameters of data in form {name:{params:{(p,v)}, kb:KB}}
            configs {dict} -- a dictionary containign the configs of model like measures we expect in the output
        """

        self.qid = qid
        self.algorithms = algorithms
        self.data = data
        self.configs = configs
        aname = ""
        dname = ""
        if not algorithms is None:
            aname = next(iter(algorithms)) + "\n"
            for p in algorithms[next(iter(algorithms))]["params"]:
                aname += str(p) + "\n"
        if not data is None:
            dname = next(iter(data)) + "\n"
            for p in data[next(iter(data))]["params"]:
                dname += str(p) + "\n"
        self.alg_name = aname
        self.data_name = dname
        self.type = typ

    def to_dict(self):
        query_dict = {}
        query_dict["qid"] = self.qid
        query_dict["algorithms"] = self.algorithms
        query_dict["data"] = self.data
        query_dict["configs"] = self.configs
        query_dict["alg_name"] = self.alg_name
        query_dict["data_name"] = self.data_name
        query_dict["type"] = self.type

        return query_dict

    def complete(self):
        comp_algs = set()
        comp_data = set()
        if not self.algorithms is None:
            for k, v in self.algorithms.items():
                comp_algs = complete_params(
                    module=v["kb"], func=k, params_set=v["params"]
                )
                self.algorithms[k]["params"] = comp_algs
        if not self.data is None:
            for k, v in self.data.items():
                comp_data = complete_params(
                    module=v["kb"], func=k, params_set=v["params"]
                )
                self.data[k]["params"] = comp_data


class CompoundQuery:
    def __init__(self, qid, typ, algorithms, data, configs):
        """Constructor
        
        Arguments:
            qid {str} -- the if of the query
            algorithms {list} -- the names and parameters of algorithms in form {name:{params:{(p,v)}, kb:KB}}
            data {list} -- the names and parameters of data in form {name:{params:{(p,v)}, kb:KB}}
            configs {dict} -- a dictionary containign the configs of model like measures we expect in the output
        """

        self.qid = qid
        self.algorithms = algorithms
        self.data = data
        self.configs = configs
        self.type = typ

    def breakup(self):
        sub_queries = []
        a_c = 0
        if self.type == "add_data":
            d_c = 0
            for d in self.data:
                d_c += 1
                q_id = "add" + str(a_c) + "&data" + str(d_c) + "_" + self.qid
                q = Query(
                    q_id, typ=self.type, algorithms=None, data=d, configs=self.configs
                )
                sub_queries.append(q)
        else:
            for a in self.algorithms:
                a_c += 1
                d_c = 0
                for d in self.data:
                    d_c += 1
                    q_id = "alg" + str(a_c) + "&data" + str(d_c) + "_" + self.qid
                    q = Query(
                        q_id, typ=self.type, algorithms=a, data=d, configs=self.configs
                    )
                    sub_queries.append(q)
        return sub_queries

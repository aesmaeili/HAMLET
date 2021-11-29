"""
    This file contains the definition of the Model Holon calss.
"""

from holon import *
from utilityclasses import *
from helping import *
from spade.message import Message
from spade.template import Template
import asyncio
import collections

from sklearn.model_selection import train_test_split
from sklearn.utils import multiclass
import time


class TrainBehavior(CyclicBehaviour):
    async def run(self):
        received_msg = await self.receive(timeout=10)
        if received_msg:
            content = pickle.loads(bytes(received_msg.body, "latin1"))
            if received_msg.get_metadata("performative") == Performatives.PRF:
                self.agent.add_to_mem(content["qid"], {"output": content["output"]})
                logger.debug(
                    "({}): I got a request to run a training phase for query: {}".format(
                        self.agent.name, content["qid"]
                    )
                )
                logger.debug(
                    "({}): Let's collect the data from ({})".format(
                        self.agent.name, content["co_addr"]
                    )
                )
                req_data_msg = Message(to=content["co_addr"])
                req_data_msg.set_metadata("protocol", Protocols.TRN)
                req_data_msg.set_metadata("performative", Performatives.ACS)
                msg_body = {"qid": content["qid"]}
                req_data_msg.body = pickle.dumps(msg_body, 0).decode()
                await self.send(req_data_msg)
            elif received_msg.get_metadata("performative") == Performatives.CNT:
                if not content["granted"]:
                    logger.debug(
                        "({}): The access is not granted. so let's wait 1 second and try again".format(
                            self.agent.name
                        )
                    )
                    await asyncio.sleep(1)
                    req_data_msg = received_msg.make_reply()
                    req_data_msg.set_metadata("protocol", Protocols.TRN)
                    req_data_msg.set_metadata("performative", Performatives.ACS)
                    msg_body = {"qid": content["qid"]}
                    req_data_msg.body = pickle.dumps(msg_body, 0).decode()
                    await self.send(req_data_msg)
                else:
                    logger.debug(
                        "({}): The access is granted so let's begin training".format(
                            self.agent.name
                        )
                    )

                    self.agent.skills["data"] = {
                        "name": content["name"],
                        "params": content["capabs"],
                    }

                    self.agent.super_holons.add(received_msg.sender)
                    Structure.G.add_edge(
                        self.agent.id,
                        content["data_id"],
                        color=VConfigs.model_edge_color,
                        weight=VConfigs.model_edge_weight,
                        style=VConfigs.model_edge_style,
                    )
                    await self.train(
                        content["data"], content["qid"], content["identifier"]
                    )

    @logger.catch
    async def train(self, data, qid, data_name):
        if self.agent.role == ModelTypes.CLUS:
            metrics_mod = importlib.import_module("sklearn.metrics.cluster")
        else:
            metrics_mod = importlib.import_module("sklearn.metrics")
        results = {}
        
        X_train, y_train = data
        loop = asyncio.get_event_loop()
        mod = importlib.import_module(self.agent.get_KB().to_dict()["module"])
        func = getattr(mod, self.agent.get_KB().to_dict()["function"],)
        args = params_set_to_dict(self.agent.skills["alg"]["params"])
        if "n_clusters" in args.keys():
            if args["n_clusters"] == "auto":
                args["n_clusters"] = len(list(np.unique(y_train)))
        model = func(**args)
        t0 = time.time()
        self.agent.built_model = await loop.run_in_executor(
            None, functools.partial(model.fit, X_train, y_train)
        )
        t1 = time.time()
        self.agent.add_to_mem(qid, {"train_time": t1 - t0})
        for e in self.agent.get_from_mem(qid)["output"]["eval"]:
            if e in self.agent.capabilities:
                metric = getattr(metrics_mod, e)
                additional_args = {}
                if (
                    not multiclass.type_of_target(y_train) == "binary"
                    and not e == "accuracy_score"
                    and self.agent.role == ModelTypes.CLAS
                ):
                    additional_args = {"average": "macro"}
                if self.agent.role == ModelTypes.CLUS:
                    fp = await loop.run_in_executor(
                        None, functools.partial(model.fit_predict, X_train)
                    )
                    met_val = metric(y_train, fp, **additional_args)
                else:
                    met_val = metric(
                        y_train,
                        self.agent.built_model.predict(X_train),
                        **additional_args
                    )
                results[e] = met_val
            else:
                logger.error(
                    "({}): I am asked for an evaluation method that I am not capable of".format(
                        self.agent.name
                    )
                )
                results[e] = None
        results["time"] = t1 - t0
        
        alg_name = None
        for su in self.agent.super_holons:
            if isinstance(su, Agent):
                alg_name = su.id  

        comp_results = {(alg_name, data_name): results}
        await self.send_results(comp_results, qid)

    async def send_results(self, results, qid):
        for su in self.agent.super_holons:
            su_add = str(su.jid) if isinstance(su, Agent) else str(su)
            skills = (
                self.agent.skills["data"]
                if isinstance(su, Agent)
                else self.agent.skills["alg"]
            )
            res_msg = Message(to=su_add)
            res_msg.set_metadata("protocol", Protocols.TRN)
            res_msg.set_metadata("performative", Performatives.RES)
            msg_body = {
                "qid": qid,
                "results": results,
                "skills": skills,
            }
            res_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
            await self.send(res_msg)
            logger.debug(
                "({}): I just sent the results of {} to {}".format(
                    self.agent.name, qid, su_add
                )
            )


class TestBehavior(CyclicBehaviour):
    async def run(self):
        received_msg = await self.receive(timeout=10)
        if received_msg:
            content = pickle.loads(bytes(received_msg.body, "latin1"))
            if received_msg.get_metadata("performative") == Performatives.PRF:
                
                if self.agent.role == content["role"] or content["role"] == "*":
                    self.agent.add_to_mem(
                        content["qid"],
                        {
                            "configs": content["configs"],
                            "data_count": len(content["data"]),
                            
                            "data_providers": {},
                            "test_results": {},
                        },
                    )
                    for dk, dv in content["data"].items():
                        d_name = dv
                        if d_name == self.agent.skills["data"]["name"]:
                            logger.debug(
                                "({}): I got a request to run a testing phase for query: {} because I have {}".format(
                                    self.agent.name, content["qid"], d_name
                                )
                            )
                            logger.debug(
                                "({}): Let's collect the data from ({})".format(
                                    self.agent.name, dk
                                )
                            )

                            req_data_msg = Message(to=dk)
                            req_data_msg.set_metadata("protocol", Protocols.TST)
                            req_data_msg.set_metadata("performative", Performatives.ACS)
                            msg_body = {"qid": content["qid"]}
                            req_data_msg.body = pickle.dumps(msg_body, 0).decode()
                            try:
                                await self.send(req_data_msg)
                            except:  
                                logger.error(
                                    "({}): Fails to access data at {}, probably the address is not available. Proceeding anyway....".format(
                                        self.agent.name, dk
                                    )
                                )
                                self.agent.get_from_mem(content["qid"])[
                                    "data_providers"
                                ].update({dk: None})
                        
                        else:
                            self.agent.get_from_mem(content["qid"])[
                                "data_providers"
                            ].update({dk: None})
                            if (
                                len(
                                    self.agent.get_from_mem(content["qid"])[
                                        "data_providers"
                                    ]
                                )
                                == self.agent.get_from_mem(content["qid"])["data_count"]
                            ):
                                logger.debug(
                                    "({}): expected data count is {} and Data providers are: {}".format(
                                        self.agent.name,
                                        self.agent.get_from_mem(content["qid"])[
                                            "data_count"
                                        ],
                                        self.agent.get_from_mem(content["qid"])[
                                            "data_providers"
                                        ],
                                    )
                                )
                                await self.send_results(None, content["qid"])
                else:
                    await self.send_results(None, content["qid"])
            elif received_msg.get_metadata("performative") == Performatives.CNT:
                if not content["granted"]:
                    logger.debug(
                        "({}): The access is not granted. so let's wait 1 second and try again".format(
                            self.agent.name
                        )
                    )
                    await asyncio.sleep(1)
                    req_data_msg = received_msg.make_reply()
                    req_data_msg.set_metadata("protocol", Protocols.TST)
                    req_data_msg.set_metadata("performative", Performatives.ACS)
                    msg_body = {"qid": content["qid"]}
                    req_data_msg.body = pickle.dumps(msg_body, 0).decode()
                    await self.send(req_data_msg)
                else:
                    logger.debug(
                        "({}): The access is granted so let's begin testing".format(
                            self.agent.name
                        )
                    )
                    self.agent.get_from_mem(content["qid"])["data_providers"].update(
                        {str(received_msg.sender): True}
                    )
                    await self.test(
                        content["data"],
                        content["qid"],
                        self.agent.get_from_mem(content["qid"])["configs"],
                        content["identifier"],
                    )

    @logger.catch
    async def test(self, data, qid, configs, data_name):
        metrics_mod = importlib.import_module("sklearn.metrics")
        results = {}
        d = None
        t = None
        if isinstance(data, tuple):
            d = data[0]
            t = data[1]
        else:
            d = data.data
            t = data.target
        X_test, y_test = d, t

        for e in configs["output"]["eval"]:
            if e in self.agent.capabilities:
                metric = getattr(metrics_mod, e)
                additional_args = {}
                if (
                    not multiclass.type_of_target(y_test) == "binary"
                    and not e == "accuracy_score"
                    and self.agent.role == ModelTypes.CLAS
                ):
                    additional_args = {"average": "macro"}
                if self.agent.role == ModelTypes.CLUS:
                    loop = asyncio.get_event_loop()
                    mod = importlib.import_module(
                        self.agent.get_KB().to_dict()["module"]
                    )
                    func = getattr(mod, self.agent.get_KB().to_dict()["function"],)
                    args = params_set_to_dict(self.agent.skills["alg"]["params"])
                    if "n_clusters" in args.keys():
                        if args["n_clusters"] == "auto":
                            args["n_clusters"] = len(list(np.unique(y_test)))
                    model = func(**args)
                    fp = await loop.run_in_executor(
                        None, functools.partial(model.fit_predict, X_test)
                    )
                    met_val = metric(y_test, fp, **additional_args)
                else:
                    met_val = metric(
                        y_test,
                        self.agent.built_model.predict(X_test),
                        **additional_args
                    )
                results[e] = met_val
        alg_name = None
        for su in self.agent.super_holons:
            if isinstance(su, Agent):
                alg_name = su.id  

        comp_results = {(alg_name, data_name): results}
        self.agent.get_from_mem(qid)["test_results"].update(comp_results)
        if (
            len(self.agent.get_from_mem(qid)["data_providers"])
            == self.agent.get_from_mem(qid)["data_count"]
        ):
            logger.debug(
                "({}): Conducted all tests on provided data. Sending the aggregated list to super_holon".format(
                    self.agent.name
                )
            )
            await self.send_results(self.agent.get_from_mem(qid)["test_results"], qid)

    async def send_results(self, results, qid):

        for su in self.agent.super_holons:
            if isinstance(su, Agent):
                res_msg = Message(to=str(su.jid))
                res_msg.set_metadata("protocol", Protocols.TST)
                res_msg.set_metadata("performative", Performatives.RES)
                msg_body = {
                    "qid": qid,
                    "results": results,
                }
                res_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                await self.send(res_msg)
                logger.debug(
                    "({}): I just sent the results of {} to {}".format(
                        self.agent.name, qid, str(su.jid)
                    )
                )


class ModH(Holon):
    def __init__(
        self,
        holon_jid,
        holon_pass,
        name,
        super_holons=None,
        color=VConfigs.model_node_color,
        id_is_jid=True,
        is_terminal=False,
    ):
        """
        Args:
            holon_jid: The address of the holon on XMPP server
            Holon_pass: The password of the holon on the server
            name: The name of the holon. Not necessarily unique
            super_holons: The list containing super holons' jid in the holarchy
            color: The color in visual representation
        """
        super().__init__(
            holon_jid,
            holon_pass,
            name,
            super_holons,
            color,
            id_is_jid=id_is_jid,
            is_terminal=is_terminal,
        )

        self.built_model = None

    async def setup(self):
        await super().setup()

        train_perf_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.PRF
        )
        train_cnt_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.CNT
        )

        train_template = train_perf_template | train_cnt_template
        self.add_behaviour(TrainBehavior(), train_template)

        test_perf_template = get_template(
            protocol=Protocols.TST, performative=Performatives.PRF
        )
        test_cnt_template = get_template(
            protocol=Protocols.TST, performative=Performatives.CNT
        )

        test_template = test_perf_template | test_cnt_template
        self.add_behaviour(TestBehavior(), test_template)

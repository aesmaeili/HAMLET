"""
    This file contains the definition of the System Holon calss as a
    first level entity in the system.
"""

from holon import *
from visual import *
from utilityclasses import *
from spade.message import Message
from algh import *
from dath import *
from modh import *
import pandas as pd


class GetQueryBehavior(CyclicBehaviour):
    async def run(self):
        query = await self.receive(timeout=10)
        if query:
            q_content = pickle.loads(bytes(query.body, "ascii"))
            logger.debug(
                "({}): I got a query from ({}) with content: {}".format(
                    self.agent.name, extract_name(str(query.sender)), q_content
                )
            )
            qid = q_content["qid"]
            mainQid = qid.split("_")[1]
            if (
                not mainQid in self.agent.collected_results.keys()
                and query.get_metadata("performative") != Performatives.DAD
            ):
                
                self.agent.collected_results[mainQid] = pd.DataFrame()

            if query.get_metadata("performative") == Performatives.TRN:
                
                a = qid.split("_")[0].split("&")[0]
                d = qid.split("_")[0].split("&")[1]
                self.agent.q_map[a] = q_content["alg_name"]
                self.agent.q_map[d] = q_content["data_name"]

                for sub in self.agent.sub_holons:
                    await self.send_for_check(q_content, sub)

                self.agent.add_to_mem(
                    qid,
                    {
                        "status": "checking",
                        "target_model": None,
                        "target_data": None,
                        "results": {},
                        "output": q_content["configs"]["output"],
                    },
                )
                logger.debug(
                    "({}): Initiated check with sub-holons and updated the status in memory for that query".format(
                        self.agent.name
                    )
                )
            elif query.get_metadata("performative") == Performatives.DAD:

                for sub in self.agent.sub_holons:
                    if isinstance(sub, DatH):
                        check_msg = Message(to=str(sub.jid))
                        check_msg.set_metadata("protocol", Protocols.TRN)
                        check_msg.set_metadata("performative", Performatives.CHK)
                        for data_name, params in q_content["data"].items():
                            msg_body = {
                                "qid": q_content["qid"],
                                "name": data_name,
                                "params": params["params"],
                                "KB": params["kb"],
                                "what": "all",
                            }
                        check_msg.body = pickle.dumps(msg_body, 0).decode()
                        await self.send(check_msg)

                self.agent.add_to_mem(
                    qid,
                    {
                        "status": "adding",
                        "target_model": None,
                        "target_data": None,
                        "results": {},
                    },
                )
                logger.debug(
                    "({}): Initiated check with sub-holons and updated the status in memory for that query".format(
                        self.agent.name
                    )
                )

            elif query.get_metadata("performative") == Performatives.TST:
                # Collecting the data info
                from_orig_query = {
                    "name": next(iter(q_content["algorithms"])),
                    "params": q_content["algorithms"][
                        next(iter(q_content["algorithms"]))
                    ]["params"],
                    "configs": q_content["configs"],
                    "role": q_content["algorithms"][
                        next(iter(q_content["algorithms"]))
                    ]["role"]
                    if "role"
                    in q_content["algorithms"][next(iter(q_content["algorithms"]))]
                    else "*",
                }

                for sub in self.agent.sub_holons:
                    if isinstance(sub, DatH):
                        await self.check_test_data(q_content, sub)

                self.agent.add_to_mem(
                    qid,
                    {
                        "status": "waiting for data",
                        "target_model": None,
                        "target_data": None,
                        "results": {},
                        "from_orig_query": from_orig_query,
                    },
                )
                logger.debug(
                    "({}): Initiated get data info with Data subholon and updated the status in memory for that query".format(
                        self.agent.name
                    )
                )
        else:
            logger.debug(
                "({}): Sounds like there is no new query, so let's start the visualization".format(
                    self.agent.name
                )
            )
            if not VConfigs.visualized:
                

                for qk, qv in self.agent.collected_results.items():
                    vis_msg = Message(to=str(self.agent.result_visualizer.jid))
                    vis_msg.set_metadata("protocol", Protocols.VIZ)
                    vis_msg.set_metadata("performative", Performatives.RES)
                    msg_body = {"qid": qk, "results": qv}
                    vis_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                    await self.send(vis_msg)

                print("res sent  ", msg_body)
                str_msg = Message(to=str(self.agent.structure_visualizer.jid))
                str_msg.set_metadata("protocol", Protocols.TRN)
                str_msg.set_metadata("performative", Performatives.STR)
                msg_body = {"hide_color": VConfigs.model_node_color}
                str_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                await self.send(str_msg)
                VConfigs.visualized = True

    async def on_end(self):
        for a in Structure.all_agents:
            for q, v in a.get_entire_memory().items():
                if "ref_to_dest" in v:
                    print(
                        "({}): my ref_to_dest for ({}):{}".format(
                            a.name, q, v["ref_to_dest"]
                        )
                    )
            print("({}): my KB is {}".format(a.name, a.get_KB().to_dict()))

    async def send_for_check(self, q_content, sub_holon):
        check_msg = Message(to=str(sub_holon.jid))
        check_msg.set_metadata("protocol", Protocols.TRN)
        check_msg.set_metadata("performative", Performatives.CHK)
        msg_body = None
        if isinstance(sub_holon, AlgH):
            for alg_name, params in q_content["algorithms"].items():
                msg_body = {
                    "qid": q_content["qid"],
                    "name": alg_name,
                    "params": params["params"],
                    "KB": params["kb"],
                    "what": "all",
                    "configs": q_content["configs"],
                    "role": params["role"] if "role" in params.keys() else None,
                }

        elif isinstance(sub_holon, DatH):
            for data_name, params in q_content["data"].items():
                msg_body = {
                    "qid": q_content["qid"],
                    "name": data_name,
                    "params": params["params"],
                    "KB": params["kb"],
                    "what": "all",
                }
        check_msg.body = pickle.dumps(msg_body, 0).decode()
        await self.send(check_msg)

    async def check_test_data(self, q_content, sub):
        check_msg = Message(to=str(sub.jid))
        check_msg.set_metadata("protocol", Protocols.TST)
        check_msg.set_metadata("performative", Performatives.CHK)
        msg_body = None
        for data_name, params in q_content["data"].items():
            msg_body = {
                "qid": q_content["qid"],
                "name": data_name,
                "params": params["params"],
                "KB": params["kb"],
            }
            check_msg.body = pickle.dumps(msg_body, 0).decode()
            await self.send(check_msg)

    async def extract_parts(self, Q_id):
        main_split = Q_id.split("_")
        part_split = main_split[0].split("&")
        return {"Q": main_split[1], "Algorithm": part_split[0], "Data": part_split[1]}


class PerformTrainingBehavior(CyclicBehaviour):
    async def run(self):
        checked_result = await self.receive(timeout=10)
        if checked_result:
            q_content = pickle.loads(bytes(checked_result.body, "ascii"))
            logger.debug(
                "({}): I got a checked_result from ({}) with content: {}".format(
                    self.agent.name, extract_name(str(checked_result.sender)), q_content
                )
            )
            if self.agent.get_from_mem(q_content["qid"])["status"] != "adding":
                target = "target_" + q_content["type"]
                self.agent.add_to_mem(q_content["qid"], {target: q_content["dest"]})

                if (
                    not self.agent.get_from_mem(q_content["qid"])["target_model"]
                    is None
                    and not self.agent.get_from_mem(q_content["qid"])["target_data"]
                    is None
                ):
                    await self.send_train_command(q_content)

    async def send_train_command(self, content):
        for sub in self.agent.sub_holons:
            perf_msg = Message()
            perf_msg.set_metadata("protocol", Protocols.TRN)
            perf_msg.set_metadata("performative", Performatives.PRF)
            target_data = self.agent.get_from_mem(content["qid"])["target_data"]
            target_model = self.agent.get_from_mem(content["qid"])["target_model"]
            logger.debug(
                "({}): target_data is {}, target_model is {}".format(
                    self.agent.name, target_data, target_model
                )
            )
            perf_msg.to = str(sub.jid)
            if isinstance(sub, AlgH):
                msg_body = {
                    "qid": content["qid"],
                    "co_addr": target_data,
                    "output": self.agent.get_from_mem(content["qid"])["output"],
                }
                logger.debug(
                    "(send_train_command) msg_body to be sent to ({}) is: {}".format(
                        sub.name, msg_body
                    )
                )
                perf_msg.body = pickle.dumps(msg_body, 0).decode()
                await self.send(perf_msg)
            elif isinstance(sub, DatH):
                msg_body = {
                    "qid": content["qid"],
                    "co_addr": target_model,
                }
                logger.debug(
                    "(send_train_command) msg_body to be sent to ({}) is: {}".format(
                        sub.name, msg_body
                    )
                )
                perf_msg.body = pickle.dumps(msg_body, 0).decode()
                await self.send(perf_msg)


class PerformTestingBehavior(CyclicBehaviour):
    async def run(self):
        checked_result = await self.receive(timeout=10)
        if checked_result:
            q_content = pickle.loads(bytes(checked_result.body, "ascii"))
            logger.debug(
                "({}): I got a checked_result from ({}) with content: {}".format(
                    self.agent.name, extract_name(str(checked_result.sender)), q_content
                )
            )
            if len(q_content["data"]) > 0:  
                orig_test_query = self.agent.get_from_mem(q_content["qid"])[
                    "from_orig_query"
                ]
                test_content = {"qid": q_content["qid"], "data": q_content["data"]}
                test_content.update(orig_test_query)
                for sub in self.agent.sub_holons:
                    if isinstance(sub, AlgH):
                        await self.send_test_command(test_content, sub)

    async def send_test_command(self, q_content, sub):
        test_msg = Message(to=str(sub.jid))
        test_msg.set_metadata("protocol", Protocols.TST)
        test_msg.set_metadata("performative", Performatives.PRF)
        test_msg.body = pickle.dumps(q_content, 0).decode("latin1")
        await self.send(test_msg)


class GetResultsBehavior(CyclicBehaviour):
    async def run(self):
        received_result = await self.receive(timeout=10)
        if received_result:
            res_content = pickle.loads(bytes(received_result.body, "latin1"))
            if received_result.get_metadata("protocol") == Protocols.TRN:
                logger.debug(
                    "({}): I got a train result from ({}) with content: {}".format(
                        self.agent.name,
                        extract_name(str(received_result.sender)),
                        res_content,
                    )
                )
                self.agent.get_from_mem(res_content["qid"])["results"].update(
                    {res_content["qid"]: res_content["results"]}
                )
                logger.debug(
                    "({}): my memory result content for query ({}) is:{}".format(
                        self.agent.name,
                        res_content["qid"],
                        self.agent.get_from_mem(res_content["qid"])["results"],
                    )
                )
                q = res_content["qid"].split("_")[1]
                
                for rk, rv in res_content["results"].items():
                    
                    a = rk[0]
                    d = rk[1]
                    
                    self.agent.collected_results[q].at[d, a] = [rv]
                    

            elif received_result.get_metadata("protocol") == Protocols.TST:
                logger.debug(
                    "({}): I got a test result from ({}) with content: {}".format(
                        self.agent.name,
                        extract_name(str(received_result.sender)),
                        res_content,
                    )
                )
                self.agent.get_from_mem(res_content["qid"])["results"].update(
                    {res_content["qid"]: res_content["results"]}
                )

                q = res_content["qid"].split("_")[1]
                if not res_content["results"] is None:
                    for rk, rv in res_content["results"].items():
                        
                        self.agent.collected_results[q].at[rk[1], rk[0]] = [rv]
                    
                        


class SysH(Holon):
    def __init__(
        self,
        holon_jid,
        holon_pass,
        name="SYS",
        super_holons=None,
        color=VConfigs.system_node_color,
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
            holon_jid, holon_pass, name, super_holons, color, id_is_jid=False
        )
        self.collected_results = {}
        self.q_map = {}
        self.result_visualizer = VisAgent(
            "resvisualizer@localhost", "viz", typ="results"
        )
        self.structure_visualizer = VisAgent(
            "strvisualizer@localhost", "vis", "vis", typ="structure"
        )
        self.result_visualizer.start().result()
        self.structure_visualizer.start().result()

    async def setup(self):
        await super().setup()
        DF.sys_jid = self.jid

        train_query_template = get_template(
            protocol=Protocols.QRY, performative=Performatives.TRN
        )
        add_query_template = get_template(
            protocol=Protocols.QRY, performative=Performatives.DAD
        )
        test_query_template = get_template(
            protocol=Protocols.QRY, performative=Performatives.TST
        )
        self.add_behaviour(
            GetQueryBehavior(),
            train_query_template | add_query_template | test_query_template,
        )

        train_check_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.ADD
        )
        self.add_behaviour(PerformTrainingBehavior(), train_check_template)

        train_res_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.RES
        )
        test_res_template = get_template(
            protocol=Protocols.TST, performative=Performatives.RES
        )
        self.add_behaviour(GetResultsBehavior(), train_res_template | test_res_template)

        test_check_template = get_template(
            protocol=Protocols.TST, performative=Performatives.RSP
        )
        self.add_behaviour(PerformTestingBehavior(), test_check_template)

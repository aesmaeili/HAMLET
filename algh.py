"""
    This file contains the definition of the Algorithm Holon calss.
"""

from holon import *
from utilityclasses import *
from helping import *
from spade.message import Message
from spade.template import Template
import asyncio
from modh import *


class TrainQueryBehavior(CyclicBehaviour):
    async def run(self):
        train_query = await self.receive(timeout=10)
        if train_query:
            q_content = pickle.loads(
                bytes(train_query.body, "ascii")
            )  
            logger.debug(
                "({}): I got a {} query from ({}) with content: {}".format(
                    self.agent.name,
                    train_query.get_metadata("performative"),
                    extract_name(str(train_query.sender)),
                    q_content,
                )
            )

            if (
                train_query.get_metadata("performative") == Performatives.CHK
            ):  
                self.agent.add_to_mem(
                    q_content["qid"],
                    {
                        "check_count": len(self.agent.sub_holons)
                        + 1,  
                        "check_responders": {
                            str(self.agent.jid): -1
                        },  
                        "check_winner": None,  
                        "ref_to_dest": None,  
                        "status": "checking",
                    },
                )
                if q_content["what"] == "all":  
                    logger.debug(
                        "({}): the message is from SYS".format(self.agent.name)
                    )
                    if not self.agent.is_atomic():
                        logger.debug(
                            "({}): I am not atomic so let's issue CFP to subs".format(
                                self.agent.name
                            )
                        )
                        for sub in self.agent.sub_holons:
                            await self.send_CFP(q_content, sub.jid, what="name")
                            logger.debug(
                                "({}): sent CFP to sub {}".format(
                                    self.agent.name, sub.name
                                )
                            )
                    else:
                        logger.debug(
                            "({}): I am atomic and the winner so let's create a sub and spawn a model".format(
                                self.agent.name
                            )
                        )
                        self.agent.add_to_mem(
                            q_content["qid"],
                            {
                                "check_winner": str(self.agent.jid),
                                
                            },
                        )
                        await self.create_and_spawn_model(q_content)

                else:  
                    logger.debug(
                        "({}): I am not ALG, so sounds like I have won in previous CFP".format(
                            self.agent.name
                        )
                    )
                    my_sim_ratio = param_sim_ratio(
                        self.agent.capabilities, q_content[q_content["what"]]
                    )

                    self.agent.get_from_mem(q_content["qid"])[
                        "check_responders"
                    ].update({str(self.agent.jid): my_sim_ratio})

                    logger.debug(
                        "({}): the content of my memory after updating it with similarity ratio: {}".format(
                            self.agent.name, self.agent.get_from_mem(q_content["qid"])
                        )
                    )

                    if not self.agent.is_atomic():
                        logger.debug(
                            "({}): I am not atomic so let's issue CFP to the subs".format(
                                self.agent.name
                            )
                        )
                        for sub in self.agent.sub_holons:
                            await self.send_CFP(
                                q_content, sub.jid, what=q_content["what"]
                            )  
                            logger.debug(
                                "({}): sent CFP to sub {}".format(
                                    self.agent.name, sub.name
                                )
                            )

                    else:
                        logger.debug("({}): I am atomic...".format(self.agent.name))
                        self.agent.add_to_mem(
                            q_content["qid"], {"check_winner": str(self.agent.jid)}
                        )
                        if (
                            my_sim_ratio == 1
                        ):  
                            logger.debug(
                                "({}): I already exist, so let's just spawn a model".format(
                                    self.agent.name
                                )
                            )
                            await self.spawn_model(q_content, self.agent)
                        else:
                            logger.debug(
                                "({}): no holon for the questioned params, so let's create new branch".format(
                                    self.agent.name
                                )
                            )
                            self.agent.add_to_mem(
                                q_content["qid"],
                                {
                                    "check_winner": str(self.agent.jid),
                                    
                                },
                            )
                            await self.create_and_spawn_model(q_content)

            elif (
                train_query.get_metadata("performative") == Performatives.PPZ
            ):  
                self.agent.get_from_mem(q_content["qid"])["check_responders"].update(
                    {str(train_query.sender): q_content["proposal"]}
                )
                if (
                    q_content["what"] == "name"
                ):  
                    logger.debug(
                        "({}): I am ALG, and I got a proposal for 'name'".format(
                            self.agent.name
                        )
                    )
                    if (
                        self.agent.get_from_mem(q_content["qid"])["check_winner"]
                        is not None
                    ):  
                        logger.debug(
                            "({}): ignoring the message because a winner has already been chosen".format(
                                self.agent.name
                            )
                        )
                        pass
                    elif q_content["proposal"] != 1 and (
                        self.agent.get_from_mem(q_content["qid"])["check_count"]
                        == len(
                            self.agent.get_from_mem(q_content["qid"])[
                                "check_responders"
                            ]
                        )
                    ):  
                        logger.debug(
                            "({}): the final proposal did not match so I should create every thing".format(
                                self.agent.name
                            )
                        )
                        self.agent.add_to_mem(
                            q_content["qid"], {"check_winner": str(self.agent.jid),},
                        )
                        self.agent.add_to_mem(
                            q_content["qid"],
                            {
                                "check_winner": str(self.agent.jid),
                                
                            },
                        )
                        await self.create_and_spawn_model(q_content)
                    elif q_content["proposal"] == 1:  
                        logger.debug(
                            "({}): I got the perfect match for name so lets send it a check".format(
                                self.agent.name
                            )
                        )
                        self.agent.add_to_mem(
                            q_content["qid"], {"check_winner": train_query.sender,},
                        )
                        
                        await self.send_for_check(
                            q_content, train_query.sender, "params"
                        )
                else:  
                    logger.debug(
                        "({}): I am not ALG and I am receiving a proposal. I am definetely a composite, aren't I?".format(
                            self.agent.name
                        )
                    )
                    if (
                        self.agent.get_from_mem(q_content["qid"])["check_winner"]
                        is not None# The winner has already been chosen, so let's ignore the message
                        logger.debug(
                            "({}): the winner has already been chosen, so let's ignore the message. If you see this message, it means something is wrong!!".format(
                                self.agent.name
                            )
                        )
                        pass
                    elif self.agent.get_from_mem(q_content["qid"])[
                        "check_count"
                    ] == len(
                        self.agent.get_from_mem(q_content["qid"])["check_responders"]
                    ):  
                        logger.debug(
                            "({}): I got the final proposal, and now I am trying to choose the winner.".format(
                                self.agent.name
                            )
                        )
                        winner = argmax(
                            self.agent.get_from_mem(q_content["qid"])[
                                "check_responders"
                            ]
                        )
                        logger.debug(
                            "({}): and the Oscar goes to ({})".format(
                                self.agent.name, winner
                            )
                        )
                        self.agent.add_to_mem(
                            q_content["qid"], {"check_winner": winner,},
                        )
                        if winner == str(self.agent.jid):  # I am the winner
                            logger.debug(
                                "({}): hehe, I won it! can't believe...".format(
                                    self.agent.name
                                )
                            )
                            self.agent.add_to_mem(
                                q_content["qid"],
                                {
                                    "check_winner": str(self.agent.jid),
                                    
                                },
                            )
                            await self.create_and_spawn_model(q_content)
                        else:
                            logger.debug(
                                "({}): asking the winner to handle the check".format(
                                    self.agent.name
                                )
                            )
                            await self.send_for_check(q_content, winner, "params")

            elif (
                train_query.get_metadata("performative") == Performatives.CFP
            ):  
                logger.debug("(from CFP): q_content = {}".format(q_content))
                w = q_content["what"]
                my_what = (
                    (w, self.agent._label) if w == "name" else self.agent.capabilities
                )
                logger.debug("({}): my_what: {}".format(self.agent.name, my_what))
                with_what = (w, q_content[w]) if w == "name" else q_content[w]
                my_sim_ratio = param_sim_ratio(my_what, with_what)

                logger.debug(
                    "({}): my_sim_ratio: {}".format(self.agent.name, my_sim_ratio)
                )

                cfp_msg = Message(to=str(train_query.sender))
                cfp_msg.set_metadata("protocol", Protocols.TRN)
                cfp_msg.set_metadata("performative", Performatives.PPZ)
                msg_body = q_content
                msg_body.update(
                    {w: q_content[w], "proposal": my_sim_ratio,}
                )
                logger.debug("({}): msg_body: {}".format(self.agent.name, msg_body))
                cfp_msg.body = pickle.dumps(msg_body, 0).decode()
                await self.send(cfp_msg)
                logger.debug(
                    "({}): my proposal message is as follows: {} shhhh".format(
                        self.agent.name, msg_body
                    )
                )

            

            elif (
                train_query.get_metadata("performative") == Performatives.PRF
            ):  

                pass

            

    async def send_for_check(self, msg_cnt, sub_holon_jid, what):
        check_msg = Message(to=str(sub_holon_jid))
        check_msg.set_metadata("protocol", Protocols.TRN)
        check_msg.set_metadata("performative", Performatives.CHK)
        msg_body = msg_cnt
        msg_body.update({"what": what})
        check_msg.body = pickle.dumps(msg_body, 0).decode()
        await self.send(check_msg)

    async def spawn_model(self, q_content, owner, with_sibling=False):
        new_model = ModH(
            ID.modID() + "@localhost", "model", name=q_content["name"], is_terminal=True
        )
        new_model.add_super_holon(owner, is_model=True)
        await new_model.start()
        new_model.set_KB(
            module=owner.get_KB().to_dict()["module"],
            func=owner.get_KB().to_dict()["function"],
        )
        new_model.skills = {
            "alg": {"name": q_content["name"], "params": owner.capabilities}
        }
        new_model.capabilities = q_content["configs"]["evals"]
        new_model.role = q_content["role"]
        logger.debug("A new model holon is created for qid {}".format(q_content["qid"]))
        for u in self.agent.super_holons:
            if not u.name == "alg" and not self.agent.name == "alg":  # so naive
                value_upd_msg = Message(to=str(u.jid))
                value_upd_msg.set_metadata("protocol", Protocols.REQ)
                value_upd_msg.set_metadata("performative", Performatives.UPV)
                update_body = {
                    "what": "capabilities",
                    "add_or_replace": "add",
                    "new_value": q_content["params"],
                }
                value_upd_msg.body = pickle.dumps(update_body, 0).decode()
                await self.send(value_upd_msg)
            owner.add_to_mem(q_content["qid"], {"ref_to_dest": str(new_model.jid)})
            logger.debug(
                "({}): my ref_to_dest is now: {} and for owner ({}) is : {}".format(
                    self.agent.name,
                    self.agent.get_from_mem(q_content["qid"])["ref_to_dest"],
                    owner.name,
                    owner.get_from_mem(q_content["qid"])["ref_to_dest"],
                )
            )

            if self.agent.id != owner.id:
                self.agent.get_from_mem(q_content["qid"]).update(
                    {"ref_to_dest": str(owner.jid)}
                )

            model_add_msg = Message(to=str(u.jid))
            model_add_msg.set_metadata("protocol", Protocols.TRN)
            model_add_msg.set_metadata("performative", Performatives.ADD)
            
            ref = str(self.agent.jid)
            if with_sibling:
                ref = str(owner.jid)
            msg_body = {
                "qid": q_content["qid"],
                "type": "model",
                
                "ref": ref,
                "dest": str(new_model.jid),
            }

            model_add_msg.body = pickle.dumps(msg_body, 0).decode()

            await (self.send(model_add_msg))
            logger.debug(
                "({}):The address of the newly created model holon was just sent to {}".format(
                    self.agent.name, str(u.jid)
                )
            )
       

    async def create_and_spawn_model(self, q_content):
        logger.debug("(Create&Spawn): q_content: {}".format(q_content))
        if not self.agent.is_atomic() or self.agent.name == "alg":  
            new_sub = AlgH(
                ID.atmAlgID() + "@localhost",
                "alg",
                q_content["name"],
                super_holons={self.agent},
                is_terminal=True,
            )
            await new_sub.start()
            
            logger.debug("({}):A new sub-holon is created".format(str(self.agent.name)))
            new_sub.capabilities = q_content["params"]
            new_sub.set_KB(module=q_content["KB"], func=q_content["name"])
            new_sub.role = q_content["role"]
            await self.spawn_model(q_content, new_sub)
        else:
            new_sup = AlgH(
                ID.algID() + "@localhost",
                "alg",
                q_content["name"],
                super_holons={
                    next(iter(self.agent.super_holons))
                },  
            )
            await new_sup.start()
            new_sup.role = q_content["role"]
            new_sup.capabilities = self.agent.capabilities
            for u in self.agent.super_holons:
                for q, v in u.get_entire_memory().items():
                    if v["ref_to_dest"] == str(self.agent.jid):
                        v.update({"ref_to_dest": str(new_sup.jid)})
                        new_sup.add_to_mem(q, {"ref_to_dest": str(self.agent.jid)})

            self.agent.change_super(
                next(iter(self.agent.super_holons)), new_sup
            )  
            new_sub = AlgH(
                ID.atmAlgID() + "@localhost",
                "alg",
                q_content["name"],
                super_holons={new_sup},
                is_terminal=True,
            )
            await new_sub.start()
            new_sub.capabilities = q_content["params"]
            new_sub.set_KB(module=q_content["KB"], func=q_content["name"])
            new_sub.role = q_content["role"]
            await self.spawn_model(# await asyncio.sleep(1)

    async def send_CFP(self, msg_cnt, sub_holon_jid, what):
        cfp_msg = Message(to=str(sub_holon_jid))
        cfp_msg.set_metadata("protocol", Protocols.TRN)
        cfp_msg.set_metadata("performative", Performatives.CFP)
        msg_body = msg_cnt
        msg_body.update({"what": what})
        cfp_msg.body = pickle.dumps(msg_body, 0).decode()
        await self.send(cfp_msg)


class UpdateValueBehavior(
    CyclicBehaviour
):  
    async def run(self):
        update_msg = await self.receive(timeout=10)
        
        if update_msg:
            up_content = pickle.loads(bytes(update_msg.body, "ascii"))
            logger.debug(
                "({}): I got the request to update my {} with {}".format(
                    self.agent.name, up_content["what"], up_content["new_value"]
                )
            )
            if not self.agent.name == "alg":  
                logger.debug(
                    "({}): my {} before {} is {}".format(
                        self.agent.name,
                        up_content["what"],
                        up_content["add_or_replace"],
                        self.agent.__dict__[up_content["what"]],
                    )
                )
                if up_content["add_or_replace"] == "add":
                    self.agent.__dict__[up_content["what"]] = param_sum(
                        self.agent.__dict__[up_content["what"]], up_content["new_value"]
                    )
                elif up_content["add_or_replace"] == "replace":
                    self.agent.__dict__[up_content["what"]] = up_content["new_value"]
                logger.debug(
                    "({}): my {} after {} is {}".format(
                        self.agent.name,
                        up_content["what"],
                        up_content["add_or_replace"],
                        self.agent.__dict__[up_content["what"]],
                    )
                )
                for u in self.agent.super_holons:
                    new_msg = update_msg.make_reply()
                    new_msg.to = str(u.jid)
                    await self.send(new_msg)
                    logger.debug(
                        "({}): asked the superholon ({}) to update {}".format(
                            self.agent.name, u.name, up_content["what"]
                        )
                    )





class SendBehavior(
    CyclicBehaviour
): 
    async def run(self):
        received_msg = await self.receive(timeout=10)
        if received_msg:
            content = pickle.loads(bytes(received_msg.body, "latin1"))
            if received_msg.get_metadata("performative") == Performatives.ADD:
                logger.debug(
                    "({}): I got the request to send a holon/model address to superholon".format(
                        self.agent.name
                    )
                )
                for u in self.agent.super_holons:
                    new_msg = received_msg.make_reply()
                    new_msg.to = str(u.jid)
                    self.agent.add_to_mem(
                        content["qid"], {"ref_to_dest": content["ref"]}
                    )  
                    content.update({"ref": str(self.agent.jid)})
                    new_msg.body = pickle.dumps(content, 0).decode()
                    await self.send(new_msg)
                    logger.debug(
                        "({}): I just sent the reference {} to superholon {}".format(
                            self.agent.name, content["ref"], str(u.jid)
                        )
                    )
            elif received_msg.get_metadata("performative") == Performatives.PRF:
                
                logger.debug(
                    "({}): I need to process a train perform command received with content: {}".format(
                        self.agent.name, content
                    )
                )
                perf_msg = received_msg.make_reply()
                perf_msg.to = self.agent.get_from_mem(content["qid"])["ref_to_dest"]
                await self.send(perf_msg)
                logger.debug(
                    "({}): Just forwarded the perform message to ({})".format(
                        self.agent.name, perf_msg.to
                    )
                )
            elif received_msg.get_metadata("performative") == Performatives.RES:
                logger.debug(
                    "({}): My skills are : {}".format(
                        self.agent.name, self.agent.skills
                    )
                )
                logger.debug(
                    "({}): I need to update my skills and pass the results to super holons".format(
                        self.agent.name
                    )
                )
                for u in self.agent.super_holons:
                    new_msg = received_msg.make_reply()
                    new_msg.to = str(u.jid)
                    new_set = content["skills"]
                    if (
                        not new_set in self.agent.skills
                        and not self.agent.name == "alg"
                    ):
                        self.agent.skills.append(new_set)
                    logger.debug(
                        "({}): My skills after update are : {}".format(
                            self.agent.name, self.agent.skills
                        )
                    )
                    new_msg.body = pickle.dumps(content, 0).decode("latin1")
                    await self.send(new_msg)
                    logger.debug(
                        "({}): I just sent the skills {} to superholon {}".format(
                            self.agent.name, content["skills"], str(u.jid)
                        )
                    )


class TestQueryBehavior(CyclicBehaviour):
    async def run(self):
        test_query = await self.receive(timeout=10)
        if test_query:
            q_content = pickle.loads(bytes(test_query.body, "latin1"))
            logger.debug(
                "({}): Just received {} with content: {}".format(
                    self.agent.name, test_query.get_metadata("performative"), q_content
                )
            )
            if test_query.get_metadata("performative") == Performatives.PRF:
                self.agent.add_to_mem(
                    q_content["qid"],
                    {
                        "test_count": len(self.agent.sub_holons)
                        if not self.agent.is_atomic()
                        else len(self.agent.model_holons),
                        "test_responders": {},  
                        "status": "performing_test",
                    },
                )
                if str(test_query.sender) == str(
                    DF.sys_jid
                ):  
                    logger.debug(
                        "({}): the message is from SYS".format(self.agent.name)
                    )
                    if not self.agent.is_atomic():
                        logger.debug(
                            "({}): I am not atomic so let's issue perform command to subs. The contents will be: {}".format(
                                self.agent.name, q_content
                            )
                        )
                        for sub in self.agent.sub_holons:
                            await self.send_test_command(q_content, sub)
                            logger.debug(
                                "({}): sent test command to sub {}".format(
                                    self.agent.name, sub.name
                                )
                            )
                    else:
                        logger.error(
                            "({}): I must not be atomic during test phase. The system should have at least a trained algorithm".format(
                                self.agent.name
                            )
                        )
                else:  # I am not ALG
                    logger.debug(
                        "({}): my name is {} and the name asked in query is {}".format(
                            self.agent.name, self.agent._label, q_content["name"]
                        )
                    )
                    common_data = {}
                    matched = param_lt(
                        ("name", self.agent._label), ("name", q_content["name"])
                    )
                    if matched:
                        logger.debug(
                            "({}): my capabilities are {} and the params asked in query are {}".format(
                                self.agent.name,
                                self.agent.capabilities,
                                q_content["params"],
                            )
                        )
                        matched = param_lt(
                            q_content["params"], self.agent.capabilities,
                        )
                        logger.debug(
                            "({}): matched = {}".format(self.agent.name, matched)
                        )
                    if matched:
                        
                        my_skill_names = set()
                        for s in self.agent.skills:
                            my_skill_names.add(s[next(iter(s))])

                        required_skill_names = set(q_content["data"].values())
                        common_skills = my_skill_names & required_skill_names
                        logger.debug(
                            "({}): my skill names are {} and the required skill names are {}. as the result, the commons are {}".format(
                                self.agent.name,
                                my_skill_names,
                                required_skill_names,
                                common_skills,
                            )
                        )
                        matched = len(common_skills) > 0
                        if matched:
                            for dk, dv in q_content["data"].items():
                                if dv in my_skill_names:
                                    common_data.update({dk: dv})

                    if matched:
                        logger.debug(
                            "({}): my name and capabilities match the query's".format(
                                self.agent.name
                            )
                        )
                        if not self.agent.is_atomic():
                            logger.debug(
                                "({}): I am not atomic so let's issue test perform to subs".format(
                                    self.agent.name
                                )
                            )
                            for sub in self.agent.sub_holons:
                                subq_content = {}
                                subq_content.update(q_content)
                                subq_content["data"] = common_data
                                await self.send_test_command(subq_content, sub)
                                logger.debug(
                                    "({}): sent test data check to sub {}".format(
                                        self.agent.name, sub.name
                                    )
                                )
                        else:
                            logger.debug(
                                "({}): I am atomic during test phase, let's ask the models to see if they can run the tests".format(
                                    self.agent.name
                                )
                            )
                            if len(self.agent.model_holons) > 0:
                                subq_content = {}
                                subq_content.update(q_content)
                                subq_content["data"] = common_data
                                for mod in self.agent.model_holons:
                                    await self.send_test_command(subq_content, mod)
                                    logger.debug(
                                        "({}): sent test command to model {}".format(
                                            self.agent.name, mod.name
                                        )
                                    )
                            else:  
                                pass

                    else:  
                        res_msg = test_query.make_reply()
                        res_msg.set_metadata("performative", Performatives.RES)
                        msg_body = {
                            "qid": q_content["qid"],
                            "results": None,
                        }
                        res_msg.body = pickle.dumps(msg_body, 0).decode()
                        await self.send(res_msg)
                        logger.debug(
                            "({}): just sent result {} to superholon ({})".format(
                                self.agent.name, msg_body, res_msg.to
                            )
                        )
            elif test_query.get_metadata("performative") == Performatives.RES:
                
                logger.debug(
                    "({}): I got the result: {}".format(
                        self.agent.name, q_content["results"]
                    )
                )
                self.agent.get_from_mem(q_content["qid"])["test_responders"].update(
                    {str(test_query.sender): q_content["results"]}
                )
                
                if self.agent.get_from_mem(q_content["qid"])["test_count"] == len(
                    self.agent.get_from_mem(q_content["qid"])["test_responders"].keys()
                ):
                    logger.debug(
                        "({}): collected all test results. Let's aggregate them all and send them to the super-holon".format(
                            self.agent.name
                        )
                    )
                    available_results = {}
                    for resv in self.agent.get_from_mem(q_content["qid"])[
                        "test_responders"
                    ].values():
                        if not resv is None:
                            available_results.update(resv)

                    for sup in self.agent.super_holons:
                        res_msg = test_query.make_reply()
                        res_msg.to = str(sup.jid)
                        msg_body = {
                            "qid": q_content["qid"],
                            "results": available_results,
                        }
                        res_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                        await self.send(res_msg)
                        logger.debug(
                            "({}): just sent results {} to superholon ({})".format(
                                self.agent.name, msg_body, str(sup.jid)
                            )
                        )

    async def send_test_command(self, q_content, holon):
        test_msg = Message(to=str(holon.jid))
        test_msg.set_metadata("protocol", Protocols.TST)
        test_msg.set_metadata("performative", Performatives.PRF)
        test_msg.body = pickle.dumps(q_content, 0).decode()
        await self.send(test_msg)


class AlgH(Holon):
    def __init__(
        self,
        holon_jid,
        holon_pass,
        name,
        super_holons=None,
        color=VConfigs.algorithm_node_color,
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
        self.model_holons = set()

    async def setup(self):
        await super().setup()

        train_check_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.CHK
        )
        train_proposal_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.PPZ
        )
        train_cfp_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.CFP
        )
        train_address_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.ADD
        )
        train_templates = (
            train_check_template
            | train_proposal_template
            | train_cfp_template
            | train_address_template
        )
        update_value_template = get_template(
            protocol=Protocols.REQ, performative=Performatives.UPV
        )

        send_address_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.ADD
        )
        send_perfrom_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.PRF
        )
        train_res_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.RES
        )

        send_template = (
            send_address_template | send_perfrom_template | train_res_template
        )

        self.add_behaviour(UpdateValueBehavior(), update_value_template)

        self.add_behaviour(TrainQueryBehavior(), train_templates)
        self.add_behaviour(SendBehavior(), send_template)

        test_perfrom_template = get_template(
            protocol=Protocols.TST, performative=Performatives.PRF
        )
        test_res_template = get_template(
            protocol=Protocols.TST, performative=Performatives.RES
        )

        self.add_behaviour(
            TestQueryBehavior(), test_perfrom_template | test_res_template
        )

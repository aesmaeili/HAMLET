"""
    This file contains the definition of the Data Holon calss.
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
                            "({}): I am atomic and the winner so let's create a sub".format(
                                self.agent.name
                            )
                        )
                        self.agent.add_to_mem(
                            q_content["qid"],
                            {
                                "check_winner": str(self.agent.jid),
                                
                            },
                        )
                        await self.extend(q_content)

                else:  
                    logger.debug(
                        "({}): I am not DATA, so sounds like I have won in previous CFP".format(
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
                                "({}): I already exist, so let's just send my address up".format(
                                    self.agent.name
                                )
                            )
                            await self.send_address_up(q_content, None)
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
                            await self.extend(q_content)

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
                        "({}): I am DATA, and I got a proposal for 'name'".format(
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
                        await self.extend(q_content)
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
                        "({}): I am not DATA and I am receiving a proposal. I am definetely a composite, aren't I?".format(
                            self.agent.name
                        )
                    )
                    if (
                        self.agent.get_from_mem(q_content["qid"])["check_winner"]
                        is not None
                    ):  
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
                        if winner == str(self.agent.jid):  
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
                            await self.extend(q_content)
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

    

    async def extend(self, q_content):
        logger.debug("(extend): q_content: {}".format(q_content))
        new_sub = None
        got_sibling = False
        if not self.agent.is_atomic() or self.agent.name == "data":  
            new_sub = DatH(
                ID.datID() + "@localhost",
                "data",
                q_content["name"],
                super_holons={self.agent},
                is_terminal=True,
            )
            await new_sub.start()
            
            logger.debug("({}):A new sub-holon is created".format(str(self.agent.name)))
            new_sub.capabilities = q_content["params"]
            new_sub.set_KB(module=q_content["KB"], func=q_content["name"])
        else:
            new_sup = DatH(
                ID.datID() + "@localhost",
                "data",
                q_content["name"],
                super_holons={
                    next(iter(self.agent.super_holons))
                },  
            await new_sup.start()
            new_sup.capabilities = self.agent.capabilities
            for u in self.agent.super_holons:
                for q, v in u.get_entire_memory().items():
                    if v["ref_to_dest"] == str(self.agent.jid):
                        v.update({"ref_to_dest": str(new_sup.jid)})
                        new_sup.add_to_mem(q, {"ref_to_dest": str(self.agent.jid)})
            self.agent.change_super(
                next(iter(self.agent.super_holons)), new_sup
            )  
            new_sub = DatH(
                ID.datID() + "@localhost",
                "data",
                q_content["name"],
                super_holons={new_sup},
                is_terminal=True,
            )
            got_sibling = True
            await new_sub.start()
            new_sub.capabilities = q_content["params"]
            new_sub.set_KB(module=q_content["KB"], func=q_content["name"])

        new_sub.add_to_mem(q_content["qid"], {"ref_to_dest": None})

        for u in self.agent.super_holons:
            if not u.name == "data" and not self.agent.name == "data":  
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
        await self.send_address_up(q_content, new_sub, with_sibling=got_sibling)

    async def send_CFP(self, msg_cnt, sub_holon_jid, what):
        cfp_msg = Message(to=str(sub_holon_jid))
        cfp_msg.set_metadata("protocol", Protocols.TRN)
        cfp_msg.set_metadata("performative", Performatives.CFP)
        msg_body = msg_cnt
        msg_body.update({"what": what})
        cfp_msg.body = pickle.dumps(msg_body, 0).decode()
        await self.send(cfp_msg)

    async def send_address_up(self, q_content, owner, with_sibling=False):
        logger.debug(
            "({}): passed arguments to send_address_up: {}".format(
                self.agent.name, (q_content, owner, with_sibling)
            )
        )
        for u in self.agent.super_holons:
            add_msg = Message(to=str(u.jid))
            add_msg.set_metadata("protocol", Protocols.TRN)
            add_msg.set_metadata("performative", Performatives.ADD)
            
            ref = None
            dest = str(self.agent.jid)
                self.agent.add_to_mem(q_content["qid"], {"ref_to_dest": None})
                self.agent.add_to_mem(q_content["qid"], {"name": q_content["name"]})
                logger.debug(
                    "({}): the mem content of me for qid {} is {}".format(
                        self.agent.name,
                        q_content["qid"],
                        self.agent.get_from_mem(q_content["qid"]),
                    )
                )
                ref = str(self.agent.jid)
            else:
                ref = str(self.agent.jid)
                dest = str(owner.jid)
                if with_sibling:
                    ref = str(owner.jid)
                    
                self.agent.add_to_mem(q_content["qid"], {"ref_to_dest": str(owner.jid)})
                owner.add_to_mem(q_content["qid"], {"name": q_content["name"]})
                logger.debug(
                    "({}): the mem content of agent {} for qid {} is {}".format(
                        self.agent.name,
                        owner.name,
                        q_content["qid"],
                        owner.get_from_mem(q_content["qid"]),
                    )
                )
            logger.debug(
                "({}): my ref_to_dest is: {}".format(
                    self.agent.name,
                    self.agent.get_from_mem(q_content["qid"])["ref_to_dest"],
                )
            )
            msg_body = {
                "qid": q_content["qid"],
                "type": "data",
                "ref": ref,
                "dest": dest,
            }

            add_msg.body = pickle.dumps(msg_body, 0).decode()

            await (self.send(add_msg))
            logger.debug(
                "({}):The address of the newly created data holon was just sent to {}".format(
                    self.agent.name, str(u.jid)
                )
            )


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
            if not self.agent.name == "data":  
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
            logger.debug(
                "({}): received content from ({}) is : {}".format(
                    self.agent.name, received_msg.sender, content
                )
            )
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
                logger.debug(
                    "({}): My memory content for ({}) is: {}".format(
                        self.agent.name,
                        content["qid"],
                        self.agent.get_from_mem(content["qid"]),
                    )
                )
                ref_to_dest = self.agent.get_from_mem(content["qid"])["ref_to_dest"]
                if ref_to_dest is None:  
                    self.agent.add_to_mem(
                        content["qid"], {"granted": content["co_addr"]}
                    )
                    logger.debug(
                        "({}): Just allowed ({}) access to my data for query ({})".format(
                            self.agent.name, content["co_addr"], content["qid"]
                        )
                    )
                else:
                    perf_msg = received_msg.make_reply()
                    perf_msg.to = ref_to_dest
                    await self.send(perf_msg)
                    logger.debug(
                        "({}): Just forwarded the perform message to ({})".format(
                            self.agent.name, perf_msg.to
                        )
                    )
            elif received_msg.get_metadata("performative") == Performatives.ACS:
                logger.debug(
                    "({}): I got an access request from ({})".format(
                        self.agent.name, str(received_msg.sender)
                    )
                )
                cnt_msg = received_msg.make_reply()
                cnt_msg.set_metadata("performative", Performatives.CNT)
                msg_body = {"qid": content["qid"], "data": "Nothing yet!"}
                if "granted" in self.agent.get_from_mem(content["qid"]).keys():
                    loop = asyncio.get_event_loop()
                    mod = importlib.import_module(
                        self.agent.get_KB().to_dict()["module"]
                    )
                    func = getattr(mod, self.agent.get_KB().to_dict()["function"],)
                    args = params_set_to_dict(self.agent.capabilities)
                    data = await loop.run_in_executor(
                        None, functools.partial(func, **args)
                    )
                    msg_body.update(
                        {
                            "granted": self.agent.get_from_mem(content["qid"])[
                                "granted"
                            ],
                            "data": data,
                            "data_id": self.agent.id,
                            "capabs": self.agent.capabilities,
                            "name": self.agent.get_from_mem(content["qid"])["name"],
                            "identifier": "{}\n({})".format(
                                self.agent.name, self.agent._label,
                            ),
                        }
                    )
                else:
                    msg_body.update({"granted": False})

                cnt_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                await self.send(cnt_msg)
                
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
                        and not self.agent.name == "data"
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
            q_content = pickle.loads(bytes(test_query.body, "ascii"))
            if test_query.get_metadata("performative") == Performatives.CHK:
                self.agent.add_to_mem(
                    q_content["qid"],
                    {
                        "check_count": len(self.agent.sub_holons),
                        "check_responders": {},  
                        "status": "checking",
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
                            "({}): I am not atomic so let's issue check to subs".format(
                                self.agent.name
                            )
                        )
                        for sub in self.agent.sub_holons:
                            await self.check_test_data(q_content, sub)
                            logger.debug(
                                "({}): sent test data check to sub {}".format(
                                    self.agent.name, sub.name
                                )
                            )
                    else:
                        logger.error(
                            "({}): I must not be atomic during test phase. The system should have at least a dataset".format(
                                self.agent.name
                            )
                        )
                else:  
                    logger.debug(
                        "({}): my name is {} and the name asked in query is {}".format(
                            self.agent.name, self.agent._label, q_content["name"]
                        )
                    )
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
                    if matched:
                        logger.debug(
                            "({}): my name and capabilities match the query's".format(
                                self.agent.name
                            )
                        )
                        if not self.agent.is_atomic():
                            logger.debug(
                                "({}): I am not atomic so let's issue check to subs".format(
                                    self.agent.name
                                )
                            )
                            for sub in self.agent.sub_holons:
                                await self.check_test_data(q_content, sub)
                                logger.debug(
                                    "({}): sent test data check to sub {}".format(
                                        self.agent.name, sub.name
                                    )
                                )
                        else:
                            logger.debug(
                                "({}): I am atomic during test phase, starting to prepare my response".format(
                                    self.agent.name
                                )
                            )
                            
                            self.agent.add_to_mem(
                                q_content["qid"],
                                {"accept_test": True, "name": q_content["name"]},
                            )
                            
                            res_msg = test_query.make_reply()
                            res_msg.set_metadata("performative", Performatives.RSP)
                            msg_body = {
                                "qid": q_content["qid"],
                                "data": {str(self.agent.jid): self.agent._label},
                            }
                            res_msg.body = pickle.dumps(msg_body, 0).decode()
                            await self.send(res_msg)
                            logger.debug(
                                "({}): just sent response {} to superholon ({})".format(
                                    self.agent.name, msg_body, res_msg.to
                                )
                            )
                    else:  
                        res_msg = test_query.make_reply()
                        res_msg.set_metadata("performative", Performatives.RSP)
                        msg_body = {
                            "qid": q_content["qid"],
                            "data": None,
                        }
                        res_msg.body = pickle.dumps(msg_body, 0).decode()
                        await self.send(res_msg)
                        logger.debug(
                            "({}): just sent response {} to superholon ({})".format(
                                self.agent.name, msg_body, res_msg.to
                            )
                        )
            elif test_query.get_metadata("performative") == Performatives.RSP:

                self.agent.get_from_mem(q_content["qid"])["check_responders"].update(
                    {test_query.sender: q_content["data"]}
                )
                if self.agent.get_from_mem(q_content["qid"])["check_count"] == len(
                    self.agent.get_from_mem(q_content["qid"])["check_responders"].keys()
                ):
                    logger.debug(
                        "({}): collected all data. Let's aggregate them all and send them to the super-holon".format(
                            self.agent.name
                        )
                    )
                    available_data = {}
                    for resv in self.agent.get_from_mem(q_content["qid"])[
                        "check_responders"
                    ].values():
                        if not resv is None:
                            available_data.update(resv)

                    for sup in self.agent.super_holons:
                        res_msg = test_query.make_reply()
                        res_msg.to = str(sup.jid)
                        msg_body = {
                            "qid": q_content["qid"],
                            "data": available_data,
                        }
                        res_msg.body = pickle.dumps(msg_body, 0).decode()
                        await self.send(res_msg)
                        logger.debug(
                            "({}): just sent response {} to superholon ({})".format(
                                self.agent.name, msg_body, str(sup.jid)
                            )
                        )
            elif test_query.get_metadata("performative") == Performatives.ACS:
                logger.debug(
                    "({}): I got an access request from ({})".format(
                        self.agent.name, str(test_query.sender)
                    )
                )
                cnt_msg = test_query.make_reply()
                cnt_msg.set_metadata("performative", Performatives.CNT)
                msg_body = {"qid": q_content["qid"], "data": "Nothing yet!"}
                
                if self.agent.get_from_mem(q_content["qid"])["accept_test"]:
                    loop = asyncio.get_event_loop()
                    mod = importlib.import_module(
                        self.agent.get_KB().to_dict()["module"]
                    )
                    func = getattr(mod, self.agent.get_KB().to_dict()["function"],)
                    args = params_set_to_dict(self.agent.capabilities)
                    data = await loop.run_in_executor(
                        None, functools.partial(func, **args)
                    )
                    msg_body.update(
                        {
                            "granted": True,
                            "data": data,
                            "name": self.agent.name,
                            "identifier": "{}\n({})".format(
                                self.agent.name, self.agent._label,
                            ),
                        }
                    )
                else:
                    msg_body.update({"granted": False})

                cnt_msg.body = pickle.dumps(msg_body, 0).decode("latin1")
                await self.send(cnt_msg)
                

    async def check_test_data(self, q_content, sub):
        check_msg = Message(to=str(sub.jid))
        check_msg.set_metadata("protocol", Protocols.TST)
        check_msg.set_metadata("performative", Performatives.CHK)
        msg_body = q_content
        
        check_msg.body = pickle.dumps(msg_body, 0).decode()
        await self.send(check_msg)


class DatH(Holon):
    def __init__(
        self,
        holon_jid,
        holon_pass,
        name,
        super_holons=None,
        color=VConfigs.data_node_color,
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

        send_content_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.CNT
        )

        send_access_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.ACS
        )

        train_res_template = get_template(
            protocol=Protocols.TRN, performative=Performatives.RES
        )

        send_template = (
            send_address_template
            | send_perfrom_template
            | send_content_template
            | send_access_template
            | train_res_template
        )

        self.add_behaviour(UpdateValueBehavior(), update_value_template)

        self.add_behaviour(TrainQueryBehavior(), train_templates)
        self.add_behaviour(SendBehavior(), send_template)

        test_check_template = get_template(
            protocol=Protocols.TST, performative=Performatives.CHK
        )
        test_resp_template = get_template(
            protocol=Protocols.TST, performative=Performatives.RSP
        )
        test_access_template = get_template(
            protocol=Protocols.TST, performative=Performatives.ACS
        )
        self.add_behaviour(
            TestQueryBehavior(),
            test_check_template | test_resp_template | test_access_template,
        )

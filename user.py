"""
    This file contains the definition of the User agent calss.
"""


import asyncio
import time
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour

from loguru import logger
from helping import *
from utilityclasses import *
from query import *

# from dummy_exps import *
from experiments import *


query_list = [
    classification_train_query,
    regression_train_query,
    clustering_query,
    add_data_query,
    test4,
    
]


class GenerateQuery(CyclicBehaviour):
    def __init__(self, num_times):
        super().__init__()
        self.num_times = num_times
        self._current = 0

    async def on_start(self):
        logger.debug("(USER):Starting generatQuery behavior...")
        if self.num_times < 0:
            self.num_times = 0

    async def run(self):
        if self._current < self.num_times:
           
            Q = query_list[self._current]
            ql = None
            if isinstance(Q, CompoundQuery):
                ql = Q.breakup()
            else:
                ql = [Q]
            for q in ql:
                if Q.type != Performatives.TST:
                    q.complete()
                query_msg = Message(to=str(DF.sys_jid))
                query_msg.set_metadata("protocol", Protocols.QRY)
                query_msg.set_metadata("performative", q.type)
                q_body = q.to_dict()
                
                query_msg.body = pickle.dumps(q_body, 0).decode()
                await self.send(query_msg)
                logger.debug("(USER):A query sent from user to {}".format(query_msg.to))
                await asyncio.sleep(2)
            self._current += 1

    def generate(self):
        return Query(
            qid="Q1",
            algorithms={"svm": {("p", "v")}},
            data={"iris": {}},
            measures={"eval": "accuracy"},
        )


class User(Agent):
    def __init__(self, jid, password, alias="user_agent"):
        super().__init__(jid, password)
        self.alias = alias

    async def setup(self):
        self.my_behav = GenerateQuery(len(query_list))
        self.add_behaviour(self.my_behav)

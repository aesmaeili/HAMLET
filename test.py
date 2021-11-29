import asyncio
import time
from spade.agent import Agent
from spade import quit_spade
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from holon import *
from sysh import *
from algh import *
from dath import *
from modh import *
from user import *

from helping import *
from utilityclasses import *
from visual import *


logger.remove()
# logger.add("log_debug.log")


class RandomSpawnBehavior(CyclicBehaviour):
    async def run(self):
        if True:
            for s in range(0, 2):
                SUB = Holon(
                    holon_jid=str(generate_uid()) + "@localhost",
                    holon_pass="SUB",
                    name="SUB",
                    super_holons=None,
                    color="black",
                )
                await SUB.start()
                self.agent.add_sub_holon(SUB)
                SUB.add_behaviour(RandomSpawnBehavior())
                await asyncio.sleep(1)


def main():

    SYS = SysH(holon_jid="SYS@localhost", holon_pass="SYS")
    SYS.start().result()
    ALG = AlgH(
        holon_jid="ALG@localhost",
        holon_pass="ALG",
        name="ALG",
        super_holons={SYS},
        color=VConfigs.algorithm_abstract_node_color,
        id_is_jid=False,
    )
    ALG.start().result()
    DATA = DatH(
        holon_jid="DATA@localhost",
        holon_pass="DATA",
        name="DATA",
        super_holons={SYS},
        color=VConfigs.data_abstract_node_color,
        id_is_jid=False,
    )
    DATA.start().result()

    user_agent = User("USER@localhost", "user")
    user_agent.start().result()

    Structure.started = True

   


if __name__ == "__main__":
    main()

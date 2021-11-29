"""
    This file contains the definition of the Holon calss as a
    first level entity in the system, together with the general
    and standard functionalities that a holon should have.
"""


from loguru import logger
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from helping import *
from utilityclasses import *





class Holon(Agent):
    """
    The holon class inhertits from the spade Agent class.
    Because a holon can behave like an agent.
    """

    class KB:
        def __init__(self, module="a module", func="a function"):
            self.mod = module
            self.fnc = func

        def to_dict(self):
            return {"module": self.mod, "function": self.fnc}

    @logger.catch
    def __init__(
        self,
        holon_jid,
        holon_pass,
        name,
        super_holons=set(),
        color="tab:blue",
        id_is_jid="true",
        is_terminal=False,
    ):
        """
        Args:
            holon_jid: The address of the holon on XMPP server
            Holon_pass: The password of the holon on the server
            name: The name of the holon. Not necessarily unique
            super_holons: The set containing super holons' reference in the holarchy
            color: The color in visual representation
            id_is_jid: if the current jid of the holon can be used as the id of it
        """
        super().__init__(holon_jid, holon_pass)
        self.super_holons = set()
        self.sub_holons = set()
        self.id = generate_uid() if not id_is_jid else extract_name(holon_jid)
        self._label = name
        self._memory = {}
        self._color = color
        self._position = np.asarray(
            [random.randrange(0, 100), random.randrange(0, 100)]
        )
        self.capabilities = set()
        self.skills = []
        self._KB = self.KB()
        self.role = None
        self.is_terminal = is_terminal

        

        if super_holons:
            for su in super_holons:
                self.add_super_holon(su)

    async def setup(self):
        logger.debug(
            "{} {} is born and its color and availability are {}, {}".format(
                type(self).__name__,
                self.name,
                self._color,
                self.presence.is_available(),
            )
        )
        Structure.G.add_node(
            self.id,
            Position=self._position,
            color=self._color,
            name=self.name,
            is_terminal=self.is_terminal,
        )
        Structure.all_agents.append(self)

    def set_KB(self, module="a module", func="a function"):
        self._KB = self.KB(module, func)

    def get_KB(self):
        return self._KB

    def add_super_holon(self, su, is_model=False):
        """
        Adds the the super holon object of the holon
        """
        if not su in self.super_holons:
            try:
                su.add_sub_holon(self, is_model)
                self.super_holons.add(su)
            except Exception as e:
                logger.error("EXCEPTION adding superholon {}: {}".format(su.jid, e))

    def add_sub_holon(self, sub_holon, is_model=False):
        """
        Adds sub_holon to its list of subordinate holons
        """
        if not sub_holon in self.sub_holons:
            try:
                color = VConfigs.normal_edge_color
                weight = VConfigs.normal_edge_weight
                style = VConfigs.normal_edge_style
                if not is_model:
                    self.sub_holons.add(sub_holon)
                else:
                    self.model_holons.add(sub_holon)
                    color = VConfigs.model_edge_color
                    weight = VConfigs.model_edge_weight
                    style = VConfigs.model_edge_style
                Structure.G.add_edge(
                    self.id, sub_holon.id, color=color, weight=weight, style=style
                )

            except Exception as e:
                logger.error(
                    "EXCEPTION adding subholon {}: {}".format(sub_holon.jid, e)
                )

    @logger.catch
    def add_to_mem(self, key, fact):
        """
        Adds a new entry in the memory

        Args:
            key: key of the memory entry
            fact: info to be stored, which can be of any type
        """
        if key in self._memory.keys():
            self._memory[key].update(fact)
        else:
            self._memory[key] = fact

    @logger.catch
    def get_from_mem(self, key):
        """
        Gets the fact from memory using its key

        Args:
            key: key of the fact in the memory
        """
        return self._memory[key]

    def get_entire_memory(self):
        return self._memory

    def is_atomic(self):
        """
        Checks to see if the holon is atomic
        """
        return len(self.sub_holons) == 0

    def get_name(self):
        """Returns the label of the holon as its name
        """
        return self._label

    def change_super(self, from_su, to_su):
        logger.debug(
            "({}): I am asked to change my super holon from ({}) to ({})".format(
                self.name, from_su.name, to_su.name
            )
        )
        self.super_holons.remove(from_su)
        from_su.sub_holons.remove(self)
        Structure.G.remove_edge(self.id, from_su.id)
        self.add_super_holon(to_su)


class HolonicBehavior(CyclicBehaviour):
    """
    This class contains all the behaviors that are common among
    all types of holons
    """

    """
    TODO: controlling the presence and subscriptions
    """

    async def run(self):
        pass


    async def forward_to_subs(self, msg):
        for s in self.agent.sub_holons:
            msg_copy = msg.make_reply()
            msg_copy.to = str(s)
            await self.send(msg_copy)



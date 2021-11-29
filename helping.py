import uuid
import numpy as np
import random
import os
import json
import pickle
import inspect
import importlib
import functools
from loguru import logger
from spade.template import Template

from utilityclasses import *


TRAIN_PROTOCOL = "TRAIN"
TEST_PROTOCOL = "TEST"
VERIFICATION_PROTOCOL = "VERIFY"

TRAIN_PERFORMATIVE = "train"
SINGLE_TEST_PERFORMATIVE = "single_test"
GROUP_TEST_PERFORMATIVE = "group_test"
CONFIRM_PERFORMATIVE = "confirm"
UNCONFIRM_PERFORMATIVE = "unconfirm"
RESULT_PERFORMATIVE = "result"
CANCEL_PERFORMATIVE = "cancel"
COMMAND_PERFORMATIVE = "command"


def generate_uid():
    """This function generates a unique id when it's needed."""
    return str(uuid.uuid4())


def prosody_cleanup():
    os.system(
        "sudo rm -rf /var/lib/prosody/localhost/accounts/ /var/lib/prosody/localhost/account_details/"
    )


def extract_name(jid):
    """Extracts the name out of the complete holon jid.

    Args:
        jid: the jid of the holon/agent in the system

    Returns:
        str: the name
    """
    return jid.split("@")[0]


def get_template(**citeria):
    """Provides the template object for the given criteria
    """
    temp = Template()
    for key, value in citeria.items():
        temp.set_metadata(key, value)
    return temp


def param_congruent(p1, p2):
    if isinstance(p1, tuple) and isinstance(p2, tuple):
        return p1[0] == p2[0]
    elif isinstance(p1, set) and isinstance(p2, set):
        res = len(p1) == len(p2)
        if res:
            for p in p1:
                temp = False
                for pp in p2:
                    if param_congruent(p, pp):
                        temp = True
                        break
                if not temp:
                    return False
        return res
    else:
        raise ValueError("(param_congruence): The arguments are not tuple nor sets")


def param_lt(p1, p2):
    # if not param_congruent(p1, p2):
    #     raise ValueError(
    #         "(param_lt): the arguments are not comparible because they are not congruent"
    #     )
    # else:
    if isinstance(p1, tuple) and isinstance(p2, tuple):
        if param_congruent(p1, p2):
            return (
                p1[1] == p2[1]
                or p2[1] == Constants.GENERAL_CHAR
                or p1[1] == Constants.GENERAL_CHAR
            )
    elif isinstance(p1, set) and isinstance(p2, set):
        if len(p1) == 0:
            
            return True
        for p in p1:
            temp = False
            for pp in p2:
                if param_congruent(p, pp):
                    temp = param_lt(p, pp)
                    break
            if not temp:
                return False
        return True


def param_sum(p1, p2):
    logger.debug("(param_sum): I am called with p1:{} and p2:{}".format(p1, p2))
    if len(p1) == 0:
        return p2
    elif len(p2) == 0:
        return p1
    elif not param_congruent(p1, p2):
        raise ValueError(
            "(param_sum): the arguments are not comparible because they are not congruent"
        )
    else:
        if isinstance(p1, tuple) and isinstance(p2, tuple):
            if p1[1] == p2[1]:
                return p1
            else:
                return (p1[0], Constants.GENERAL_CHAR)
        elif isinstance(p1, set) and isinstance(p2, set):
            res = set()
            for p in p1:
                for pp in p2:
                    if param_congruent(p, pp):
                        res = res | {param_sum(p, pp)}
                        break
            return res


def param_sim_ratio(p1, p2):
    logger.debug("(param_sim_ratio): I am called with p1:{} and p2:{}".format(p1, p2))
    if not param_congruent(p1, p2):
        raise ValueError(
            "(param_sim_ratio): the arguments are not comparible because they are not congruent"
        )
    else:
        if isinstance(p1, tuple) and isinstance(p2, tuple):
            if p1[1] == p2[1]:
                return 1
            elif (p1[1] == Constants.GENERAL_CHAR) ^ (p2[1] == Constants.GENERAL_CHAR):
                return Constants.ALPHA
            else:
                return Constants.BETA
        elif isinstance(p1, set) and isinstance(p2, set):
            sums = 0
            muls = 1
            for p in p1:
                for pp in p2:
                    if param_congruent(p, pp):
                        if p[1] == pp[1]:
                            sums += param_sim_ratio(p, pp)
                        else:
                            muls *= param_sim_ratio(p, pp)
                        break
            if (
                muls == 1
            ):  
                muls = 0
            logger.debug(
                "sim({},{})={}, because sums={}, muls={}, len={}".format(
                    p1, p2, (sums + muls) / len(p1), sums, muls, len(p1)
                )
            )
            return (sums + muls) / len(p1)


def argmax(a_dict):
    logger.debug("(argmax): I am called with a_dict:{}".format(a_dict))
    if not isinstance(a_dict, dict):
        raise ValueError("A dictionary is expected as the argument")
    else:
        mx = -float("inf")
        agmx = None
        for k, v in a_dict.items():
            if v > mx:
                agmx = k
                mx = v
        return agmx


def extract_params(a_func):
    params = set()
    sig = inspect.signature(a_func)
    for v in sig.parameters.values():
        params.add((v.name, v.default))
    return params


def combine_params(defaults_params_set, params_set):
    output = set()
    for d in defaults_params_set:
        found = False
        for t in params_set:
            if d[0] == t[0]:
                output.add(t)
                found = True
                break
        if not found:
            output.add(d)
    return output


def complete_params(module, func, params_set):
    
    if func == Constants.GENERAL_CHAR or is_general_set(params_set):
        return params_set
    else:
        mod = importlib.import_module(module)
        defaults = extract_params(getattr(mod, func))
        return combine_params(defaults, params_set)


def is_general_set(params_set):
    for t in params_set:
        if t[1] == Constants.GENERAL_CHAR:
            return True
    return False


def params_set_to_dict(params_set):
    output = {}
    for p in params_set:
        output.update({p[0]: p[1]})
    return output



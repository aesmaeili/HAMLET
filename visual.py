import asyncio
import time
import os
import sys
import math
import re
from spade.agent import Agent
from spade import quit_spade
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour

import pygraphviz
from networkx.drawing.nx_agraph import graphviz_layout
from loguru import logger
import matplotlib.backends.backend_pdf

from helping import *
from utilityclasses import *
import pandas as pd


class VisualizeStructure(CyclicBehaviour):
    async def on_start(self):
        logger.debug("Starting visualizing behavior...")
        

    async def run(self):
        viz_msg = await self.receive(timeout=10)
        if viz_msg:
            content = pickle.loads(bytes(viz_msg.body, "latin1"))
            
            graph = Structure.G
            struct = None
            terminals = None

            if not content["hide_color"] is None:
                nodes = (
                    node
                    for node, data in graph.nodes(data=True)
                    if data.get("color") != content["hide_color"]
                )
                ts = (
                    node
                    for node, data in graph.nodes(data=True)
                    if data.get("is_terminal")
                )
                struct = graph.subgraph(nodes)
                terminals = graph.subgraph(ts)
            
            colors = [
                c[1] for c in list(struct.nodes(data="color", default="tab:gray"))
            ]
            h_types = list(struct.nodes(data="h_type"))
            names = list(struct.nodes(data="name"))
            edge_colors = [struct[u][v]["color"] for u, v in struct.edges()]
            edge_weights = [struct[u][v]["weight"] for u, v in struct.edges()]
            edge_styles = [struct[u][v]["style"] for u, v in struct.edges()]
            label_map = {}
            for n in names:
                label_map[n[0]] = n[1]
            pos = graphviz_layout(
                struct, prog="neato", args=""
            )  

            ntw_file_name = "Network" + time.strftime("%m-%d %H:%M:%S")
            network_pdf = matplotlib.backends.backend_pdf.PdfPages(
                ntw_file_name + ".pdf"
            )
            struct_fig, st_axes = plt.subplots()  # figsize=(10, 10))
            struct_fig.canvas.set_window_title("Structure")
            
            modh_nodes = []
            datah_nodes = []
            algh_nodes = []
            data_node = []
            alg_node = []
            sys_node = []
            pos = nx.kamada_kawai_layout(struct)
            for node, data in struct.nodes(data=True):
                if data.get("color") == VConfigs.model_node_color:
                    modh_nodes.append(node)
                elif data.get("color") == VConfigs.data_node_color:
                    datah_nodes.append(node)
                elif data.get("color") == VConfigs.algorithm_node_color:
                    algh_nodes.append(node)
                elif data.get("color") == VConfigs.data_abstract_node_color:
                    data_node.append(node)
                elif data.get("color") == VConfigs.algorithm_abstract_node_color:
                    alg_node.append(node)
                elif data.get("color") == VConfigs.system_node_color:
                    sys_node.append(node)

            nx.draw_networkx_nodes(
                struct,
                nodelist=sys_node,
                pos=pos,
                node_color=VConfigs.system_node_color,
                
                font_size=7,
                
                ax=st_axes,
                label="SYS",
                edgecolors="k",
            )

            nx.draw_networkx_nodes(
                struct,
                nodelist=alg_node,
                pos=pos,
                node_color=VConfigs.algorithm_abstract_node_color,
                
                font_size=7,
                
                ax=st_axes,
                label="ALG",
                edgecolors="k",
            )

            nx.draw_networkx_nodes(
                struct,
                nodelist=algh_nodes,
                pos=pos,
                node_color=VConfigs.algorithm_node_color,
                
                font_size=7,
                
                ax=st_axes,
                label="AlgH",
                edgecolors="k",
            )
            nx.draw_networkx_nodes(
                struct,
                nodelist=data_node,
                pos=pos,
                node_color=VConfigs.data_abstract_node_color,
                
                font_size=7,
                
                ax=st_axes,
                label="DATA",
                edgecolors="k",
            )

            nx.draw_networkx_nodes(
                struct,
                nodelist=datah_nodes,
                pos=pos,
                node_color=VConfigs.data_node_color,
                
                font_size=7,
                
                ax=st_axes,
                label="DataH",
                edgecolors="k",
            )

            nx.draw_networkx_edges(
                struct,
                pos=pos,
                width=edge_weights,
                style=edge_styles,
                edge_color=edge_colors,
                ax=st_axes,
            )
            st_axes.legend(scatterpoints=1, loc="upper right")
            network_pdf.savefig(struct_fig)

            terminal_fig, t_axes = plt.subplots()
            terminal_fig.canvas.set_window_title("Atomic connections")
            t_cols = [
                c[1] for c in list(terminals.nodes(data="color", default="tab:gray"))
            ]
            ec = [terminals[u][v]["color"] for u, v in terminals.edges()]
            ew = [terminals[u][v]["weight"] for u, v in terminals.edges()]
            es = [terminals[u][v]["style"] for u, v in terminals.edges()]
            
            modh_nodes = []
            datah_nodes = []
            algh_nodes = []
            pos = nx.spring_layout(terminals, k=0.23, seed=0)
            for node, data in terminals.nodes(data=True):
                if data.get("color") == VConfigs.model_node_color:
                    modh_nodes.append(node)
                elif data.get("color") == VConfigs.data_node_color:
                    datah_nodes.append(node)
                elif data.get("color") == VConfigs.algorithm_node_color:
                    algh_nodes.append(node)

            nx.draw_networkx_nodes(
                terminals,
                nodelist=algh_nodes,
                pos=pos,
                node_color=VConfigs.algorithm_node_color,
                
                font_size=7,
                
                ax=t_axes,
                label="AlgH",
                edgecolors="k",
            )
            nx.draw_networkx_nodes(
                terminals,
                nodelist=datah_nodes,
                pos=pos,
                node_color=VConfigs.data_node_color,
                
                font_size=7,
                
                ax=t_axes,
                label="DataH",
                edgecolors="k",
            )

            nx.draw_networkx_nodes(
                terminals,
                nodelist=modh_nodes,
                pos=pos,
                node_color=VConfigs.model_node_color,
                
                font_size=7,
                
                ax=t_axes,
                label="ModH",
                edgecolors="k",
            )

            nx.draw_networkx_edges(
                terminals, pos=pos, width=ew, style=es, edge_color=ec, ax=t_axes,
            )
            t_axes.legend(scatterpoints=1, loc="upper right")

            network_pdf.savefig(terminal_fig)
            network_pdf.close()

            

            plt.axis("equal")
            plt.legend(scatterpoints=1, loc="upper right")
            await asyncio.sleep(1)

    async def handle_close_window(self, evt):
        await quit_spade()


class VisualizeResults(CyclicBehaviour):
    
    async def run(self):
        results_msg = await self.receive(timeout=10)
        if results_msg:
            figs_dir_name = time.strftime("%m-%d %H:%M:%S")
            figs_dir = os.path.join(VConfigs.save_dir, figs_dir_name)
            if not os.path.isdir(figs_dir):
                os.makedirs(figs_dir)
            content = pickle.loads(bytes(results_msg.body, "latin1"))
            if results_msg.get_metadata("protocol") == Protocols.VIZ:
                
                c = 0
                
                nr = content["results"].shape[0]
                print("Received {} to visualize".format(content["results"]))
                content["results"].to_pickle(str(content["qid"])+".pkl")
                
                interesting_evals = []
                for row in range(content["results"].shape[0]):
                    for r in content["results"].values[row]:
                        d = None
                        if isinstance(r, dict):
                            d = r
                        elif isinstance(r, list):
                            d = r[0]
                        if not d is None:
                            for dk in d.keys():
                                if not dk in interesting_evals: 
                                    interesting_evals.append(dk)
                
                nc = (
                    len(interesting_evals) - 1
                    if "time" in interesting_evals
                    else len(interesting_evals)
                )  
                fig, axs = plt.subplots(
                    nr, nc, squeeze=False, figsize=(10, 15), sharey=True,  # sharex=True
                )
                fig.canvas.set_window_title(content["qid"])
                all_in_one_pdf = matplotlib.backends.backend_pdf.PdfPages(
                    content["qid"] + "-----" + figs_dir_name + ".pdf"
                )
                
                res_df = content["results"]
                res_df.sort_index(axis=1, inplace=True)
                res_df.sort_index(inplace=True)
               
                for efk in interesting_evals:
                    if efk != "time":
                        for r in range(res_df.shape[0]):
                            y = []
                            x2 = []
                            is_all_nan = True
                            for i, d in enumerate(res_df.values[r]):
                                if isinstance(d, dict) or isinstance(d, list):
                                    d = d if isinstance(d, dict) else d[0]
                                    if efk in d.keys():
                                        y.append(d[efk])
                                        x2.append(res_df.columns[i])
                                        is_all_nan = False
                                    
                            if is_all_nan:
                                axs[r, c].axis("off")
                            else:
                                axs[r, c].plot(
                                    x2, y, color="tab:red", marker="o", linewidth=1.5
                                )
                                axs[r, c].tick_params(axis="y", labelcolor="tab:red")
                                axs[r, c].grid(True, "both", "y")
                                if r == 0:
                                    axs[r, c].set_title(efk, color="tab:red")
                                if c == 0:
                                    axs[r, c].set_ylabel(
                                        list(res_df.index)[r].replace("_", " "),
                                        multialignment="center",
                                    )
                                    axs[r, c].set_xlabel(
                                        "Algorithms", size="large"
                                    ) 
                                temp_fig, temp_ax = plt.subplots()
                                temp_ax.plot(
                                    x2, y, color="tab:red", marker="o", linewidth=1.5
                                )
                                if "time" in interesting_evals:
                                    temp_ax.tick_params(axis="y", labelcolor="tab:red")
                                temp_ax.grid(True, "both", "y")
                                ttl = list(res_df.index)[r].replace("_", " ")
                                m = re.search(".*\((.*)\)", ttl.split("\n")[1])
                                st = m.group(1)
                                if st == "make moons":
                                    st = "artificial moon"
                                elif st == "make classification":
                                    st = "artificial classification"
                                elif st == "make regression":
                                    st = "artificial regression"
                                temp_ax.set_title(st + " dataset", size="large")
                                if "time" in interesting_evals:
                                    temp_ax.set_ylabel(
                                        efk.replace("_", " "),
                                        multialignment="center",
                                        size="large",
                                        color="tab:red",
                                    )
                                    temp_ax.set_xlabel("Algorithms", size="large")
                                else:
                                    temp_ax.set_ylabel(
                                        efk.replace("_", " "),
                                        multialignment="center",
                                        size="large",
                                    )
                                    temp_ax.set_xlabel("Algorithms", size="large")
                                
                                if "time" in interesting_evals:
                                    time_ax = axs[r, c].twinx()
                                    time_ax2 = temp_ax.twinx()
                                    time_ax.set_ylabel(
                                        "training time(s)",
                                        color="tab:blue",
                                        size="large",
                                    )
                                    time_ax2.set_ylabel(
                                        "training time(s)",
                                        color="tab:blue",
                                        size="large",
                                    )
                                    t = []
                                    
                                    for i, d in enumerate(res_df.values[r]):
                                        if isinstance(d, dict) or isinstance(d, list):
                                            d = d if isinstance(d, dict) else d[0]
                                            t.append(d["time"])
                                    time_ax.plot(
                                        x2,
                                        t,
                                        color="tab:blue",
                                        marker="o",
                                        linewidth=0.8,
                                    )
                                    time_ax.tick_params(axis="y", labelcolor="tab:blue")
                                    
                                    time_ax2.plot(
                                        x2,
                                        t,
                                        color="tab:blue",
                                        marker="o",
                                        linewidth=0.8,
                                    )
                                    
                                    time_ax2.tick_params(
                                        axis="y", labelcolor="tab:blue"
                                    )
                                fig_name = "{} of {}.pdf".format(
                                    efk, list(res_df.index)[r]
                                )
                                comp_fig_name = os.path.join(figs_dir, fig_name)
                                all_in_one_pdf.savefig(temp_fig, bbox_inches="tight")
                                plt.close(temp_fig)
                        c += 1
                all_in_one_pdf.close()
                fig.tight_layout()

            elif results_msg.get_metadata("protocol") == Protocols.TST:
                pass
        else:
            plt.style.use(VConfigs.plot_style)
            sys.stdout.write("\a")
            sys.stdout.flush()
            plt.show()


class VisAgent(Agent):
    def __init__(self, jid, password, alias="visualizer", typ="structure"):
        super().__init__(jid, password)
        self.alias = alias
        self.type = typ

    async def setup(self):
        print("Agent {} starting ...".format(self.name))
        if self.type == "structure":
            structure_viz_template = get_template(
                protocol=Protocols.TRN, performative=Performatives.STR
            )
            self.add_behaviour(VisualizeStructure(), structure_viz_template)
        elif self.type == "results":
            results_viz_template = get_template(
                protocol=Protocols.VIZ, performative=Performatives.RES
            )

            self.add_behaviour(VisualizeResults(), results_viz_template)

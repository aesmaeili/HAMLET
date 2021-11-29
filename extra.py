import igraph

print(igraph.__version__)
# g = igraph.read("structure.net", format="pajek")
g = igraph.read("structure_0.net", format="pajek")
l = g.layout_reingold_tilford_circular(mode="all")
# l = g.layout_reingold_tilford(mode="all")

igraph.plot(g, layout=l)

import pandas as pd
import re
import numpy as np
from webweb import Web
import hashlib
import networkx as nx
import matplotlib.pyplot as plt
import  utils
import keywords_icalt

listHashtagsRT2 = utils.get_hashtagsRT2("/home/fernando/Documentos/Lynguo_def2.csv", keywords_icalt.k, keywords_icalt.k_stop)
edges2 = utils.get_edgesHashRT2(listHashtagsRT2)

G = nx.Graph()
G.add_edges_from(edges2)
subgraphs = utils.get_subgraphs(G)
subgraphs = [graph for graph in subgraphs if len(graph.nodes) > 5]
web = Web(title="HashtagsRT", nx_G=subgraphs[0])
web.display.gravity = 1

name ="graph"
for i in range(2, len(subgraphs)):
    web.networks.hashrts.add_layer(nx_G=subgraphs[i])

# show the visualization
web.show()
import pandas as pd
import re
from webweb import Web
import hashlib
import networkx as nx
import utils
import keywords_icalt

hashmain = utils.get_hashtagsmain("/home/fernando/Documentos/Lynguo_def2.csv", keywords_icalt.k, keywords_icalt.k_stop)
hashmain2= utils.mainHashtags(hashmain)
hashtags_edges = utils.prepare_hashtags2(hashmain2)

G = nx.Graph()
G.add_edges_from(hashtags_edges)
#subgraphs = utils.get_subgraphs(G)
#subgraphs = [graph for graph in subgraphs if len(graph.nodes) > 5]

web = Web(title="Main Hashtags",nx_G=G)
#web = Web(title="Main Hashtags", nx_G=subgraphs[0])
web.display.gravity = 1

#for i in range(2, len(subgraphs)):
   # web.networks.hashtags.add_layer(nx_G=subgraphs[i])

# show the visualization
web.show()
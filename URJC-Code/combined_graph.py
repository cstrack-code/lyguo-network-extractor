from webweb import Web
import networkx as nx
import  utils
import keywords_icalt

retweetList = utils.get_retweets("/home/fernando/Documentos/Lynguo_def2.csv", keywords_icalt.k, keywords_icalt.k_stop)
retweetEdges = utils.get_edges(retweetList)

mentionList = utils.get_cites("/home/fernando/Documentos/Lynguo_def2.csv", keywords_icalt.k, keywords_icalt.k_stop)
mentionEdges = utils.get_edges(mentionList)

combined_edges = utils.combined_edges(mentionEdges,retweetEdges)

G = nx.Graph()
G.add_edges_from(combined_edges)
subgraphs = utils.get_subgraphs(G)
subgraphs = [graph for graph in subgraphs if len(graph.nodes) > 5]

web = Web(title="Cmbined graph", nx_G=subgraphs[0])
web.display.gravity = 1

name ="graph"
for i in range(2, len(subgraphs)):
    web.networks.rtscites.add_layer(nx_G=subgraphs[i])

# show the visualization
web.show()

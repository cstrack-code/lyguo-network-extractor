import pandas as pd
import csv
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import community as community_louvain
import twitter
from collections.abc import Iterable
import defaults


# def get_pos():


def draw_network(g):
    weights = nx.get_edge_attributes(g, 'weight')
    # custom_weights = {k: v*1000 for k, v in weights.items()}

    maxWeight = max(weights.values())

    # pos = nx.spring_layout(g, weight="custom_weights", iterations=100)  # positions for all nodes
    pos = nx.spring_layout(g, weight="weight", iterations=50)  # positions for all nodes
    edge_labels = nx.get_edge_attributes(g, 'weight')
    nx.draw_networkx_edges(g, pos, edgelist=g.edges, width=2)
    nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=8)

    colors = range(maxWeight)
    print("max(weight):", maxWeight)
    options = {
        "node_color": "#A0CBE2",
        "node_size": 300,
        "width": 4,
        "edge_cmap": plt.cm.Blues,
        "with_labels": True,
        "pos": pos
    }
    nx.draw(g, **options)

    plt.axis('off')
    plt.savefig("export/work.png")  # save as png
    plt.show()  # display


def draw_network_communities(graph, g_partition):
    pos = nx.spring_layout(graph, weight="weight", iterations=50)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    # color the nodes according to their partition
    cmap = cm.get_cmap('viridis', max(g_partition.values()) + 1)
    if "followerscount" in g_partition.values():
        nx.draw_networkx_nodes(graph, pos, g_partition.keys(), node_size=list(g_partition.values()['followerscount']),
                               cmap=cmap,
                               node_color=list(g_partition.values()))
    else:
        nx.draw_networkx_nodes(graph, pos, g_partition.keys(), node_size=40, cmap=cmap,
                               node_color=list(g_partition.values()))
    nx.draw_networkx_edges(graph, pos, alpha=0.5)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=8)
    nx.draw_networkx_labels(graph, pos, font_size=6)
    plt.savefig("export/community-detection.png", format="PNG")
    plt.show()


def community_detection_louvain(g):
    if g.is_directed():
        print("[WARNING] g is directed - converting into undirected graph")
        g = g.to_undirected()
    partition = community_louvain.best_partition(g)
    return partition


def create_subgraph(g, min_weight=1):
    elarge = [(u, v) for (u, v, d) in g.edges(data=True) if d['weight'] >= min_weight]
    h = g.edge_subgraph(elarge)
    print(h.nodes)
    print(h.edges)
    return h


def export_gml(G):
    print("Exporting Graph:", G)
    nx.write_gml(G, "export/export.gml")


def create_dataframe(file=defaults.LYNGUO_CSV_FILE):
    # use sniffing to create the correct csv dialect
    with open(file) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(14734))

    # some of the original lynguo CSV exports contain problematic line breaks (mixing \n and \r\n)

    df = pd.read_csv(filepath_or_buffer=file, dialect=dialect, encoding="1252")
    print(df)
    return df


# the GML specification does not allow underscores
def create_empty_attribute_set(default_key, username):
    return {
        'description': default_key,
        'location': default_key,
        'name': username,
        'followerscount': default_key,
        'friendscount': default_key,
        'listedcount': default_key,
        'favouritescount': default_key,
        'verified': default_key,
        'geoenabled': default_key,
        'statusescount': default_key,
        'protected': default_key,
        'lang': default_key,
        'url': default_key
    }


def create_user_profile(user):
    user_json = {
        'description': user.get('description', ''),
        'location': user.get('location', ''),
        'name': user.get('name', ''),
        'followerscount': user.get('followers_count', ''),
        'friendscount': user.get('friends_count', ''),
        'listedcount': user.get('listed_count', ''),
        'favouritescount': user.get('favourites_count', ''),
        'verified': user.get('verified', ''),
        'geoenabled': user.get('geo_enabled', ''),
        'statusescount': user.get('statuses_count', ''),
        'protected': user.get('protected', ''),
        'lang': user.get('lang', ''),
        'url': user.get('url', '')
    }
    for key in user_json:
        if user_json[key] == None:
            user_json[key] = defaults.DEFAULT_NONE_VAL
    return user_json


# the GML specification does not allow underscores
def get_node_attributes_for(username):
    profile = twitter.retrieve_profile(username)
    if profile is None or not isinstance(profile, dict):
        print("[WARNING] empty profile for user", username)
        return create_empty_attribute_set(defaults.DEFAULT_VAL, username)
    if not isinstance(profile, Iterable):
        print("[WARNING] profile is not iterable for user", username)
        return False
    if "error_code" in profile:
        print("[WARNING] error", profile['error_code'], "retrieving the twitter profile for user", username)
        return create_empty_attribute_set(defaults.DEFAULT_SUSPENDED_PROFILE, username)
    try:
        json = create_user_profile(profile)
    except KeyError as e:
        print("[WARNING] Could not read property", e.args[0], "from user", username)
        return False

    return json


def create_twitter_network(dataframe, limit=0, attach_twitter_profiles=defaults.attach_twitter_profiles):
    G = nx.DiGraph()
    i = 0
    for row in dataframe.iterrows():
        user = row[1].get("Usuario")
        text = row[1].get("Texto")
        interest = row[1].get("Marca")
        # retweets
        try:
            # just to limit the network and execution time
            if i == limit:
                break

            # Retweet network: if text starts with "RT @" then it is a retweet
            # texto: index 4
            # usuario: index 7
            if interest == defaults.LYNGUO_INTEREST and text.startswith(defaults.SNA_RT_PATTERN):
                start = text.find(defaults.SNA_RT_PATTERN) + len(defaults.SNA_RT_PATTERN)
                end = start + text[start:].find(" ")
                # print("start:", start, ", end:", end)
                retweetedUser = text[start:end - 1]
                # print(retweetedUser)

                # node attributes: followerscount, description
                if user is None or retweetedUser is None:
                    print("[WARNING] discarding edge - user:", user, ", retweetedUser:", retweetedUser)
                    continue

                # construct network
                if attach_twitter_profiles:
                    user_profile_info = get_node_attributes_for(user)
                    if not user_profile_info: continue
                    G.add_node(user, attr_dict=user_profile_info)
                    retweeted_user_profile_info = get_node_attributes_for(retweetedUser)
                    if not retweeted_user_profile_info: continue
                    G.add_node(retweetedUser, attr_dict=retweeted_user_profile_info)
                else:
                    G.add_node(user)
                    G.add_node(retweetedUser)

                weight = 1
                # if edge exists, update weight
                if G.has_edge(user, retweetedUser) and 'type' in G[user][retweetedUser] and G[user][retweetedUser][
                    'type'] == defaults.SNA_EDGE_LABEL_RT:
                    weight = G[user][retweetedUser]['weight'] + 1
                G.add_edge(user, retweetedUser, weight=weight, type=defaults.SNA_EDGE_LABEL_RT)
                # print(user, "--RT(" + str(weight) + ")-->", retweetedUser)

                i += 1

        except AttributeError:
            print("AttributeError in row for user:", user, ", retweetedUser:", retweetedUser)
            # print(row)
            continue

    return G


def attach_user_profiles(g):
    for n in g.nodes:
        attributes = get_node_attributes_for(n);
        if g.nodes[n] is None:
            print("[WARNING] attaching user profile to value None is not working. Check user", n)
            continue
        g.nodes[n].update(attributes)
    return g


df = create_dataframe()
g = create_twitter_network(df, 5000000, False)
print("Network consists of", len(g.edges), "edges")
h = create_subgraph(g, 5)
# h = attach_user_profiles(h)

# retrieve all profiles for the nodes
# twitter.retrieve_profiles(h.nodes)

print("Subgraph consists of", len(h.edges), "edges")
# draw_network(h)
export_gml(g)

partition = community_detection_louvain(h)
draw_network_communities(h, partition)

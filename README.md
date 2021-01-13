# Lynguo Tools
The lynguo tools are useful for importing lynguo datasets and to construct networks based
on the relations of the underlying social networks. For example, Twitter exposes the inherent relations "retweet",
"follow", "comment" or "like" relations. The lynguo-tools module can be used to import a lynguo file
and to construct the network, export this as GML, create subgraphs based on filtering or to explore the data interactively.  

## Read Lynguo CSV


## attach twitter profiles to networks
1. Go to defaults.py
2. Set 

       attach_twitter_profiles = True

3. configure the Twitter API 

If you run the application with attaching user profiles, the retrieved profiles are stored in a local MongoDB
in order to reduce the number of API calls. The later calls to user profiles are then cached through the DB.
You can deactivate that by setting the caching to False.

## Configure the Twitter API
The Twitter API is used to enrich the data by retrieving profile information from
the nodes of the constructed network from the lynguo dataset. You need to sign in for a twitter
account at the twitter developer page. In the application, set your API keys in defaults.py


# -*- coding: utf-8 -*-
'''
VICTOR GARCIA PINA
'''

from time import sleep
import networkx as nx
import tweepy
import pickle
import sys

#### AÑADIR LAS CREDENCIALES DE TWITTER PARA PODER EJECUTAR EL PROGRAMA #####

API_KEY = ""
API_SECRET_KEY = ""
ACCESS_TOKEN = ""
ACCESS_SECRET_TOKEN = ""

BEARER_TOKEN = ""
################

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Nombre de la cuenta de twitter desde la que se quiere iniciar el grafo
user = ""
seed_node = api.get_user( user )


def loadGraph(file_name):
    '''
    :param file_name: name of the file that will be loaded.
    :return: a graph in networkxs format.
    '''
    with open(file_name, 'rb') as f:
        G = pickle.load(f)
    return G

#### FUNCIONS QUE ES DEMANEN EN L'ENUNCIAT DE LA PART 1 DE LA PRACTICA   #####

def crawler(seed_node, max_nodes_to_crawl):
    '''
    :param seed_node: node_id of the first node to explore by the crawler.
    :param max_nodes_to_crawl: total number of nodes to explore. The crawler stops after the number has been reached.
    :return: the constructed graph.
    '''
    
    def createNode(user):
        '''
        Creem un node del graf amb els atributs correponents.
        :param user: user object de la llibreria tweepy.
        '''
        if user.screen_name not in G:
            atts = {user.screen_name:{'num_followers':  user.followers_count,
                                      'num_friends':    user.friends_count,
                                      'id':             user.id,
                                      'location':       user.location,
                                      'num_favourites': user.favourites_count,
                                      'verified':       user.verified,
                                      'num_tweets':     user.statuses_count,
                                      'protected':      user.protected}}
            
            G.add_node(user.screen_name)
            nx.set_node_attributes(G, atts)

    def validUser(user):
        '''
        Definim a un usuari vàlid si té <10.000 seguidors/amics, 
        >99 seguidors/amics i té més de 1000 likes o retweets
        :param node: user object de la llibreria tweepy
        :return: bool
        '''
        if (user.followers_count > 10000 or user.friends_count > 10000) or \
        (user.followers_count < 99 or user.friends_count < 99):
            return False
        elif user.favourites_count < 1000 or user.protected: return False
        return True
    
    def exploreFollowers(user):
        '''
        Descobrim els followers d'un usuari donat
        i creem els vertex i arestes pertinents
        :param user: user object de la llibreria tweepy
        '''
        print(f'Explorant els followers de {user.screen_name}...')
        for i, follower in enumerate(tweepy.Cursor(api.followers, user_id=user.id, count=200).items()):
            if i%200 == 0:
                print('Sleeping for 1 minute.')
                sleep(60)
                print('Iteració (followers)',i+1)
            createNode(follower)
            G.add_edge(follower.screen_name, user.screen_name)
        print("Fi de l'exploració.\n")
        
    def exploreFriends(user):
        '''
        Descobrim els amics d'un usuari donat
        i creem els vertex i arestes pertinents
        :param user: user object de la llibreria tweepy
        '''
        print(f'Explorant els amics de {user.screen_name}...')
        for i, friend in enumerate(tweepy.Cursor(api.friends, user_id=user.id, count=200).items()):
            if i%200 == 0:
                print('Sleeping for 1 minute.')
                sleep(60)
                print('Iteració (friends)',i+1)
            createNode(friend)
            G.add_edge(user.screen_name, friend.screen_name)
        print("Fi de l'exploració.\n")
    
    G = nx.DiGraph()
    # Creem el node de l'usuari llavor
    createNode(seed_node)
    
    # Llista de nodes a explorar, relacionats amb el seed node
    explore = []
    
    print(f'Explorant els amics del node incial: {seed_node.screen_name}')
    # Iteració dels amics del seed node utilitzant 'Cursor'
    for i, friend in enumerate(tweepy.Cursor(api.friends, user_id=seed_node.id, count=200).items()):
        if i%200 == 0:
            print('Sleeping for 1 minute.')
            sleep(60)
            print('Iterant pels amics del seed node:',i+1)
        createNode(friend)
        G.add_edge(seed_node.screen_name, friend.screen_name)
        '''
        En el cas de que la longitud de la llista de nodes a explorar
        sigui < al màxim de nodes a explorar, mirem si l'usuari es un usuari valid,
        si es així el fiquem a la llista per després fer l'exploració.
        '''
        if len(explore) < max_nodes_to_crawl:
            if validUser(friend):
                explore.append(friend)
    print("Fi de l'exploració.\n")
    
    # Iteració dels followers del seed node utilitzant 'Cursor'
    exploreFollowers(seed_node)
    
    # Iteració dels amics i followers dels nodes a explorar
    for i, node_ex in enumerate(explore):
        print(f'Explorant node {i+1}/{max_nodes_to_crawl}: {node_ex.screen_name}.\n')
        exploreFriends(node_ex)
        exploreFollowers(node_ex)
    
    print('### Exploració TOTAL finalitzada! ###\n')
    
    file_name = seed_node.screen_name+'_'+str(max_nodes_to_crawl)+'.pickle'
    print(f"Guardant el graf creat com a: {file_name}")
    try:
        with open(file_name, 'wb') as file:
            pickle.dump(G, file, pickle.HIGHEST_PROTOCOL)
    except:
        print(f'ERROR: Error al intentar guardar el graf amb el nom {file_name}')
        sys.exit(1)
        
    print('Programa finalitzat correctament.\n')
    return G


def export_graph_to_gexf(G, file_name):
    '''
    :param g: A graph with the corresponding networkx format.
    :param file_name: name of the file that will be saved.
    :return: the function does not return any parameter.
    '''
    nx.write_gexf(G, file_name)
    return



#### FUNCIONS QUE ES DEMANEN EN L'ENUNCIAT DE LA PART 2 DE LA PRACTICA   #####

def retrieve_bidirectional_edges(G, file_name):
    '''
    :param g: A graph with the corresponding networkx format.
    :param file_name: Name of the file that will be saved.
    :return: The reduced graph.
    '''
    # {Keys = node: {Value = attributes of the node} }
    nodes_attrs = {}
    # Bidirectional graph to be returned
    H = nx.Graph()
    '''
    For every neightbor of a node in G, create an edge of H,
    between the node and their neighbor if this neighbor is
    also a predeccessor of the node.
    '''
    for node in G.nodes:
        for neigh in G.neighbors(node):
            if (G.has_edge(neigh, node)):
                '''
                For every new node added to H, save all theirs
                attributes in a dictionary to set them after
                '''
                if node not in H:
                    nodes_attrs[node] = G.node[node]
                if neigh not in H:
                    nodes_attrs[neigh] = G.node[neigh]
                if not (H.has_edge(node, neigh)):
                    H.add_edge(node, neigh)
    
    # Set all the nodes attributes of H
    nx.set_node_attributes(H, nodes_attrs)
    
    # Save and return the graph created
    with open(file_name, 'wb') as f:
        pickle.dump(H, f, pickle.HIGHEST_PROTOCOL)
    return H

def prune_low_degree_nodes(G, min_degree, file_name):
    '''
    :param g: A graph with the corresponding networkx format.
    :param min_degree: lower bound value for the degree
    :param file_name: name of the file that will be saved.
    :return: the pruned graph.
    '''
    # First find the nodes with degree <= min_degree and create a list with them
    nodes_to_remove = []
    for node, grau in G.degree():
        if grau <= min_degree:
            nodes_to_remove.append(node)
    # Remove the nodes finded of the graph G
    for node in nodes_to_remove:
        G.remove_node(node)
    
    # Now find the nodes with degree = 0 and create another list with them
    nodes_to_remove = []
    for node, grau in G.degree():
        if grau == 0:
            nodes_to_remove.append(node)
    # Remove the nodes finded of the graph G
    for node in nodes_to_remove:
        G.remove_node(node)
        
    # Save and return the graph with the nodes removed
    with open(file_name, 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
    return G



#### FUNCIONS QUE ES DEMANEN EN L'ENUNCIAT DE LA PART 3 DE LA PRACTICA   #####

def find_cliques(G, min_size_clique):
    '''
    :param G: A graph with the corresponding networkx format.
    :param min_size_clique: Value of the minimum size of the clique.
    :return: A list with all the cliques finded, and another list with the unique nodes of those cliques.
    '''
    cliques = []
    nodes = set()
    for clique in nx.enumerate_all_cliques(G):
        if len(clique) >= min_size_clique:
            cliques.append(clique)
            for node in clique:
                if node not in nodes:
                    nodes.add(node)
    
    print(f"Nombre de cliques obtinguts amb 'min_size_clique' de {min_size_clique}: {len(cliques)}\n"+
          f"Nombre de nodes diferents: {len(nodes)}\n")
    
    nodes = list(nodes)
    return cliques, nodes

def find_max_k_core(G):
    '''
    :param G: A graph with the corresponding networkx format.
    :return: A subgraph of G.
    '''
    H = nx.k_core(G)
    return H

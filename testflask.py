import pandas as pd
import pickle
import nltk
import re
from nltk.corpus import stopwords
from sklearn import cluster
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_similarity_score
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt
import numpy as np
import itertools


with open("df_mod1.p", 'rb') as picklefile: 
    df_mod1 = pickle.load(picklefile)

with open("nmf_fitrans.p", 'rb') as nmfpickle: 
    nmf_fitrans = pickle.load(nmfpickle)

nmf_recipes = nmf_fitrans.tolist()

def user_choice(user_words):
    match = []
    user_words = user_words[0].split(',')
    for i in range(len(df_mod1)):
        c = 0
        for word in user_words:
            if word in df_mod1['ingredients_list'][i]:
                c += 1
            else:
                pass
        if c == len(user_words):
            match.append(i)
    df_ratings = df_mod1.loc[match,:].sort_values('ratings',ascending = False)
    top_recipes=list(df_ratings['recipe_name'])[:6]      
    images = list(df_ratings['image'])[:6]
    return top_recipes, images

# def user_choice(user_words):
#     match = []
#     user_words = user_words.split()
#     for i in range(len(df_mod1)):
#         c = 0
#         for word in user_words:
#             if word in df_mod1['ingredients_list'][i]:
#                 c += 1
#             else:
#                 pass
#         if c == len(user_words):
#             match.append(i)
#     df_ratings = df_mod1.loc[match,:].sort_values('ratings',ascending = False)
#     top_recipes=list(df_ratings['recipe_name'])[:6]      
#     images = list(df_ratings['image'])[:6]
#     #cuisine = list(df_ratings['cuisine'])[:6]
#     return top_recipes, images
    
#Top recommended recipes based on user selection of recipe

def get_recipe(name):
    recipe_id = []
    match = []
    num = df_mod1[df_mod1['recipe_name'] == name].index.tolist()
    item = nmf_fitrans[num]
    item.reshape(1,-1).shape
    pair_wise = [(cosine_similarity(np.array(item).reshape(1, -1), np.array(j).reshape(1, -1)), index)for index, j in enumerate(nmf_recipes)]
    top_recipes = sorted(pair_wise, reverse = True)[1:10]
    for i in top_recipes:
        recipe_id.append(i[1])
    for i in recipe_id:
        match.append({
            'recipe_name' : df_mod1.loc[i, 'recipe_name'],
            'cuisine' : df_mod1.loc[i, 'cuisine'],
            'image' : df_mod1.loc[i, 'image'][0]
        })    

    return match[:6]

# New cuisine recommender
def new_cuisine(names):
    print names
    recipe_id = []
    match = []
    names = names.split(',')
    name1 = names[0]
    name2 = names[1]
    idx1 = df_mod1[df_mod1['recipe_name'] == name1].index.tolist()
    idx2 = df_mod1[df_mod1['recipe_name'] == name2].index.tolist()
    rcp1 = nmf_fitrans[idx1]
    rcp2 = nmf_fitrans[idx2]
    new_rcp = rcp1 + rcp2
    pair_wise = [(cosine_similarity(new_rcp,np.array(j).reshape(1, -1)),index)for index, j in enumerate(nmf_recipes)]
    top_recipes = sorted(pair_wise, reverse = True)[1:5]
    for i in top_recipes:
        recipe_id.append(i[1])
    for i in recipe_id:
        match.append({
                'recipe_name' : df_mod1.loc[i, 'recipe_name'],
                'cuisine' : df_mod1.loc[i, 'cuisine'],
                'image' : df_mod1.loc[i, 'image'][0]
                })
    print match[:5]
    print len(nmf_recipes)
    print nmf_recipes[0]
    return match[:1]


import flask

# Initialize the app
app = flask.Flask(__name__, static_folder='static',static_url_path='')

#loads the page
@app.route("/")
def viz_page():
    with open("w3test2.html", 'r') as viz_file:
        return viz_file.read()


#listens
@app.route("/gof", methods=["POST"])
def score():
    """
    When A POST request with json data is made to this url,
    Read the grid from the json, update and send it back
    """
    #html "posts" a request and python gets the json  from that request 
    request = flask.request.form
    print(request)
    data = flask.request.json
    print(data)
    a = data
    #print(a['key'])    
    names,images = user_choice(a['key'])
    return flask.jsonify({'names': names, 'images' : images})

@app.route("/recipe", methods=["POST"])
def new():
    data = flask.request.json
    print(data)
    a = data
    names = get_recipe(a['key'])
    print(names)
    return flask.jsonify({'names': names})

# @app.route("/cuisine", methods=["POST"])
# def choice():
#     data = flask.request.json
#     print(data)
#     a = data
#     print (a['key'])
#     names = new_cuisine(a['key'][0])
#     print(names)
#     return flask.jsonify({'names': names})

@app.route("/cuisine", methods=["POST"])
def choice():
    data = flask.request.json
    print("data", data)
    a = data
    print ("key", a['key'])
    names = new_cuisine(a['key'][0])
    print("names",names)
    return flask.jsonify({'names': names})


#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0', port=5003, debug = True)
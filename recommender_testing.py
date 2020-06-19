import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from surprise import Reader, Dataset
from surprise.model_selection import train_test_split
from surprise import SVD, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, KNNBaseline
from surprise import NormalPredictor, BaselineOnly, prediction_algorithms
import games_api_functions

bgg_steam_data = pd.read_csv('bgg_steam_data_normed.csv', index_col=0)

# Exclude expansions
no_expansions = pd.read_csv('csvs/bgg_GameItem.csv')
no_expansions = set(no_expansions.name)
bgg_steam_data = bgg_steam_data[(bgg_steam_data.source=='steam')|\
                                (bgg_steam_data.game.isin(no_expansions))]

## Starting the recommenders
u_i_matrix = bgg_steam_data.pivot_table(index = 'game', columns = 'user', values = 'rating')
u_i_matrix = u_i_matrix.fillna(0)
u_i_matrix
from numpy import count_nonzero
sparsity = (1.0 - count_nonzero(u_i_matrix) / u_i_matrix.size)*100
print(sparsity)

# Time for a recommender
# loading data

reader = Reader(rating_scale=(1,10))
bgg_steam_data.rating_normed.hist()
bgg_steam_data.rating_normed.describe()
bgg_steam_data.dropna(inplace=True)
len(bgg_steam_data)
plt.show()

# data = Dataset.load_from_df(bgg_steam_data[['user', 'game', 'rating_normed']], reader)
#
# trainset, testset = train_test_split(data, test_size=0.25)
# algo = SVD()
# algo.fit(trainset)
# predictions = algo.test(testset)
# algo.test(testset, verbose=True)
# print(accuracy.rmse(predictions))

testgames = just_bgg_data.game.value_counts()
testgames = testgames[testgames < 45]
testgames = testgames[testgames < 20]
testgames = testgames[testgames > 13]
uncommon_games= list(testgames.index)

import random
users_15 = random.sample(list(bgg_steam_data.user.unique()), round((bgg_steam_data.user.nunique()/7)))

bool_is_training = ~((bgg_steam_data.user.isin(users_15))&(bgg_steam_data.source=='bgg'))
bool_is_testing = (~bool_is_training)

                #  | bgg_steam_data.game.isin(uncommon_games)

trainset2 = bgg_steam_data[bool_is_training]
trainset2 = Dataset.load_from_df(trainset2[['user', 'game', 'rating_normed']], reader)
trainset2 = trainset2.build_full_trainset()

testset2 = bgg_steam_data[bool_is_testing]
testset2 = Dataset.load_from_df(testset2[['user', 'game', 'rating_normed']], reader)
testset2 = testset2.build_full_trainset()
testset2 = testset2.build_testset()

known_games = set(bgg_steam_data[bgg_steam_data.source=='bgg'].game)
testset3 = [(user, game, '?') for user in users_15 for game in known_games]

algo = SVD()
algo.fit(trainset2)
predictions = algo.test(testset2, verbose=True)
print(accuracy.rmse(predictions))
print(assess_predictions(predictions, total_games))

predictions = algo.test(testset3)
print(calculate_weighted_coverage(predictions, good_games))

# A dumb baseline -- guess 5
testvals = [c for (a,b,c) in testset2]
dumb_RMSE = (sum([(val-5.5)**2 for val in testvals])/len(testvals))**.5

total_games = len(set(bgg_steam_data.game[bgg_steam_data.source == 'bgg']))

# Completely random baseline
import random
true_vals = [c for (a,b,c) in testset2]
est_vals = [random.uniform(1,10) for item in testset2]
predictions=  [(a, b, c, est_value,'details') for ((a, b, c), est_value) in list(zip(testset2, est_vals))]
assess_predictions(predictions, total_games)

est_vals = [random.uniform(1,10) for item in testset3]
predictions=  [(a, b, c, est_value,'details') for ((a, b, c), est_value) in list(zip(testset3, est_vals))]
print(calculate_coverage(predictions, total_games))
print(calculate_weighted_coverage(predictions, good_games))

print("Just guessing 5 gives you RMSE of %s"%dumb_RMSE+", not much better...")

sim_options = {'name': 'cosine',
               'user_based': False  # compute  similarities between items
               }
algo = KNNBasic(sim_options=sim_options)
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))
assess_predictions(predictions, total_games)

predictions = algo.test(testset3)
print(calculate_weighted_coverage(predictions, good_games))
0.17757009345794392 * len(good_games)

mean_ratings = bgg_steam_data[bgg_steam_data.source=='bgg'].groupby('game').mean().rating_normed
mean_ratings = mean_ratings[mean_ratings>5.5]
good_games = set(mean_ratings.index)
total_good_games = len(good_games)

sim_options = {'name': 'cosine',
               'user_based': True,
               'max_k': 50# compute  similarities between items
               }

algo = KNNBasic(sim_options=sim_options)
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))
assess_predictions(predictions, total_games)


predictions = algo.test(testset3)
print(calculate_coverage(predictions, total_games))
print(calculate_weighted_coverage(predictions, good_games))

algo = BaselineOnly()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))
assess_predictions(predictions, total_games)

predictions = algo.test(testset3)
print(calculate_coverage(predictions, total_games))
print(calculate_weighted_coverage(predictions, good_games))

sim_options = {'name': 'cosine',
               'user_based': True  # compute  similarities between items
               }
algo = KNNBaseline(sim_options=sim_options)
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

predictions = algo.test(testset3)
print(calculate_coverage(predictions, total_games))
print(calculate_weighted_coverage(predictions, good_games))


sim_options = {'name': 'cosine',
               'user_based': False  # compute  similarities between items
               }

algo = KNNBaseline(sim_options=sim_options)
algo.fit(trainset2)
algo.get_neighbors()
help(trainset2)
trainset2.to_inner_iid('Catan')

predictions = algo.test(testset2)
print(accuracy.rmse(predictions))
print(assess_predictions(predictions, total_games))

predictions = algo.test(testset3)
print(calculate_weighted_coverage(predictions, good_games))

    sim_options = {'name': 'cosine',
                   'user_based': True  # compute  similarities between items
                   }
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset2)
    predictions = algo.test(testset2)
    print(assess_predictions(predictions, total_games))

    predictions = algo.test(testset3)
    print(calculate_weighted_coverage(predictions, good_games))
    0.038232795242141036 * len(good_games)

print(calculate_coverage(predictions, total_games))
print(calculate_weighted_coverage(predictions, good_games))

.02998 * total_games
algo = KNNWithZScore()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = KNNWithMeans()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = NormalPredictor()
algo.fit(trainset2)
predictions = algo.test(testset2)
assess_predictions(predictions, total_games)

predictions = algo.test(testset3)
calculate_coverage(predictions, total_games)
calculate_weighted_coverage(predictions, good_games)

predictions = algo.test(testset2)
precisions, recalls = precision_recall_at_k(predictions, k=10, threshold=6)
precisions

    # Precision and recall can then be averaged over all users
print(sum(prec for prec in precisions.values()) / len(precisions))
print(sum(rec for rec in recalls.values()) / len(recalls))

def assess_predictions(predictions, total_games):
    rmse = accuracy.rmse(predictions)
    coverage = calculate_coverage(predictions, total_games)
    precisions, recalls = precision_recall_at_k(predictions, k=10, threshold=6)
    print('coverage is ' + str(coverage))
    print('MAP@10 is ' + str(sum(prec for prec in precisions.values()) / len(precisions)))
    print('RMSE is ' + str(rmse))

from collections import defaultdict

from surprise import Dataset
from surprise import SVD
from surprise.model_selection import KFold

precision_recall_at_k()
def precision_recall_at_k(predictions, k=10, threshold=5.5):
    '''Return precision and recall at k metrics for each user.'''

    # First map the predictions to each user.
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():

        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

        # Number of recommended items in top k
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])

        # Precision@K: Proportion of recommended items that are relevant
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 1

        # Recall@K: Proportion of relevant items that are recommended
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 1

    return precisions, recalls

from collections import defaultdict

def read_item_names():
    """Read the u.item file from MovieLens 100-k dataset and return two
    mappings to convert raw ids into movie names and movie names into raw ids.
    """

    file_name = get_dataset_dir() + '/ml-100k/ml-100k/u.item'
    rid_to_name = {}
    name_to_rid = {}
    with io.open(file_name, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            line = line.split('|')
            rid_to_name[line[0]] = line[1]
            name_to_rid[line[1]] = line[0]

    return rid_to_name, name_to_rid

def calculate_coverage(predictions, total_games, k=10):
    user_est_true = defaultdict(list)
    top_k_games = []
    for uid, iid, _, est, _ in predictions:
        user_est_true[uid].append((est, iid))
    for uid, user_ratings in user_est_true.items():
        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        # Number of recommended items in top k
        top_k_games += [game for (_, game) in user_ratings[0:k]]
    return len(set(top_k_games))/total_games

def calculate_weighted_coverage(predictions, good_games, k=10):
    user_est_true = defaultdict(list)
    top_k_games = []
    for uid, iid, _, est, _ in predictions:
        user_est_true[uid].append((est, iid))
    for uid, user_ratings in user_est_true.items():
        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        # Number of recommended items in top k
        top_k_games += [game for (_, game) in user_ratings[0:k]]
    okay_games = set(good_games).intersection(set(top_k_games))
    return len(okay_games) / len(good_games)

    precisions = dict()
    recalls = dict()

        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)


        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])

        # Precision@K: Proportion of recommended items that are relevant
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 1

        # Recall@K: Proportion of relevant items that are recommended
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 1

    return precisions, recalls
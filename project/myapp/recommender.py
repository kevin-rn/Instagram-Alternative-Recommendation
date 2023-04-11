"""Import necessary modules for creating the recommender"""
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from sentence_transformers import SentenceTransformer, util


# Datasets Importing
# post_data consists of post details like post_id, title, category
# user_data consists of user's information
# view_data consists of which user view which post

def preprocessing_data(post_df, view_df):
    """Preprocess data to be correct format"""
    dataframe = pd.DataFrame(view_df)
    if "Valuable" not in dataframe.columns:
        dataframe["Valuable"] = np.random.randint(1, 6, len(dataframe))
    df_merge = pd.merge(dataframe, post_df, on='post_id')
    data = df_merge.drop(['time_stamp', 'category'], axis=1)
    # data.tail()
    # print(df_merge.head())
    combine_post_rating = data.dropna(axis=0, subset=['title'])
    post_rating_count = (combine_post_rating.groupby(
        by=['title'])['Valuable'].count().reset_index().rename(
        columns={'Valuable': 'totalValuableCount'})[['title', 'totalValuableCount']]
    )
    # post_ratingCount.to_csv('post_ratingCount.csv', index=True)
    # print(post_ratingCount.head())
    rating_with_total_valuable_count = combine_post_rating.merge(
        post_rating_count, left_on='title', right_on='title', how='left'
    )
    # rating_with_total_valuable_count.to_csv('rating_with_total_valuable_count.csv', index=True)
    pd.set_option('display.float_format', lambda x: f"{x:.3f}")
    # print(post_ratingCount['totalValuableCount'].describe())
    # print(post_ratingCount['totalValuableCount'].quantile(np.arange(.9, 1, .01)))
    popularity_threshold = 13
    rating_popular_post = rating_with_total_valuable_count.query(
        'totalValuableCount >= @popularity_threshold')  #
    # rating_popular_post.tail()
    # user_data.head()
    # len(user_data.city.unique())
    # rating_popular_post.to_csv('rating_popular_post.csv', index=True)
    rating_popular_post = rating_popular_post.drop_duplicates(['user_id', 'title'])  # 删除重复组合
    # rating_popular_post.to_csv('rating_popular_post.csv', index=True)
    rating_post_pivot = rating_popular_post.pivot(index='title', columns='user_id',
                                                  values='Valuable').fillna(0)
    # rating_popular_post_pivot.to_csv('rating_popular_post_pivot.csv', index=True)
    rating_post_matrix = csr_matrix(rating_post_pivot.values)
    return rating_post_matrix, rating_post_pivot


def collaborative_filter(rating_post_matrix, rating_post_pivot,
                         n_neighbors, query_idx):
    """Collaborative filtering"""
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(rating_post_matrix)
    dist, idx = model_knn.kneighbors(
        rating_post_pivot.iloc[query_idx, :].values.reshape(1, -1),
        n_neighbors)
    dictionary = {}
    for i in range(1, len(dist.flatten())):
        rate_2 = rating_post_pivot.index[idx.flatten()[i]]
        dictionary[rate_2] = 1 - dist.flatten()[i]
    return dist, idx, dictionary


def content_based(rating_post_pivot, dist, idx, query_idx):
    """content-based filtering"""
    hybrid_score = {}
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    for i in range(0, len(dist.flatten())):
        if i == 0:
            continue
        rate_1 = rating_post_pivot.index[query_idx]
        rate_2 = rating_post_pivot.index[idx.flatten()[i]]
        query_embedding = model.encode(rate_1)
        passage_embedding = model.encode(rate_2)
        score = util.cos_sim(query_embedding, passage_embedding)
        hybrid_score[rate_2] = score.item()
    return hybrid_score


def mrr(query_value, final_items, post_df):
    """Calculate MRR score"""
    selected_row = post_df.loc[post_df['title'] == query_value]
    row_type = selected_row['category'].values[0]
    # print(query_value, 'category:', row_type)
    mrr_score = 0
    for i, (key, value) in enumerate(final_items):
        tmp_row = post_df.loc[post_df['title'] == key]
        # print(i, key, value, tmp_row['category'].values[0])
        if row_type == tmp_row['category'].values[0]:
            mrr_score += (1 / (i + 1))
    mrr_score /= 10
    # print(mrr_score)
    return mrr_score


def hybrid_recommendation(rating_post_matrix, rating_post_pivot, adjustment=0.5, neighbours=20):
    """calculates hybrid recommendation score with an adjustment to the score available"""
    query_idx = np.random.choice(rating_post_pivot.shape[0])

    dist, idx, collab_score = collaborative_filter(rating_post_matrix, rating_post_pivot,
                                                   neighbours, query_idx)
    cont_score = content_based(rating_post_pivot, dist, idx, query_idx)

    results_dict = {}
    for key, _ in collab_score.items():
        results_dict[key] = adjustment * cont_score[key] + (1 - adjustment) * collab_score[key]

    sorted_hybrid = dict(sorted(results_dict.items(), key=lambda item: item[1], reverse=True))
    final_hybrid = list(sorted_hybrid.items())[:10]
    return final_hybrid


if __name__ == '__main__':  # pragma: no cover
    user_data = pd.read_csv(r'../static/dataset_hybrid/user_data.csv')
    post_data = pd.read_csv(r'dataset_hybrid\postdata_new.csv')
    view_data = pd.read_csv(r'../static/dataset_hybrid/view_data.csv')
    rating_popular_post_matrix, rating_popular_post_pivot = preprocessing_data(post_data, view_data)
    query_index = np.random.choice(rating_popular_post_pivot.shape[0])
    # query_index = 21
    query = rating_popular_post_pivot.index[query_index]
    distances, indices, collaborative_score = collaborative_filter(
        rating_popular_post_matrix, rating_popular_post_pivot, 20, query_index)
    # rating_popular_post_pivot.index[query_index]
    # content based algorithm
    content_score = content_based(rating_popular_post_pivot, distances, indices, query_index)
    hybrid_dict = {}
    for k, v in collaborative_score.items():
        hybrid_dict[k] = 1 * content_score[k] + 1 * collaborative_score[k]
    sorted_hybrid_dict = dict(sorted(hybrid_dict.items(),
                                     key=lambda item: item[1],
                                     reverse=True))
    final_hybrid_items = list(sorted_hybrid_dict.items())[:10]

    sorted_content_dict = dict(sorted(content_score.items(),
                                      key=lambda item: item[1],
                                      reverse=True))
    final_content_items = list(sorted_content_dict.items())[:10]

    sorted_collaborative_dict = dict(sorted(collaborative_score.items(),
                                            key=lambda item: item[1],
                                            reverse=True))
    final_collaborative_items = list(sorted_collaborative_dict.items())[:10]
    print("Recommendations:")
    for k, v in final_hybrid_items:
        print(k, "score", v)
    # mrr(query, final_content_items, post_data)

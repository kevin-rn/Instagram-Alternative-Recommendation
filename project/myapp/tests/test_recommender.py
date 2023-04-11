import pandas as pd
import numpy as np
import unittest
from myapp.recommender import preprocessing_data, collaborative_filter, content_based, hybrid_recommendation, mrr


class TestRecommendation(unittest.TestCase):

    def setUp(self):
        """setup before each test"""
        self.post_matrix = np.array([[1, 0, 1],
                                     [0, 1, 1],
                                     [1, 1, 0]])

    def test_preprocessing_data(self):
        """test the preprocessing_data function"""
        post_data = pd.DataFrame({
            'post_id': [1, 2, 3],
            'title': ['post1', 'post2', 'post3'],
            'category': ['cat1', 'cat1', 'cat2']
        })
        view_data = pd.DataFrame({
            'user_id': [1, 1, 2],
            'post_id': [1, 2, 2],
            'time_stamp': ['2022-01-01', '2022-01-02', '2022-01-03']
        })
        rating_popular_post_matrix, rating_popular_post_pivot = preprocessing_data(post_data, view_data)
        self.assertEqual(list(rating_popular_post_pivot.columns), [])

    def test_collaborative_filter(self):
        """test the collaborative_filter function"""
        rating_popular_post_pivot = pd.DataFrame(self.post_matrix, columns=[1, 2, 3],
                                                 index=['post1', 'post2', 'post3'])
        distances, indices, collaborative_score = collaborative_filter(self.post_matrix,
                                                                       rating_popular_post_pivot, 2, 0)
        collaborative_score = {k: round(v, 2) for k, v in collaborative_score.items()}
        self.assertEqual(collaborative_score, {'post2': 0.50})
        distances, indices, collaborative_score = collaborative_filter(self.post_matrix,
                                                                       rating_popular_post_pivot, 2, 1)
        collaborative_score = {k: round(v, 2) for k, v in collaborative_score.items()}
        self.assertEqual(collaborative_score, {'post1': 0.50})

    def test_content_based(self):
        """test the content_based function"""
        rating_popular_post_pivot = pd.DataFrame(self.post_matrix, columns=[1, 2, 3],
                                                 index=['post1', 'post2', 'post3'])
        score = content_based(rating_popular_post_pivot, np.array([[0.0, 0.5, 0.0]]), np.array([[0, 1, 2]]), 1)
        score = {k: round(v, 2) for k, v in score.items()}
        self.assertEqual(score, {'post3': 0.69, 'post2': 1.00})

    def test_hybrid_recommendation(self):
        """test hybrid function"""
        rating_popular_post_pivot = pd.DataFrame(self.post_matrix, columns=[1, 2, 3],
                                                 index=['post1', 'post2', 'post3'])
        final_hybrid = hybrid_recommendation(self.post_matrix, rating_popular_post_pivot, 0.5, 2)
        self.assertIsInstance(final_hybrid, list)
        self.assertEqual(len(final_hybrid), 1)

        # Check if each item is a tuple with two elements
        for item in final_hybrid:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)

        # Check if recommendation score is sorted
        scores = [score for _, score in final_hybrid]
        self.assertEqual(scores, sorted(scores, reverse=True))

        # Check if the items are valid post titles
        self.assertListEqual([title for title, _ in final_hybrid], ['post2'])

        # Check if the recommendation score is between 0 and 1 for each item
        for _, score in final_hybrid:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)

    def test_MRR(self):
        """test the MRR function"""
        post_data = pd.DataFrame({
            'post_id': [1, 2, 3],
            'title': ['post1', 'post2', 'post3'],
            'category': ['cat1', 'cat1', 'cat2']
        })
        query = 'post1'
        final_items = [('post2', 0.5), ('post3', 0.3)]
        expected_mrr = 0.1
        actual_mrr = mrr(query, final_items, post_data)
        self.assertAlmostEqual(actual_mrr, expected_mrr, places=2)

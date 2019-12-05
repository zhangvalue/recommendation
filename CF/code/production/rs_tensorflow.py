# *===================================*
# -*- coding: utf-8 -*-
# * Time : 2019-12-05 19:47
# * Author : zhangsf
# *===================================*
import pandas as pd
import numpy as np
import tensorflow as tf

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'  # 这是默认的显示等级，显示所有信息  
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'  # 只显示 warning 和 Error   
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3'  # 只显示 Error
dataset_dir = '../../data/'
ratings_df = pd.read_csv(dataset_dir + 'ratings.csv')

print(ratings_df.head())
movies_df = pd.read_csv(dataset_dir + 'movies.csv')
print(movies_df.shape)
print(movies_df.head())
## select the features from movies_df
movies_df = movies_df[['movieId', 'title']]
movies_df.to_csv(dataset_dir + 'movies_processed.cvs', index=False, header=True, encoding='utf-8')
print(movies_df.head())
ratings_df = pd.merge(ratings_df, movies_df, on='movieId')
print(ratings_df.head())
ratings_df = ratings_df[['userId', 'movieId', 'rating']]
ratings_df.to_csv(dataset_dir + 'ratings_processed.csv', index=False, header=True, encoding='utf-8')
print(ratings_df.head())
## 创建电影评分矩阵rating和评分记录矩阵record
userNo = ratings_df['userId'].max() + 1
movieNo = ratings_df['movieId'].max() + 1
print(userNo)
print(movieNo)

ratings = np.zeros((movieNo, userNo))
flag = 0
ratings_df_length = np.shape(ratings_df)[0]
for index, row in ratings_df.iterrows():
    ratings[int(row['movieId']), int(row['userId'])] = row['rating']
    flag += 1
    print('processed %d, %d left' % (flag, ratings_df_length - flag))
ratings.shape
record = ratings > 0
record
# change the boolean value to 0 or 1
record = np.array(record, dtype=int)
record


## Build the model
def normalizeRatings(rating, record):
    m, n = rating.shape
    rating_mean = np.zeros((m, 1))
    rating_norm = np.zeros((m, n))
    for i in range(m):
        idx = record[i, :] != 0
        rating_mean[i] = np.mean(rating[i, idx])
        rating_norm[i, idx] -= rating_mean[i]
    return rating_norm, rating_mean


rating_norm, rating_mean = normalizeRatings(ratings, record)
# Some movies are scored by nobody, change the nan value to num
rating_norm = np.nan_to_num(rating_norm)
rating_norm
rating_mean = np.nan_to_num(rating_mean)
rating_mean
num_features = 10
x_parameters = tf.Variable(tf.random_normal([movieNo, num_features], stddev=0.35))
theta_parameters = tf.Variable(tf.random_normal([userNo, num_features], stddev=0.35))
loss = 1 / 2 * tf.reduce_sum(
    ((tf.matmul(x_parameters, theta_parameters, transpose_b=True) - rating_norm) * record) ** 2) + \
       1 / 2 * (tf.reduce_sum(x_parameters ** 2) + tf.reduce_sum(theta_parameters ** 2))  # lambda1 = lambda2 = 1
optimizer = tf.train.AdamOptimizer(1e-4)
train = optimizer.minimize(loss)
## Train the model
tf.summary.scalar('loss', loss)
summaryMerged = tf.summary.merge_all()
filename = '../../log/movie_tensorboard'
writer = tf.summary.FileWriter(filename)
sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)
for i in range(5000):
    _, movie_summary = sess.run([train, summaryMerged])
    writer.add_summary(movie_summary, i)
    if i % 200 == 0:
        print("episode: " + i)
## Evaluate the model
current_x_parameters, current_theta_parameters = sess.run([x_parameters, theta_parameters])
predicts = np.dot(current_x_parameters, current_theta_parameters.T) + rating_mean
errors = np.sqrt(np.sum((predicts - ratings) ** 2))
print(errors)
## Build the whole recommendation system
user_id = input('您要向哪位用户进行推荐？请输入用户编号： ')
sorted_result = predicts[:, int(user_id)].argsort()[::-1]
idx = 0
print('为该用户推荐的评分最高的20部电影是： '.center(80, '='))
for i in sorted_result:
    if i and i < movies_df.shape[0]:
        print('评分： %.2f, 电影名：%s' % (predicts[i, int(user_id)], movies_df.iloc[i]['title']))
        idx += 1
    if idx == 20: idx = 0;break

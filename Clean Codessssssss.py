#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


column_names = ['user_id', 'item_id', 'rating', 'timestamp']
df = pd.read_csv('u.data', sep='\t', names=column_names)
movie_titles = pd.read_csv("Movie_Id_Titles")
movie_titles.head()


# In[3]:


df = pd.merge(df,movie_titles,on='item_id')
df.head()


# In[4]:


# Remove year:
df['year'] = df.title.str.extract("\((\d{4})\)", expand=True)
df.year = pd.to_datetime(df.year, format='%Y')
df.year = df.year.dt.year 
df.title = df.title.str[:-7]


# In[7]:


# Clean titles:
banned = ['The']
f = lambda x: ' '.join([item for item in x.split() if item not in banned])
df["title"] = df["title"].apply(f)


# In[8]:


df['title'] = df['title'].replace(',','', regex=True)
df['title']


# In[10]:


df.groupby('title')['rating'].mean().sort_values(ascending=False).head()
df.groupby('title')['rating'].count().sort_values(ascending=False).head()
ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
ratings['num of ratings'] = pd.DataFrame(df.groupby('title')['rating'].count())
ratings.head()


# In[11]:


moviemat = df.pivot_table(index='user_id',columns='title',values='rating')
moviemat.head()


# In[12]:


# Dash App:
from jupyter_dash import JupyterDash
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update


# In[13]:


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
   html.H1(children="Recommender System", style={'textAlign': 'center'}),
   dcc.Markdown('''
               ###### Step 1: Visit my movie dashboard, and hover over the data points.
               ###### Step 2: Pick a title of a movie you enjoyed.
               ###### Step 3: Enter the movie name, and wait for recommendations to appear!
   ''',style={'textAlign': 'center'}),
   
   dcc.Input(id='username',type='text'),
   html.Button(id='submit-button', type='submit', children='Submit'),
   html.Div(id='output_div')
   ],style={'textAlign': 'center','justify':'center','align':'middle','verticalAlign':'middle'})

@app.callback(Output('output_div', 'children'),
               [Input('submit-button', 'n_clicks')],
               [State('username', 'value')],
               )

def update_output(clicks, input_value):
   if clicks is not None:
       if input_value is not None and input_value!='':
           count = 0
           for i in df['title']:
               if i==input_value:
                   count+=1
           if(count==0):
               return('Sorry, no movie recommendations available :(. Please enter another movie name!')
           else:
               movie = input_value
               movie_user_ratings = moviemat[movie]
               similar_to_movie = moviemat.corrwith(movie_user_ratings)
               corr_movie = pd.DataFrame(similar_to_movie,columns=['Correlation'])
               corr_movie.dropna(inplace=True)
               corr_movie = corr_movie.join(ratings['num of ratings'])
               a = corr_movie[corr_movie['num of ratings']>100].sort_values('Correlation',ascending=False).head()
               return ('If you enjoyed '+movie+', you would also enjoy '+a.reset_index()["title"][1]+', '+a.reset_index()["title"][2]+', and '+a.reset_index()["title"][3]+'!')
           return ('Please enter valid input')
       
app.run_server(mode='external',port = 8061)


# In[ ]:





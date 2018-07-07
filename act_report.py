
# coding: utf-8

# # Project: "We Rate Dogs" Twitter Data Wrangling

# ## Analysis and Visualization
# 
# This section of the project focuses on coming up with visuals and insights about the data that was wrangled and cleaned in the previous section. 

# In[17]:


#Import requried packages
import pandas as pd


# In[18]:


#Reload the clean dataframe
df = pd.read_csv('twitter_archive_master.csv')


# In[19]:


df.head()


# In[20]:


#Remove the first column that was imported 
df.drop(['Unnamed: 0'], axis =1, inplace = True)


# In[21]:


df.head()


# ### Insights
# 
# There are a few possible insights to be drawn from this data. Here are a couple I chose to investigate: 
# 
# 1. Is there a breed that received more likes than other breeds? How many likes on average does each breed receive?
# 2. Which classification resulted in the highest ratings? (This may be challenging, since the dog classification wasn't always provided). 
# 3. Is there a time of day (morning, noon, or afternoon) that people tweet the most about their dogs? 
# 
# Visualization: 
# - I would like to provide a word cloud of different parts of the extracted tweet texts in the shape of a dog to illustrate how excited people are about their dogs!

# #### Insight #1: Is there a breed of dogs that received more likes than other breeds? 
# 
# To answer this question I will look at comparing the likes for each of the breeds. To do this, I will need to group by breed, and then summarize the variables 'likes'.  
# 
# 

# In[22]:


# Group by breed, then summarize the variables 

breed_likes = df.groupby(['predicted_breed'])['likes'].mean()



# In[23]:


#Summarize the likes into a table or graph showing the most popular breeds
breed_likes.describe()


# In[24]:


#Convert to dataframe to get the breed associated with each number of likes

df_breed_likes = breed_likes.to_frame(name = 'likes')
df_breed_likes.head()


# In[25]:


# Drop all zero values: 
df_breed_likes = df_breed_likes[(df_breed_likes != 0).all(1)]


# In[26]:


#Add an index: 
df_breed_likes.reset_index(level=0, inplace=True)
df_breed_likes.head()


# In[27]:


df_breed_likes.info()


# In[28]:


df_breed_likes.likes.describe()


# In[31]:


#summarize with a graph showing the breeds with the greatest number of likes: 
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
df_breed_likes.plot.bar(x = 'predicted_breed', y = 'likes')
labels = df_breed_likes.predicted_breed

plt.title('Distribution of Number of Likes')
plt.xlabel('Dog Breed')


# Looking at the above graph it is not clear (due to the number of breeds) which are most liked. Obviously, there are too many breeds shown on this graph. There are 143 total breeds in this data set. To get a better understanding of which breeds are most popular on the twitter site "We rate dogs", it makes more sense to take the top 40, for example, and look at the which breeds those are. 
# Also interesting is that the number of likes falls mostly below 10,000 (75%). There are less than 25% of the breeds in this subset of data that are greater than that, with the max at 46,549. It'll be interesting to see which breeds got the highest likes. 
# Below please find the subset of the 20 highest liked breeds, as well as the summary of the number of likes for the most popular breeds. 

# In[32]:


#find the greatest 20 likes in the dataframe df_breed_likes
df_breed_likes_largest = df_breed_likes.nlargest(40, 'likes')


# In[33]:


df_breed_likes_largest.describe()


# In[34]:


df_breed_likes_largest.plot.bar(x = 'predicted_breed')
x_labels = df_breed_likes.predicted_breed
labels = x_labels

plt.title('Distribution of Number of Likes')
plt.xlabel('Dog Breed')


# It looks like, from this plot, there were actually no dog breeds that had over 40,000 likes. Angora is a cat breed. Also, the machine learning model that was used to pull some of these dog breeds based on a picture didn't get all the top liked tweets correct. Starting with the first actual dog breed, it looks like the most liked breed is the Saluki, followed by breeds like flat-coated retriever, standard poodle and the norweigen elkhound. Of course, there may actually be a few breeds that received greater than 20,000 likes, and the machine learning algorithm just didn't identify the breed correctly. 
# Despite not knowing exactly which breeds received the most likes, we can say that the average number of likes for the breeds in this dataset is 7,297 and 75% of the breeds (correctly or incorrectly identified) received 17,900 likes or less. 
# Optimally, at this stage, a reassessment would be performed on the dog breed dataset and the data would be cleaned to remove all incorrect dog breeds. This was not one of the 8 quality attributes chosen to fix, but had it been, we would have a clearer understanding of which breeds are most popular. 

# ### Insight #2: Which classification resulted in the highest rating? 
# 
# The next area I'll explore is determining which classifications resulted in the highest ratings given by the dog owner. The classifications that I'm referring to are doggo (big pupper, usually older), floofer (dogs with excess fur), pupper (small dogs, usually younger), and puppo (transitional phase between pupper and doggo). This was a limited data set to begin with. That is, although there are 1994 tweet id's, most of the tweet id's did not provide this classification.  
# 
# The "Final float ratings" is a converted rating given to the dog by the person tweeting. These numbers started as fraction and were extracted from the tweet text. For example, a rating of value of 1.2 is actually a rating of 12/10. That is, their dog is of course so great that the numerator exceeds the denominator. 

# In[35]:


#Group by category to determine the average rating per classification
classification_ratings = df.groupby
classification_ratings = df.groupby(['classification'])['final_float_ratings'].mean()


# In[36]:


classification_ratings.head()


# It looks like the order of ranking for scores is: 
# 
# 1) Floofer and puppo tied at 1.2
# 
# 2) Doggo at 1.178
# 
# 3) Pupper at 1.066
# 
# Whether or not these ranking are significant, they do seem to make some sense. That is, puppies ("pupper") are a lot of work, requiring extra attention and training. Floofers are fluffy, one of the main draws of having a pet, and puppo is the stage beyond the high attention needs of a pupper but still plenty of energy to play. 
# And of course, it makes sense that people would rank their Doggo higher than a new puppy, especially if the owner has had the dog for a long time. 
# 

# ### Insight #3: Is there a time of day that people tweet the most about their dogs? 

# Just out of curiosity, it would be interesting to find out when people are most active on twitter when tweeting about their dogs. Before the analysis occurs, I'm going to guess afternoon or evening, since that's when most people are leisurely spending time with their dogs. 
# What this will entail is adding a column to the dataframe (morning, afternoon, evening, or night). The way I will classify the times are as follows: 
# 
# 6am - 12am : Morning (hour 6 - 12)
# 
# 12pm - 5 pm: Afternoon (hour 12 - 17)
# 
# 5pm - 9 pm: Evening (hour 17-21)
# 
# 9 pm - 6 am: Night (hour 21-24, 0-6)

# In[37]:


#Convert the datetime into a datetime object: 
df['timestamp'] = pd.to_datetime(df.timestamp)
df.info()


# In[38]:


df.head()


# In[39]:


#Extract the hour from each timestamp for further classification into bins: 
for index, row in df.iterrows():
    time = row[4]
    df.loc[index, "extracted_hour"] = time.hour
    


# In[40]:


df.head()


# In[41]:


#Divide up the hour according to bins outlined in the description above: 

# Bin edges that will be used to "cut" the data into groups
bin_edges = [-0.1, 6.0, 12.0, 17.0, 21.0, 24.1] 

#Step 3:
# Labels for the five time of day groups
bin_names = [ 'early morning', 'morning' , 'afternoon','evening', 'night' ] # Name each acidity level category

#Step 4:
# Creates part of day column
df['part_of_day'] = pd.cut(df['extracted_hour'], bin_edges, labels=bin_names)


#Step 5:
# Find the count for the number of tweets for each time of day category.
df.groupby('part_of_day').count()




# I wasn't surprised by this information. The time shown above is UTC time, which is 4 hours ahead of EST. So the bins are actually as follows: 
# For the purpose of this analysis, we'll assume EST, although tweets are most likely from other parts of the country and world on different time zones. Most of the US is either on EST or central (which is only 1 hour from EST). 
# 
# Early morning (0 -6 am UTC) : (4am - 10 am EST)
# 
# Morning (6 - 12 am UTC): (10am - 4 pm EST)
# 
# Afternoon (12 pm - 5 pm UTC): (4 pm - 9 pm EST)
# 
# Evening (5 pm - 9 pm UTC): (9 pm - 1 am EST) 
# 
# Night (9 pm - 12 midnight) : (1 am - 4 am EST)
# 
# Most tweets occurred between the hours of 4 am and 10 am EST, which makes sense, since dogs need to be walked in the morning, and that's when most people are out with their dogs. What I found interesting is that no tweets in this dataset are between 10 am and 4 pm. Although most people are working between those hours, I found it surprising that 0 tweets occurred during that time (in this dataset). 
# 
# Also not surprising is that the next most popular time was between the hours of 4 and 9 pm (dogs also need their second walk of the day), followed by 9 p -1 am , and then 1 am until 4 am. 
# To be sure my classification was correct, I double checked the values of the values of the extracted hour in the code block below. 

# In[42]:


df['extracted_hour'].unique()


# #### Visual: Word cloud of texts and descriptions about the dogs
# 
# Each tweet id in this dataframe has texts associated with the tweet. These words are typically words used to describe their dogs, as well as might they might be doing in the picture. 
# 
# A word cloud is a great way to represent a summary of the tweets about how people feel about their dogs, and why they tweet about them (or at least the people in this dataset). 
# 
# 

# In[43]:


#Download packages required for wordcloud: 
from PIL import Image
from wordcloud import WordCloud, STOPWORDS


# In[47]:


#Generate the word cloud image
wordcloud = WordCloud().generate(''.join(df['text']))
# Generate plot
plt.imshow(wordcloud)
plt.axis("off")
plt.title("Twitter - We Rate Dogs")
plt.show()




# #### Final Conclusions/Statements: 
# 
# Not surprisingly, people love their dogs, and they love to tweet about them. Through this analysis exercise, I found that people tweet about their dogs the most when they are with them. The words in the word cloud above show the most common words people associate with their dogs. The most common word, https, was left in there. I thought it made sense to leave this word in, since this project is all about what people are posting about their dogs on twitter. Other words that pop out are happy, good, pup, pupper, tongue. etc. 
# Overall, the message to be taken from this exercise is that dogs are people's best friends, and people love to share information about them with others. 


# coding: utf-8

# # Project: "We Rate Dogs" Twitter Data Wrangling

# ## Step 1: Gather Data

# In[1]:


#Import Required Packages
import pandas as pd
import numpy as np
import requests
import os
import json


# In[171]:


#Read twitter_archive_enhanced csv into a dataframe
df_archive = pd.read_csv('twitter-archive-enhanced.csv')
df_archive.head()


# In[172]:


#Load image_predictions.tsv from https:
import urllib.request
image_prediction, headers = urllib.request.urlretrieve('https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv')
html = open(image_prediction)

df_image = pd.read_csv(html, sep = '\t')
df_image.head()
id_list = df_archive['tweet_id']



# In[ ]:


#Query twitter data
#(retweet count and favorite count)
### keys were removed so code will not run

import tweepy
consumer_key = 'xxxxxxx'
consumer_secret = 'xxxxxx'
access_token = 'xxxxxx'
access_secret = 'xxxxxxx'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

id_list = df_archive['tweet_id']
#id_list = [892420643555336193, 892177421306343426, 891815181378084864, 891689557279858688, 891327558926688256,
 #          891087950875897856]
data = {}

count = 0
for id in id_list: 
    try: 
        tweet = api.get_status(id, tweet_mode='extended')
        retweet_count = (tweet.retweet_count)
        likes = (tweet.favorite_count)
        data[count] = {'id': str(id), 'retweet_count': retweet_count, 'likes': likes}
        count += 1
    except: 
        pass

with open('tweet_json.txt', 'w') as outfile:
    json.dump(data, outfile)
outfile.close()

pd_likes = pd.read_json('tweet_json.txt', orient='index', convert_axes=False)
outfile.close()

pd_likes.to_csv('twitter_likes.csv')


# In[173]:


#Read the twitter file back in to perform assessments

df_likes = pd.read_csv('twitter_likes.csv')
df_likes.head()


# #### At this point I have gathered three tables of information: 
# 1) df_archive (an archived list of tweets with score
# 
# 2) df_image (image predictions)
# 
# 3) df_likes (information gathered from Twitter)
# 
# Now I will proceed to the step of going through each data set and assessing for issues of Quality and Tidiness
# 

# ## Step 2:  Assess Data

# In[174]:


#Programmatic Assessment of df_archive

#checking to see how many unique "source" values in df_archive: 
df_archive.source.value_counts()

#Describing the dataset:
df_archive.info()

df_archive.name.describe()
df_archive.head()






# In[175]:


#Assessment of the names of dogs
df_archive.name.describe()


# In[176]:


#Assessment of the rating_numerator:
df_archive.rating_numerator.unique()



# In[177]:


#Assessment of the rating_denominator: 
df_archive.rating_denominator.unique()


# In[178]:


#Programmatic Assessment of df_image
df_image.info()
df_image.describe()
df_image.head()


# As I performed the assessments on the three datasets mentioned above I documented the issues as either quality or tidiness issues. I performed both a visual and programmatic assessment. Here is the summary of the issues found. 
# 
# Quality:  
# 
# 1) In df_archive there are retweets. The rows containing retweets needs to be removed.  
# 
# 2) The names of the dogs are not correct for some of the tweets. These need to be corrected. Some of the names are "a", "None", "the". 
# 
# 3) The ratings of some of the tweets (numerator and denominator) are not correct. These need to be corrected. I performed a visual assessment of the csv file and was able to see that there was a value of 5/10 (numerator/denominator). Looking at this value in particular it was appearant that the value was actually 9.5/10, and the numerator only pulled the 5. Also, in one case there were two ratings given, when the user actually intended to give the second rating. All provided ratings should be provided in this case and further investigated. 
# 
# 4) In df_archive, the column "source" looked exactly the same for every row based on visual assessment. A programmatic assessment showed that most of the values (2221) were on the iphone. This column is most likely irrelevant and can be removed. 
# 
# 5) In df_archive, the columns "doggo", "floofer", "pupper", and "puppo" contain the word "None" instead of N/A. The word "none" is also used in the names column, preventing missing entries for names from showing up as "NaN". 
# 
# 6) The timestamp column in df_archive is a string, not a date.time object. This needs to be converted to a date time object. 
# 
# 7) df_archive is missing the final rating, that is, numerator/denominator. 
# 
# 8) In df_archive, expanded_url is missing values. This column can most likely be removed. 
# 
# 
# 
# 
# Tidiness: 
# 
# 1) In df_archive, doggo, floofer, pupper, and puppo are 4 seperate columns. This should be one column, "dog classification", that contains either dogo, floofer, pupper, or puppo. 
# 
# 2) All the tables can be combined into one table containing the following columns: 
# - Tweet id
# - timestamp
# - name of dog
# - breed
# - dog category
# - number of retweets
# - number of likes
# 

# ## Step 3: Clean Data

# In[179]:


#Make copies of the dataframes
df_archive_clean = df_archive.copy()
df_image_clean = df_image.copy()
df_likes_clean = df_likes.copy()


# ### Quality Issue #1: Remove all retweets
# 
# 

# #### Define
# Remove retweeted Tweet ID's by removing all rows containing data in retweeted_status_id. 

# #### Code

# In[180]:


#Code
#Remove columns containing non null values in retweeted_status_id: 

df_archive_clean = df_archive_clean[df_archive_clean.retweeted_status_id.isnull()]


# #### Test

# In[181]:


#Test
#Test to see if there are any more rows that contain values in retweeted_status_id column
df_archive_clean[df_archive_clean.retweeted_status_id.notnull()]
df_archive_clean.retweeted_status_id.describe()
df_archive_clean.retweeted_status_id.unique()
df_archive_clean.info()


# In[182]:


#Code: 
#Remove columns containing information about retweets. 
df_archive_clean.drop(['retweeted_status_id', 'retweeted_status_user_id', 'retweeted_status_timestamp'], axis = 1, inplace = True)
df_archive_clean.info()


# ### Quality Issue #2: Dog Names

# #### Define
# 
# Replace invalid names ("a", "an", "the") with the expression "Invalid Name". Names of the dogs in the dataframe df_archive will be compared to a list compiled from 3 sources: 
# - list of most common dog names
# - list of most common female names
# - list of most common male names
# 
# All three lists will be combined, converted to a list, and the code will iterate through the list of dog names in df_archive and compare to the combined list of most common names. If not in the list, the code will return "Invalid Name". 

# #### Code

# In[183]:


#Re-assess the column after removing retweet rows: 
df_archive_clean.name.describe()



# In[184]:


#Import the list of most common female names
female_names = pd.read_csv('dist.female.first', sep = '\s+', header = None)

female_names.head()
female_names2= female_names[[0]]
female_names2.head()
female_names2.describe()


# In[185]:


#Import the list of most common male names
male_names = pd.read_csv('dist.male.first', sep = '\s+', header = None)
male_names.head()
male_names2 = male_names[[0]]
male_names2.head()
male_names2.describe()


# In[186]:


#Combine both female and male names into one dataframe to ease in appending to dog name list
human_names = female_names2.append(male_names2)
human_names.columns = ['DogName']
human_names.head()


# In[187]:


#Import list of most common dog names
dog_names = pd.read_csv('2018_dog_license2.csv')
dog_names.head()


# In[188]:


#Combine human and dog names into one dataframe
final_dog_list = dog_names.append(human_names, ignore_index = True)
final_dog_list.describe()


# In[189]:


#Convert the dog name into a list to iterate over
name_list = final_dog_list['DogName'].tolist()


# In[190]:


df_archive_clean.info()
df_archive_clean.iloc[2,9]


# In[191]:


#Iterate over the list of dog names in the dataframe and compare to the compiled list "name_list" to determine if the 
#name is a real name, or just an error ("a", "an", "the", etc.)

for i in range(0, len(name_list)):
    name_value = name_list[i]

    if type(name_list[i]) != str:
        continue
    else:
        name_list[i] = name_value.lower()
        

updated_names = []

for i in range(0, len(df_archive_clean)):
    original_name = ((df_archive_clean.iloc[i, 9]))
    original_name = original_name.lower()
    if original_name in name_list:
        updated_names.append(original_name)
    else:
        updated_names.append("Invalid Name")
        
print(updated_names)


# In[192]:


#Append list of updated names to dataframe
updated_names_dataframe = pd.Series(updated_names)
df_archive_clean['new_names'] = updated_names_dataframe.values
df_archive_clean.head()
df_archive_clean.new_names.value_counts()


# #### Test

# In[193]:


#Look at the new values of names to determine if there are any more values "None", "a", "the"
df_archive_clean.head()
df_archive_clean.new_names.value_counts()


# While there are more values that state "Invalid Name" it appears that the obviously invalid names ("a", "an", "the", "None") have been removed. In addition to removing these invalid names, this cleaning approach was slightly more conversative in that perhaps valid names that were not included in the list used for comparison were in fact dog names, it's just that these dog names were not included in the lists used. 

# ### Quality Issue #3: Incorrect Ratings

# #### Define
# 
# Create a regex function that will pull out the rating from the column "text". The regex function should account for decimals and cases where more than one rating is provided. 

# #### Code

# In[194]:


#loop through and iterate using regex to provide the rating
updated_ratings_list = []
tweet_id_list = []
text_str_list = []
import re
regex = r"\d{1,4}.?\d{0,4}\/\d{1,4}"

for i in range(0, len(df_archive_clean)):
    text_str = ((df_archive_clean.iloc[i, 5]))
    new_rating = re.findall(regex,text_str)
    updated_ratings_list.append(new_rating)
   # if (new_rating == '.10/10'):
        #print(new_rating)
    

updated_ratings_dataframe = pd.DataFrame(updated_ratings_list)
updated_ratings_dataframe.head()


#Iterate through the list and take the last rating as the most likely accurate rating
#print(len(updated_ratings_dataframe.columns))

final_rating_list = []
for i in range(0, len(updated_ratings_dataframe)):
    #if i > 3:
     #   break
        
    ratings = []
    for j in range (0, len(updated_ratings_dataframe.columns)):
        curr_rating = updated_ratings_dataframe.iloc[i, j]
        #print(curr_rating)
        if curr_rating != None:
            ratings.append(curr_rating)
            
    if len(ratings) > 0:
        #print("rating len %d" % len(ratings))
        final_rating_list.append(ratings[-1])
        #print(final_rating_list)
    
#print(final_rating_list)
            
    


# In[195]:


updated_ratings_dataframe = pd.Series(final_rating_list)
updated_ratings_dataframe.head()
df_archive_clean['new_ratings'] = updated_ratings_dataframe.values
df_archive_clean.head()
df_archive_clean.new_ratings.value_counts()


# #### Test

# In[196]:


#Re-assess the ratings column
df_archive_clean.head()
df_archive_clean.new_ratings.value_counts()


# #### Quality Issue #3, Continued Definition
# While it looks like the change did improve the ratings extracted from the text, there appears to be a number of remaining ratings that are still not correct: 
# - 3 13/10
# - 007/10
# 
# 
# The approach I'll take now is to pull up these three rows and visually determine what the correct rating is, and then correct the rating. 

# #### Code
# 

# In[197]:


#replace erroneous ratings
df_archive_clean['new_ratings'].replace('3 13/10', '13/10', regex=True, inplace=True)
df_archive_clean['new_ratings'].replace('007/10', '10/10', regex=True, inplace=True)


# #### Test
# 

# In[198]:


#Test to see if the incorrect ratings are in the dataframe: 
df_archive_clean.new_ratings.value_counts()


# ### Quality Issue # 4 Irrelevant Columns

# #### Define: 
# Remove irrelevant column "Source"
# 
# 

# #### Code

# In[199]:


#Remove the column "source"
df_archive_clean.head()
df_archive_clean.drop(['source'], axis = 1, inplace = True)


# #### Test

# In[200]:


#Preview the dataframe: 
df_archive_clean.head()


# ### Quality Issue #5 (The word "None" instead of NaN in columns doggo, floofer, pupper, and puppo)
# 

# #### Define
# Change the word None to "NaN" in columns "doggo", "floofer", "pupper", and "puppo"

# #### Code

# In[201]:


#Change the word none to NaN for columns mentioned in the definition
df_archive_clean['doggo'].replace('None', np.NaN, inplace = True)
df_archive_clean['floofer'].replace('None', np.NaN, inplace = True)
df_archive_clean['pupper'].replace('None', np.NaN, inplace = True)
df_archive_clean['puppo'].replace('None', np.NaN, inplace = True)



# #### Test

# In[202]:


#Determine if there are any more "None" values for the columns
print(df_archive_clean['doggo'].unique())
print(df_archive_clean['floofer'].unique())
print(df_archive_clean['pupper'].unique())
print(df_archive_clean['puppo'].unique())
df_archive_clean.info()


# ### Quality Issue #6: The timestamp column in df_archive is a string, not a date.time object. 

# #### Define
# Convert the column timestamp in df_archive_clean to a date time object.

# #### Code

# In[203]:


#conversion of column to datetime object
df_archive_clean['timestamp'] = pd.to_datetime(df_archive_clean.timestamp)


# #### Test

# In[204]:


#Test to see what the data type of timestamp is
df_archive_clean.info()


# ### Quality Issue #7: df_archive is missing final rating, numerator/denominator

# #### Define
# This issue was somewhat addressed in quality issue # 3 above (incorrect ratings). To make this data usable, it needs to be converted from a string to a float. 

# #### Code

# In[205]:


#Conversion of df_archive_clean['new_ratings'] to a fraction: 

score_float = []
for i in range (0, len(df_archive_clean)): 
    original_rating = df_archive_clean.iloc[i, 14]
    split_fraction = original_rating.split('/')
    numerator = float(split_fraction[0])
    denominator = float(split_fraction[1])
    float_score = numerator/denominator
    score_float.append(float_score)

float_ratings_dataframe = pd.Series(score_float)
float_ratings_dataframe.head()

#Append the updated scores to the df_archive dataframe: 

df_archive_clean['final_float_ratings'] = float_ratings_dataframe.values
df_archive_clean.head()
#df_archive_clean.new_ratings.value_counts()
#df_archive_clean.new_ratings_float = float(df_archive_clean.new_ratings)


# #### Test

# In[206]:


#Assess the new column of data (final float ratings), ensure it's a float
print(df_archive_clean.info())
print(df_archive_clean['final_float_ratings'].value_counts())



# ### Quality Issue #8: Removal of 'expanded_urls' column
# 

# #### Define
# Remove the column 'expanded_urls' column from the dataframe. In addition to removing this column remove the other unnecessary columns (rating_numerator, rating_denominator, in_reply_to_user_id, in_reply_to_status_id)

# #### Code

# In[207]:


#Removal of columns listed above in "Define"

df_archive_clean.drop(['rating_numerator', 'rating_denominator', 'in_reply_to_user_id', 'in_reply_to_status_id', 'expanded_urls'], axis = 1, inplace = True)



# #### Test

# In[208]:


#preview the dataframe to ensure columns were dropped

df_archive_clean.sample(50)


# ### Tidiness Issue #1: 
# In df_archive, doggo, floofer, pupper, and puppo are 4 seperate columns. This should be one column, "dog classification", that contains either dogo, floofer, pupper, or puppo. 

# #### Define
# Change the columns in df_archive_clean into one column entitled dog classification, that contains either 'doggo', 'floofer' or puppo. 

# #### Code

# In[209]:


#Melting wouldn't work because of all the N/A values for values not provided, so a loop would be easier

for index, row in df_archive_clean.iterrows():
    doggo = row[4]
    floofer = row[5]
    pupper = row[6]
    puppo = row[7]

    if doggo == 'doggo':
        df_archive_clean.loc[index, "classification"] = 'doggo'
    elif floofer == 'floofer':
        df_archive_clean.loc[index, "classification"] = 'floofer'
    elif pupper == 'pupper':
        df_archive_clean.loc[index, "classification"] = 'pupper'
    elif puppo == 'puppo':
        df_archive_clean.loc[index, "classification"] = 'puppo'
    else: 
        df_archive_clean.loc[index, "classification"] = 'not provided'
        
   


# #### Test

# In[210]:



df_archive_clean.sample(50)


# #### Code
# Additional code for further removal of unnecessary columns

# In[211]:


#Drop the extra unnecessary columns ('doggo', floofer', 'pupper', 'puppo', 'name', 'new_ratings')

df_archive_clean = df_archive_clean.drop(['doggo', 'floofer', 'pupper', 'puppo', 'new_ratings', 'name'], axis =1)





# In[212]:


df_archive_clean.head()


# In[213]:



df_archive_clean.info()


# In[214]:


df_archive_clean.to_csv('cleancopy1.csv')


# ### Tidiness Issue #2: Create one dataframe with all columns of interest

# #### Define
# Further clean df_likes and df_image for ease in merging with df_archive_clean. All three dataframes should have the same column, "tweet_id" which will be used for merging. Merge the three dataframes, df_archive, df_likes, and df_image. 

# #### Code

# In[215]:


df_likes.head()
df_likes.rename(columns = {'id': 'tweet_id'}, inplace = True)


# In[216]:


df_likes.head()
df_likes.drop(['Unnamed: 0'], axis =1, inplace = True)


# In[217]:


# Ensure df_image has tweet_id: 
df_image.head()


# We don't need all this information, since I am most interested in the most probably breed based on the predictive model. The columns I will keep from this dataframe are tweet_id and p1, since that is the hight probability. 

# In[218]:


#Create a copy of the dataframe with only the columns that we need: 

df_image_copy = df_image[['tweet_id', 'p1']].copy()
#new = old[['A', 'C', 'D']].copy()


# In[219]:


df_image_copy.head()


# In[220]:


df_image_copy.rename(columns = {'p1': 'predicted_breed'}, inplace = True)


# In[221]:


df_likes.head()


# In[222]:


df_image_copy.head()


# In[223]:


#Merge dataframes
df_image_likes = pd.merge(df_likes, df_image_copy, on = 'tweet_id', how = 'outer')


# In[224]:


df_image_likes_archive = pd.merge(df_image_likes, df_archive_clean, on ='tweet_id', how = 'outer')


# In[225]:


df_image_likes_archive.head()


# In[226]:


df_image_likes_archive.info()


# In[227]:


df_image_likes_archive['likes'].unique()


# ### Re-assessment

# Looking at the merged dataframe, it's clear that there are missing values for retweets. I'm going to assume these values are zero. 
# Additional cleaning of the dataframe requires: 
# 
# Quality:
# 
# Define: 
# 
# 1) Changing the null values of tweets and retweets to zero
# 
# 2) Dropping all rows that are na (these rows would only have tweet id's or only tweet id's and predicted breed.) 

# Code: 

# In[228]:


#Change the null values of likes and retweets to 0: 
df_image_likes_archive['likes'].replace(np.NaN, 0, inplace = True)
df_image_likes_archive['retweet_count'].replace(np.NaN, 0, inplace = True)


# In[229]:


#Ensure there are no null values for retweets and likes
df_image_likes_archive.info()


# In[230]:


#Drop all remaining rows that are NaN:
df_image_likes_archive = df_image_likes_archive[df_image_likes_archive.predicted_breed.notnull()]


# In[231]:


df_image_likes_archive.info()


# In[232]:


df_image_likes_archive = df_image_likes_archive[df_image_likes_archive.timestamp.notnull()]


# In[233]:


df_image_likes_archive.info()


# In[234]:


df_image_likes_archive.head()


# Save the cleaned dataframe to csv for further analysis: 

# In[235]:


#Save cleaned dataframe to csv: 
df_image_likes_archive.to_csv('twitter_archive_master.csv')


# ## Analysis and Visualization

# In[2]:


#Reload the clean dataframe
df = pd.read_csv('twitter_archive_master.csv')


# In[3]:


df.head()


# In[4]:


#Remove the first column that was imported 
df.drop(['Unnamed: 0'], axis =1, inplace = True)


# In[5]:


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

# In[7]:


# Group by breed, then summarize the variables 

breed_likes = df.groupby(['predicted_breed'])['likes'].mean()



# In[8]:


#Summarize the likes into a table or graph showing the most popular breeds
breed_likes.describe()


# In[9]:


#Convert to dataframe to get the breed associated with each number of likes

df_breed_likes = breed_likes.to_frame(name = 'likes')
df_breed_likes.head()


# In[10]:


# Drop all zero values: 
df_breed_likes = df_breed_likes[(df_breed_likes != 0).all(1)]


# In[11]:


#Add an index: 
df_breed_likes.reset_index(level=0, inplace=True)
df_breed_likes.head()


# In[12]:


df_breed_likes.info()


# In[13]:


df_breed_likes.likes.describe()


# In[14]:


#summarize with a graph showing the breeds with the greatest number of likes: 
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
df_breed_likes.plot.bar(x = 'predicted_breed', y = 'likes')
labels = df_breed_likes.predicted_breed

plt.title('Distribution of Number of Likes')
plt.xlabel('Dog Breed')


# Looking at the above graph it is not clear (due to the number of breeds) which are most liked. There are 143 total breeds in this data set. To get a better understanding of which breeds are most popular on the twitter site "We rate dogs", it makes more sense to take the top 20, for example, and look at the which breeds those are. 
# Also interesting is that the number of likes falls mostly below 10,000 (75%). There are less than 25% of the breeds in this subset of data that are greater than that, with the max at 46,549. It'll be interesting to see which breeds got the highest likes. 
# Below please find the subset of the 20 highest liked breeds, as well as the summary of the number of likes for the most popular breeds. 

# In[15]:


#find the greatest 20 likes in the dataframe df_breed_likes
df_breed_likes_largest = df_breed_likes.nlargest(40, 'likes')


# In[16]:


df_breed_likes_largest.describe()


# In[17]:


df_breed_likes_largest.plot.bar(x = 'predicted_breed')
x_labels = df_breed_likes.predicted_breed
labels = x_labels

plt.title('Distribution of Number of Likes')
plt.xlabel('Dog Breed')


# It looks like, from this plot, there were actually no dog breeds that had over 40,000 likes. Angora is a cat breed. Also, the machine learning model that was used to pull some of these dog breeds based on a picture didn't get all the top liked tweets correct. Starting with the first actual dog breed, it looks like the most liked breed is the Saluki, followed by breeds like flat-coated retriever, standard poodle and the norweigen elkhound. Of course, there may actually be a few breeds that received greater than 20,000 likes, and the machine learning algorithm just didn't identify the breed correctly. 
# Despite not knowing exactly which breeds received the most likes, we can say that the average number of likes for the breeds in this dataset is 7,297 and 75% of the breeds (correctly or incorrectly identified) received 17,900 likes or less. 

# ### Insight #2: Which classification resulted in the highest rating? 
# 
# The next area I'll explore is determining which classifications resulted in the highest ratings given by the dog owner. The classifications that I'm referring to are doggo (big pupper, usually older), floofer (dogs with excess fur), pupper (small dogs, usually younger), and puppo (transitional phase between pupper and doggo). This was a limited data set to begin with. That is, although there are 1994 tweet id's, most of the tweet id's did not provide this classification.  
# 
# The "Final float ratings" is a converted rating given to the dog by the person tweeting. These numbers started as fraction and were extracted from the tweet text. For example, a rating of value of 1.2 is actually a rating of 12/10. That is, their dog is of course so great that the numerator exceeds the denominator. 

# In[18]:


#Group by category to determine the average rating per classification
classification_ratings = df.groupby
classification_ratings = df.groupby(['classification'])['final_float_ratings'].mean()


# In[19]:


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

# In[20]:


#Convert the datetime into a datetime object: 
df['timestamp'] = pd.to_datetime(df.timestamp)
df.info()


# In[21]:


df.head()


# In[22]:


#Extract the hour from each timestamp for further classification into bins: 
for index, row in df.iterrows():
    time = row[4]
    df.loc[index, "extracted_hour"] = time.hour
    


# In[23]:


df.head()


# In[24]:


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

# In[25]:


df['extracted_hour'].unique()


# #### Visual: Word cloud of texts and descriptions about the dogs
# 
# Each tweet id in this dataframe has texts associated with the tweet. These words are typically words used to describe their dogs, as well as might they might be doing in the picture. 
# 
# A word cloud is a great way to represent a summary of the tweets about how people feel about their dogs, and why they tweet about them (or at least the people in this dataset). 
# 
# 

# In[27]:


#Download packages required for wordcloud: 
from PIL import Image
from wordcloud import WordCloud, STOPWORDS


# In[33]:


#Generate the word cloud image
wordcloud = WordCloud().generate(''.join(df['text']))
# Generate plot
plt.imshow(wordcloud)
plt.axis("off")
stopwords = set(STOPWORDS)
stopwords.add("https")
plt.title("Twitter - We Rate Dogs")
plt.show()


#wordcloud2 = WordCloud().generate(' '.join(text2['Crime Type']))


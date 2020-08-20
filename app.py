import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import re

from collections import Counter
import streamlit as st
import seaborn as sns
from nlppreprocess import NLP


def app():
    consumerKey=""          #confidential
    consumerSecretKey=""    #confidential
    accessToken=""          #confidential
    accessTokenSecret=""    #confidential

    #creating an object for authentication
    authenticate=tweepy.OAuthHandler(consumerKey,consumerSecretKey)
    #For access
    authenticate.set_access_token(accessToken,accessTokenSecret)
    #creating an api for retrieving tweets
    api=tweepy.API(authenticate,wait_on_rate_limit=True)

    st.title("Tweet Analyzer")
    st.subheader("A Tool which is able to:")
    st.write("Fetch tweets of a user or keyword")
    st.write("Perform Sentiment Analysis over tweets")
    st.write("Generate WordCloud")


    st.sidebar.markdown("<h1 style='text-align: center;'>About</h1>", unsafe_allow_html=True)
    st.sidebar.image("https://res.cloudinary.com/practicaldev/image/fetch/s--AhOnOSVL--/c_fill,f_auto,fl_progressive,h_320,q_auto,w_320/https://dev-to-uploads.s3.amazonaws.com/uploads/user/profile_image/340844/c6ddb46a-f369-44ab-bef9-d2d8f953f3ac.png",width=None)
    st.sidebar.title("Sunil Aleti")
    st.sidebar.text("Developer at Cognizant")
    st.sidebar.text("Blogger at DEV Community")
    st.sidebar.text("Quite Optimistic about AI")

    username=st.text_area("Enter Username without @")
    
    #selectBox
    activity=st.selectbox("Select Activity",["Fetch latest tweets","Generate Word Cloud","Visualize Sentiment Analysis"])
    if st.button("Submit"):
        if(len(username.strip())==0):
            st.error("username can't be empty 😒")
        else:
            posts=api.user_timeline(screen_name=username,count=100,lang="en",tweet_mode="extended")
    
            df=pd.DataFrame([tweet.full_text for tweet in posts if tweet.lang=="en"],columns=['Tweets'])
   
        
            bad_chars = [';', ':', '!', "*",".","_","-","\'","\""] 
            emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"  
        u"\U0001F1E0-\U0001F1FF"  
        "]+", flags=re.UNICODE)
            def cleanedTweet(tweet):
                tweet=re.sub(r"RT[\s]+","",tweet)  # To remove RT(retweet symbol)
                tweet=re.sub(r'@[A-Za-z0-9]+','',tweet) # To remove mentions
                tweet=re.sub(r'amp',"",tweet)
                tweet=re.sub(r"#","",tweet) # To remove Hashtags
                tweet=re.sub(r'http\S+', '', tweet,flags=re.MULTILINE) # To remove links
                tweet=re.sub(r'\n'," ",tweet)
                tweet = ''.join(i for i in tweet if not i in bad_chars) # To remove special characters
                tweet=emoji_pattern.sub(r'', tweet) # To remove emoji's in tweets
                return tweet


            df['Tweets']=df['Tweets'].apply(cleanedTweet)
            df2=pd.DataFrame(columns=["tweets"])
            nlp = NLP(replace_words=True,
            remove_stopwords=True,
            remove_numbers=False)
    
            df2['tweets'] = df['Tweets'].apply(nlp.process)


            def getSubjectivity(text):
                return TextBlob(text).sentiment.subjectivity
            def getPolarity(text):
                return TextBlob(text).sentiment.polarity

            df["Subjectivity"]=df2["tweets"].apply(getSubjectivity)
            df["Polarity"]=df2["tweets"].apply(getPolarity)
            # Function to get negative/positive/neutral of a tweet
            def getAnalysis(score):
                if score<0:
                    return "Negative"
                elif score==0:
                    return "Neutral"
                else:
                    return "Positive"

            df["Analysis"]=df["Polarity"].apply(getAnalysis)
    
            if(activity=="Visualize Sentiment Analysis"):
                st.success("Visualizing tweets...")
                st.markdown("<h2 style='text-align: center;'>Tweets</h2>", unsafe_allow_html=True)
                st.dataframe(df,width=None,height=None)
                #st.header("Polarity & Subjectivity")
                st.markdown("<h2 style='text-align: center;'>Polarity & Subjectivity</h2>", unsafe_allow_html=True)
                sns.scatterplot(x="Polarity", y="Subjectivity",data=df)
                st.pyplot()
        
                #Get % of positive tweets
                ptweets= df[df.Analysis=="Positive"]
                ptweets=ptweets["Tweets"]
        
                st.subheader("% of Positive Tweets")
                st.success(round((ptweets.shape[0]/df.shape[0])*100,1))
                #Get % of negative tweets
                ntweets= df[df.Analysis=="Negative"]
                ntweets=ntweets["Tweets"]
                st.subheader("% of Negative tweets")
                st.success(round((ntweets.shape[0]/df.shape[0])*100,1))

    
        
                st.markdown("<h2 style='text-align: center;'>Sentiment Analysis</h2>", unsafe_allow_html=True)
                sns.set(style="darkgrid")
                sns.countplot(x="Analysis",hue="Analysis",data=df)
                st.pyplot()

                #Most Repeated Words in tweets
                st.markdown("<h2 style='text-align: center;'>Most Frequent Words</h2>", unsafe_allow_html=True)
                words=[]
                for tweet in df2["tweets"]:
                    for j in tweet.split():
                        words.append(j)
                freq = Counter(words).most_common(30)
                freq = pd.DataFrame(freq)
                freq.columns = ['word', 'frequency']
                sns.barplot(y="word", x="frequency",data=freq)
                st.pyplot()


            elif(activity=="Generate Word Cloud"):
                st.success("Generating WordCloud..")
                allwords= ' '.join([twt for twt in df2["tweets"]])
                wordcloud=WordCloud(width=500,height=300,random_state=21,max_font_size=119).generate(allwords)

                plt.imshow(wordcloud,interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt.show())
            else:
                st.success("Fetching latest tweets")
                st.markdown("<h2 style='text-align: center;'>Latest Tweets</h2>", unsafe_allow_html=True)
                posts1=api.user_timeline(screen_name=username,count=10,lang="en",tweet_mode="extended")
                df3=pd.DataFrame()
                df3=pd.DataFrame([tweet.full_text for tweet in posts1],columns=['Tweets'])
                df3['Tweets']=df3['Tweets'].apply(cleanedTweet)
                j=1
                for i in df3["Tweets"][:10]:
                    st.write(str(j)+") "+i)
                    j+=1

if __name__ == "__main__":
	app()
# importing spotipy libary and authenticating client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
client_id ="{Insert your ID}" 
client_secret = "{Insert your secret key}"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


#### Getting Spotify catalog information for tracks ####
# create empty lists to store the results
track_id = []
track_name = []
artist_name = []
popularity = []

for i in range(0,10,10):
    track_results = sp.search(q='year:2019', type='track', limit=10,offset=i)
    for i, t in enumerate(track_results['tracks']['items']):
        track_name.append(t['name'])
        track_id.append(t['id'])
        artist_name.append(t['artists'][0]['name'])
        popularity.append(t['popularity'])

#### Data Preparation and Analysis ####
# Creating Top Tracks dataframe from the lists
import pandas as pd
df_tracks = pd.DataFrame({'track_name':track_name,'track_id':track_id,'artist_name':artist_name,'popularity':popularity})
print(df_tracks.shape)
df_tracks.head()
df_tracks.shape

##### Get audio feature information for tracks ####
# empty list, batchsize and the counter for None results
rows = []
batchsize = 10
nullvalues = 0
for i in range(0,len(df_tracks['track_id']),batchsize):
    batch = df_tracks['track_id'][i:i+batchsize]
    audio_features = sp.audio_features(batch)
    for i, t in enumerate(audio_features):
        if t == None:
            nullvalues = nullvalues + 1
        else:
            rows.append(t)

print('Number of tracks with no audio features:', nullvalues)
# Creating required Audio features dataframe from the lists
df_audio_features = pd.DataFrame.from_dict(rows,orient='columns')
columns_to_drop = ['analysis_url','track_href','type','key','mode','type','time_signature']
df_audio_features.drop(columns_to_drop, axis=1,inplace=True)
df_audio_features.rename(columns={'id': 'track_id'}, inplace=True)
df_audio_features.head()

# Inner join both dataframes on track_id column
df = pd.merge(df_tracks,df_audio_features,on='track_id',how='inner')
df.shape()
df.head()
df.info()

#Drop any duplicated rows
df[df.duplicated(subset=['artist_name','track_name'],keep=False)]

#Save the final file with top tracks and audio features
df.to_csv('SpotifyAudioFeatures.csv', index=False)
del df


# Download last 3 weeks Daily global Charts from https://spotifycharts.com/regional/global/daily/latest/ to directory
# #Merging Top 200 Charts 10/1/19 to 10/19/19
from os import listdir
directory = "/Users"
filepaths = [f for f in listdir(directory) if f.endswith('.csv')]
filepaths.sort()
df = pd.concat(map(pd.read_csv, filepaths))
df.to_csv(directory+"/regional-global-daily.csv", index=False)
del df

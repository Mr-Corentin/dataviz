import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import altair as alt

st.sidebar.title(

    "Corentin Peron data",
    

)

st.write("My linkedin profile: [link](https://www.linkedin.com/in/corentin-peron-b983b519b/)")



@st.cache(allow_output_mutation=True)
def load_df(df_name1,df_name2):
    df = pd.DataFrame(pd.read_json(df_name1))
    df2=pd.DataFrame(pd.read_json(df_name2))
    df3=pd.concat([df, df2])
    return df3

df3=load_df('StreamingHistory0.json','StreamingHistory1.json')
st.title('Welcome to my spotify data analysis!')
#some useful fonctions
def get_day(df):
    return df.day
def get_month(df):
    return df.month
def get_weekday(df):
    return df.weekday()
def get_hours(df):
    return df.hour
def get_minutes(df):
    return df.minute
def get_year(df):
    return df.year
def count_rows(rows):
    return len(rows)

@st.cache()
def create_col(df):
    #convert end time to datetime
    df['endTime']=pd.to_datetime(df['endTime'])

    df['periods']=df['endTime'].dt.to_period('M')

    #create column minutesPlayed from the msPlayed column
    df['minutesPlayed']=(df['msPlayed']/1000)/60

    #create useful column thanks to the functions
    df['year']=df['endTime'].apply(get_year)

    df['month']=df['endTime'].apply(get_month)

    df['periods']=df['periods'].astype(str)

    df['hour']=df['endTime'].apply(get_hours)
    return df
df3=create_col(df3)
#list of the possible periods
per=['2021-08','2021-09','2021-10','2021-11','2021-12','2022-01','2022-02','2022-03','2022-04','2022-05','2022-06','2022-07','2022-08']
def print_df(df):
    st.title('The dataset:')
    st.write(df)
print_df(df3)

@st.cache()
def line_chart():
    #streamlit internal plots and interactive one
    #group by periods and sum the minutes played
    bymin=df3.groupby(['periods'])['minutesPlayed'].sum()
    #group by periods and count the tracks played

    bytrack=df3.groupby(['periods'])['trackName'].count()
    
   
    return (bymin,bytrack)
st.title('Evolution of my listening activity by periods')
bymin,bytrack=line_chart()
tab1, tab2 = st.tabs(["Evolution of number of minutes played by periods", "Evolution of number of musics played by periods"])
with tab1:
    st.line_chart(bymin)
with tab2:
    st.line_chart(bytrack)
with st.expander("See explanation"):

     st.write("We can see that evolution by time of listening and by number of musics launch is very similar but there is some differences like in 06-2022 or 03-2022")

def interact_histogramm():
    #external plots (plotly) and interactive one
    st.title('My top 10 by minutes of listening by the month and year you want!')

    option = st.selectbox(
        'Please select which month and year do you want to see',
        per)

    'You selected year and month: ', option

    top = st.slider('The top you want', 3, 50, 10)
    st.write('You selected top',top)
    mask=df3['periods']==option
    #mask to get applicate the option to the dataframe
    byperiods=df3[mask]
    tab1, tab2 = st.tabs(["My top 10 artist played by periods", "My top 10 tracks played by periods"])
    

    with tab1:
        #group by artist and sum the minutes played

        bymsar=byperiods.groupby('artistName')['minutesPlayed'].sum()
        bymsar=bymsar.reset_index()
        bymsar=bymsar.sort_values(by=['minutesPlayed'],ascending=False)
        fig = px.histogram(bymsar,x='artistName',y='minutesPlayed',width=800, height=400)
        fig.update_xaxes(range=[0, top-1])
        st.plotly_chart(fig)
    with tab2:
        bymsar=byperiods.groupby('trackName')['minutesPlayed'].sum()
        bymsar=bymsar.reset_index()
        bymsar=bymsar.sort_values(by=['minutesPlayed'],ascending=False)
        fig = px.histogram(bymsar,x='trackName',y='minutesPlayed',width=800, height=400)
        fig.update_xaxes(range=[0, top-1])
        st.plotly_chart(fig)
      



    
    with st.expander("See explanation"):

     st.write("Huge differences between year and month, but explainable by many of things. For example I see Laylow in concert in march 2022 and that's he is my top 1 in 03-2022!")
interact_histogramm()
def ar_chart():
    #internal streamlit plot
    #group by hour and count the number of tracks launch
    byhour=df3.groupby('hour').apply(count_rows)
    st.title('Number of musics launch by hour')
    st.area_chart(data=byhour)

ar_chart()
def bar_hour():
    #internal streamlit plot and interactive one
    st.title("To 10 of my artist most listened to (in minutes listened to) by hour")
    hour_to_filter = st.slider('Please select an hour', 0, 23, 17)
    #mask to take the hour selectionate
    mask_hour=(df3['hour']==hour_to_filter)
    hours=df3[mask_hour]

    hours_artist=hours.groupby('artistName')['minutesPlayed'].sum()
    hours_artist=hours_artist.reset_index()
    hours_artist=hours_artist.sort_values(ascending=False,by=['minutesPlayed'])[:10]
    st.bar_chart(data=hours_artist,x='artistName',y='minutesPlayed')
    with st.expander("See explanation"):

     st.write("We can see that depending on the time the results are very different, for example at 21 we can see music for parties while at the end of the evening it will be quieter songs")

bar_hour()
st.write('Now I will work on the playlist dataset, wich was join with the others datasets')
st.title('Playlist dataset:')
def df_clean():
    dfpl = pd.DataFrame(pd.read_json('Playlist1.json'))

    play=dfpl['playlists']

    df = pd.json_normalize(play)

    items=df['items']
    dfit = pd.json_normalize(play,record_path='items',meta=['name','lastModifiedDate', 'description'])
    dfit['addedDate']=pd.to_datetime(dfit['addedDate'])
    dfit=dfit.drop(['episode', 'localTrack','description'],axis=1)
    dfit['periods']=dfit['addedDate'].dt.to_period('M')
    return dfit
dfit=df_clean()
print_df(dfit)    
def pie_chart():
    #external streamlit plot
    st.title('Repartition of songs in my playlists')
    pl_name=pd.DataFrame(dfit.groupby('name').apply(count_rows))

    pl_name=pl_name.reset_index()
    pl_name = pl_name.set_axis(["name", "count"], axis=1)

    fig = px.pie(pl_name, values='count', names='name')

    st.plotly_chart(fig)

pie_chart()

def heatmap():
    #external streamlit plot
    by_artits_play2=dfit.groupby(['periods','name']).apply(count_rows)
    by_artits_play2=pd.DataFrame(by_artits_play2)

    by_artits_play2=by_artits_play2.reset_index()
    by_artits_play2['periods']=by_artits_play2['periods'].astype(str)
    by_artits_play2 = by_artits_play2.set_axis(["periods", "name","count"], axis=1)
    st.title('Links between my playlist and periods for adding song')
    artist_play=alt.Chart(by_artits_play2).mark_rect().encode(
        x='name',
        y='periods',

        color='count'
    ).properties(
        width=800,
        height=550
    ).interactive()

    st.altair_chart(artist_play)
    with st.expander("See explanation"):

     st.write("We can see that the Sah playlist is the one in which the addition of music is the most regular and important, it is indeed my most used playlist and there are 139 additions in 09/2020 because it is the month of creation of my account. On the contrary, there are very few additions to the Tri playlist because it was just a playlist for sorting music and that's why there were only additions over 2 months.")

heatmap()


#external streamlit plot and interactive one
st.title('Number of occurrences of songs, colored by album, by singer you choose')

title = st.text_input('From wich artist do you want to see the songs of?', 'Laylow')
#the user enter the artist he want to see

st.write('You choose', title)
@st.cache()
def interact_artist(df):
    maskarti=df['track.artistName']==title
    arti=df[maskarti]
    by_arti=pd.DataFrame(arti.groupby(['track.trackName','track.albumName']).apply(count_rows))
    by_arti=by_arti.reset_index()
    by_arti = by_arti.set_axis(["trackName", "albumName",'Count'], axis=1)
    fig = px.bar(by_arti, x='trackName', y='Count', color='albumName',width=1000, height=600)
    return fig

fig=interact_artist(dfit)
st.plotly_chart(fig)



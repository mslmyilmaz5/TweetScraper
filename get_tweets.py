import requests # Twitter API üzerinden istek için.
import pandas as pd # Data manipülasyon için.
import csv # Dosya yazımı için.
import dateutil.parser # Datetime çevirmek için kullanılır.
import time # Iki request arasında beklemek icin
from config import bearer_token,query_string,tw_start_date,tw_end_date # tweet config ayarları

#bearer_token'ı initilaze eder.
def auth():
    return bearer_token

#bearer_token header'i olusturur.
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

#request url'i; query,baslangic,bitis zamanları 
#ve bir requeste istenebilecek maximum
#request sayfa sayisini parametre 
#olarak alır ve istenilen url requesti modifiye eder.
def create_url(keyword, start_date, end_date, max_results = 20):
    #Academic Acces Token'a sahip oldugumuz icin endpointi,
    #full arsivhe endpoint olarak ayarliyoruz.
    search_url = "https://api.twitter.com/2/tweets/search/all" #End point search url'i
    #Kullandigimiz endpoint icin istedigimiz parametleri belirliyoruz.
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id,referenced_tweets.id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source,entities,possibly_sensitive',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified,entities,profile_image_url,withheld,pinned_tweet_id',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)


#Kullanacagimiz endpoint ve bearer token'imizi birbirlerine bağlıyoruz.
#Eger request'ten next_token fieldi gelirse ilerideki islemler icin onu tutuyoruz.
def connect_to_endpoint(url, headers, params, next_token = None,):
    params['next_token'] = next_token # next_token varsa bir sonraki page var demektir.
    response = requests.request("GET", url, headers = headers, params = params) # request gönderir.
    print("Endpoint Response Code: " + str(response.status_code)) # response geri donus kodu 200 ise request basarılı donmustur.
    if response.status_code != 200: # response geri donus kodu 200 den farklıysa hata verir.
        raise Exception(response.status_code, response.text)
    return response.json() # donen requesti json olarak dondurur.




#Json responsedaki gelen datadan istediğimiz fieldlari tutar 
#ve onu olusturgu csv dosyasına ekler.
def append_to_csv(json_response, fileName):
    counter = 0 # Total tweet sayisini tutar.
    user_dict = {} # Atılan tweeetlerin user fieldini tutmak icin gerekli. (user-tweet dicti)
    exp_dict =  {} # Atılan tweetlerin (eğer varsa) expansion fieldini tutmak icin gerekli. (exp-tweet dicti)

    #Hedef csv dosyasini olusturur.
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

#Donen json response uc temel data seklinde doner; 'data', 'includes','meta'
#'data' -- Tweet'le alakali bilgileri tutar.
#'includes' -- Tweet'i atan user'in bilgilerine ulasmak icin kullanacagiz.
#'meta' -- Token,Next-Token (Page-New Page) islemleri icin kullanacagiz.
   

# Gelen response'da eğer tweet 'retweet' ise;
# tweet texti yarım fortmatta, like, quote, reply 
# sayılar ise default olarak 0 geliyor.
# Bunu düzeltmek için response ile beraber gelen
# expansion field'ındaki tweet objectini kullanacağız.

    if ('tweets') in json_response['includes']: # Eğer response 'tweets' fieldini iceriyorsa
     
     # Expansion field
     for expansion in json_response['includes']['tweets']: # Eğer 'tweets' expansion fieldini icerıyorsa 
        
        exp_dict[expansion['id']] ={ 
            'full_text': expansion['text'],  # Retweet edilen tweet'in full textini verir.
            'true_like': expansion['public_metrics']['like_count'], # Retweet edilen tweet'in like sayısını verir.
            'true_quote':expansion['public_metrics']['quote_count'], # Retweet edilen tweet'in quote sayısını verir.
            'true_reply':expansion['public_metrics']['reply_count'], # Retweet edilen tweet'in reply sayısını verir.
            'retweeted_user_id':expansion['author_id'] # Retweet edilen user'in id'sini tutuar.
        }
    # User field
    for user in json_response['includes']['users']:
       
       # user entities'i tutar. 
       if ('entities' in user): 
        entities = user['entities']
       else:
        entities = ''

       # Profilindeki en başta tutturulan tweet'in id'sini tutar.
       if ('pinned_tweet_id' in user):
        pinned_tweet_id = user['pinned_tweet_id']
       else:
        pinned_tweet_id = ''
       
       # Profil resminin urlsini tutar.
       if ('profile_image_url' in user):
        profile_image_url = user['profile_image_url']
       else:
        profile_image_url = ''

       # Hesabın yasaklı olup olmadığı bilgisini tutar.
       if ('withheld' in user):
        withheld = user['withheld']
       else:
        withheld = ''
       
       user_dict[user['id']] ={'username': user['username'] , # account name tutar.
                               'description':user['description'], # hesap biosunun textini tutar.
                               'name':user['name'], # Twitter'a girdiği ismi tutar.
                               'author_created_at': user['created_at'], # Hesabın ne zaman olusturuldugu bilgisini tutar.
                               'verified':user['verified'], # Hesabın onaylı olup olmadğı bilgisini tutar.
                               'entities':entities,
                               'pinned_tweet_id':pinned_tweet_id,
                               'profile_image_url':profile_image_url,
                               'withheld':withheld,
                               'user_tweet_count':user['public_metrics']['tweet_count'], # Hesabın toplam tweet sayısını tutar.
                               'user_followers_count': user['public_metrics']['followers_count'], # Hesabın toplam takipçı sayısını tutar.
                               'user_following_count': user['public_metrics']['following_count'], # Hesabın toplam takip ettiği hesap sayısını tutar.
                               'user_listed_count': user['public_metrics']['listed_count']}  # List sayısını tutar.
    # Tweet field                          
    for tweet in json_response['data']:

        # Author ID
        author_id = tweet['author_id']
        # Time created
        created_at = dateutil.parser.parse(tweet['created_at']) # Date Time çevirir.
        # Tweet ID
        tweet_id = tweet['id']
        # Language
        lang = tweet['lang']
        # Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count'] # Tweet retweet sayısını verir.
        reply_count = tweet['public_metrics']['reply_count'] # Tweet reply sayısını verir.
        like_count = tweet['public_metrics']['like_count'] # Tweet like sayısını verir.
        quote_count = tweet['public_metrics']['quote_count'] # Tweet quote sayısını verir.
        # Tweet text
        text = tweet['text']
        # Entities

        if ('entities' in tweet): # Eger tweet entitiy bilgisi iceriyorsa

            entities = tweet['entities']

            if ('hashtags') in tweet['entities']: # Eger entitiy hashtags bilgisi iceriyorsa
              has_list = []
              # Entitiy icinde kullandıgı her hashtag'i listede tutar.
              for i in range(len(tweet['entities']['hashtags'])):
                 has_list.append(tweet['entities']['hashtags'][i]['tag'])
                 hashtags = has_list 
            else:
                 hashtags = '' # İçermiyorsa hastag boş.

            if ('mentions') in tweet['entities']: # Eger entitiy mentions bilgisi iceriyorsa
               men_list = []
               # Entitiy icinde kullandıgı her mention'u listede tutar.
               for i in range(len(tweet['entities']['mentions'])): 
                  men_list.append(tweet['entities']['mentions'][i]['username'])
                  mentions = men_list 
            else:
                  mentions = '' # İçermiyorsa mention boş.  
        else:

         entities = ''
        
        # Conversion id
        conversation_id = tweet['conversation_id']

        # Referenced Tweet
        if ('referenced_tweets') in tweet:
         referenced_tweets = tweet['referenced_tweets']
        else:
         referenced_tweets = ''

        # Reply user user id
        if ('in_reply_to_user_id') in tweet:
         in_reply_to_user_id = tweet['in_reply_to_user_id']
        else:
         in_reply_to_user_id = ''

        # Posible sensitive
        possibly_sensitive = tweet['possibly_sensitive']

        # Tweet source
        if ('source') in tweet:
         source = tweet['source']
        else:
         source = ''

        # Geo info
        if ('geo' in tweet):
            if ('place_id') in tweet['geo']:   
             geo = tweet['geo']['place_id']
        else:
             geo = " "
        

        # Atılan tweet fieldi ile tweeti atan kısının user fieldini bağlar.
        # Acıklamaları yukarda.
        author_info = user_dict[tweet['author_id']]
        user_tweet_count = author_info['user_tweet_count']
        user_followers_count = author_info['user_followers_count']
        user_following_count = author_info['user_following_count']
        user_listed_count = author_info['user_listed_count']
        author_screen= author_info['username']
        description = author_info['description']
        name = author_info['name']
        author_created_at = author_info['author_created_at']
        verified = author_info['verified']
        user_entities = author_info['entities']
        pinned_tweet_id = author_info['pinned_tweet_id']
        profile_image_url = author_info['profile_image_url']
        withheld = author_info['withheld']


        retweeted_user_id = ''

        if ('referenced_tweets') in tweet: # Eğer tweet 'referenced_tweets' fieldi içerioyrsa

          if tweet['referenced_tweets'][0]['type'] == 'retweeted': # Eğer tweet retweet ise
           
           # Retweet edilen tweet ile ile retweet edilen tweeti aynı columnda tutar.
           retweet_tweet = exp_dict[tweet['referenced_tweets'][0]['id']]
           retweeted_user_id = retweet_tweet['retweeted_user_id']
           text = retweet_tweet ['full_text']
           like_count = retweet_tweet ['true_like'] 
           quote_count = retweet_tweet ['true_quote']
           reply_count = retweet_tweet ['true_reply']
        
        # Cektiğimiz datayı listede topluyoruz.

        try:
         res = [tweet_id,created_at,lang,source,text,like_count,quote_count, 
         reply_count,retweet_count,entities,hashtags,mentions,conversation_id,
         referenced_tweets,possibly_sensitive,in_reply_to_user_id,retweeted_user_id,
         geo,

         author_id,author_created_at,author_screen,name,description,user_tweet_count,
         user_followers_count,user_following_count,user_listed_count,
         verified,user_entities,pinned_tweet_id,profile_image_url,withheld,
         ]
       
        # İlgili tweet bilgilerini row-row yazıyoruz.
         csvWriter.writerow(res)
         counter += 1
        except Exception as e:
            print(e)
            pass
    csvFile.close()

    # Bir responsetaki total t
    print("Bu response eklenen toplam tweet sayısı: ", counter)
    
    
bearer_token = auth() #  bearer token'i mizi cagrıyoruz.
headers = create_headers(bearer_token) # headersi olusturuyoruz
max_results = 500 # max_results'u 500 olarak ayarlıyoruz. (Twitter verdigi maximum sayi)


# query parametresini alarak token islemlerini halleder.
# Twitter her requestte belli bir sayida response veriyor.
# Eğer bu sayidan daha fazla response almak istiyorsak
# dönen responsetaki 'meta' fieldini kullanarak bir sonraki
# request'in token'i ile simdiki request'tin  next token'ini baglıyoruz.
def get_tweets(query):

 total_tweets = 0 # Cekilen toplam tweet sayısını tutar.
 count = 0 
 flag = True
 next_token = None # Baslangicta next token yok olarak initilaze edilir.
 
 # Cekilecek tweetlerin zaman araligi belirlenir.
 start_date=tw_start_date
 end_date=tw_end_date

 while flag: # Next token olduğu sürece 

        print("#"*40)
        print("Token: ", next_token)
        url = create_url(query, start_date,end_date, max_results) # istenilen parametrelerle request url'si olusturur.
        json_response = connect_to_endpoint(url[0], headers, url[1], next_token) # endpointi bağlar.
        result_count = json_response['meta']['result_count']
        if 'next_token' in json_response['meta']: # Eğer response next_token içeriyorsa
            next_token = json_response['meta']['next_token'] # Next_token'ı tutar
            print("Sıradaki token: ", next_token)
            # Eğer responsetaki tweet sayısı 0'dan fazla ve next_token var ise
            if result_count is not None and result_count > 0 and next_token is not None:
                append_to_csv(json_response, "data.csv") # Response'u csv'ye donusturen fonksiyonu cagırır.
                count += result_count
                total_tweets += result_count
                print("Toplam eklenen tweet sayısı: ", total_tweets)
                print("#"*40)
                time.sleep(5) # Requestler arası 5 saniye uyur.                
        else: # Eğer next_token yoksa (Request son sayfada demektir.)
            if result_count is not None and result_count > 0:
                print("#"*40)
                append_to_csv(json_response, "data.csv")
                count += result_count
                total_tweets += result_count
                print("Toplam eklenen tweet sayısı: ", total_tweets)
                print("#"*40)
                time.sleep(5) # Requestler arası 5 saniye uyur.  
            flag = False # Loop'u durdurur.
            next_token = None # Next token'ı sıfılar.
        time.sleep(5)

 print("Toplam tweet sayısı: ", total_tweets)




def main():

    csvFile = open("data.csv", "a", newline="", encoding='utf-8') # yeni data.csv'i olusturur.
    csvWriter = csv.writer(csvFile)

    # Header rowu yazar.
    csvWriter.writerow(['tweet_id', 'tweet_created_at', 'lang','source', 'text', 'like_count',
     'quote_count','reply_count','retweet_count','entities','hashtags','mentions','conversation_id'
     ,'referenced_tweets','possibly_sensitive','in_reply_to_user_id','retweeted_user_id','geo','author_id'
     ,'author_created_at','author_screen','name','description','user_tweet_count',
     'user_followers_count','user_following_count','user_listed_count','verified','user_entities',
     'pinned_tweet_id','profile_image_url','withheld'])

    csvFile.close()

    query = query_string
    get_tweets(query) # query ile tweetleri ceker.
   

if __name__  ==  '__main__':
      main()

 

 
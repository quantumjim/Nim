import tweepy
import time
import random
from PIL import Image

# to authenticate with twitter, you need to have the required info
keys = eval(open('account.txt').read())
auth = tweepy.OAuthHandler(keys[0],keys[1])
auth.set_access_token(keys[2],keys[3])
username = keys[4]

real_api = tweepy.API(auth)
real_api.verify_credentials()

class FakeAuthor():
    def __init__(self):
        self.screen_name = '<insert author here>'

class FakeStatus():
    def __init__(self,full_text=None):
        self.id = '<insert id here>'
        self.author = FakeAuthor()
        if full_text!=None:
            self.full_text = full_text
        else:
            self.full_text = '@'+username+' '+input()
        
class FakeApi():
    
    def update_status(self, text, in_reply_to_status_id=None):
        if in_reply_to_status_id:
            print('\n\nIn reply to',in_reply_to_status_id)
        else:
            print('\n')
        print(text)
        return FakeStatus('')
    
    def update_with_media(self, filename, text, in_reply_to_status_id=None):
        img = Image.open(filename)
        img.show()
        return self.update_status(text, in_reply_to_status_id=in_reply_to_status_id)
    
def twitter_print(text, num, reply_to=None, twitter=True):
    
    if twitter:
        api = real_api
    else:
        api = FakeApi()
        
    if reply_to:
        status = api.update_status(str(num)+'/\n\n'+text,in_reply_to_status_id=reply_to)
    else:
        status = api.update_status(str(num)+'/\n\n'+text)
        
    num += 1
        
    return status.id, num

def twitter_input(pre_turn,thread_id, num, max_time=600, twitter=True):

    if twitter:
        api = real_api
    else:
        api = FakeApi()
        
    # send tweet
    status = api.update_status(str(num)+'/\n\n'+pre_turn+'\n\nTwitter users: it\'s your turn to choose how many marbles to take!\n\nReply with 1, 2 or 3.',in_reply_to_status_id=thread_id)
    thread_id = status.id
    num += 1

    # check for replies
    t0 = time.time()
    input_given = False
    while (time.time()-t0)<max_time and not input_given:
        try:
            if twitter:
                replies = tweepy.Cursor(api.search,q='to:{}'.format(username),since_id=status.id, tweet_mode='extended').items()
            else:
                replies = [FakeStatus()]
            for reply in replies:
                if not input_given:
                    author = reply.author.screen_name
                    try:
                        output = eval(reply.full_text[len(username)+2::])
                        if output in [1,2,3]:
                            input_given = True
                    except:
                        api.update_status('@'+author+' That isn\'t a valid move. Try again.',in_reply_to_status_id=reply.id)
        except:
            pass
        if not input_given:
            time.sleep(5)

    if input_given:
        status = api.update_status(str(num)+'/\n\n'+
                                   'As suggested by @'+author+', '+str(output)+' marble'+'s'*(output!=1)+' will be taken.\n\n'+
                                   'Now wait a moment for the quantum computer to take its turn...',
                                   in_reply_to_status_id=thread_id)
    else:
        output = random.choice([1,2,3])
        author = 'random'
        status = api.update_status(str(num)+'/\n\n'+
                                   'Since no input has been given, a random value of '+str(output)+
                                   ' has been chosen.\n\n'+
                                   'Now wait a moment for the quantum computer to take its turn',
                                   in_reply_to_status_id=thread_id)
    num += 1
    thread_id = status.id

    return output, author, thread_id, num
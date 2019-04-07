# def get_user_avatar(backend, details, response, social_user, uid,
#                     user, *args, **kwargs):
#     import ipdb; ipdb.set_trace()
#     url = None

def update_user_avatar(*args, **kwargs):
    """
        Obtain user object
    """
    # user_is_new = kwargs.get('is_new')
    user_in_db = kwargs.get('user')
    
    """
        Obtain avatar
    """
    res = kwargs.get('response')
    if not res:
        return
    avatar_url = res.get('picture')
    
    # expires_in = res.get('expires_in')
    
    """
        Assign avatar to user object
    """
    user_in_db.avatar_url = avatar_url
    
    
"""
    Example input kwargs:

    kwargs = {
        'response': {
            'access_token':'ya29.GlvlBvrYj6xYOKQH2fadQWs0t7X4DDAyV5iISOb9rOBJFnu9FysdCVn36lz8yqueYIrXV9D7SCeXjUPh6G_bXY8HRJfm8XZNHivOFsapJlCISpwHzrUDUSePvEDC', 
            'expires_in': 3598, 
            'scope': 'https://www.googleapis.com/auth/userinfo.profile openid https://www.googleapis.com/auth/userinfo.email', 
            'token_type': 'Bearer', 
            'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjZmNjc4MWJhNzExOTlhNjU4ZTc2MGFhNWFhOTNlNWZjM2RjNzUyYjUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiNzMyOTg4NDk4ODQ4LXZ1aGQ2ZzYxYm5scWUzNzJpM2w1cGJwbmVydGV1Nm5hLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiNzMyOTg4NDk4ODQ4LXZ1aGQ2ZzYxYm5scWUzNzJpM2w1cGJwbmVydGV1Nm5hLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTE0OTM0MjAzMzc1Mzc5ODQyOTk2IiwiaGQiOiJ1bWljaC5lZHUiLCJlbWFpbCI6InNoYXVuZ2NAdW1pY2guZWR1IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJTRmNhWVRiUXlPdS1fejZ4ZE9zU1B3IiwiaWF0IjoxNTU0NjcyNTM4LCJleHAiOjE1NTQ2NzYxMzh9.b13pvrrHNMU2Pe_5co4SaVcGM9YtLsxB9qHAkWWK5wIBGRlP50FrrTN6oH2-9XaTRDQ9Gy3QBWYz5LQE_aM8ADwfD2UwVH56H48PIqb62Dlps9O44Lm17IB9-LQgRC7rP-tB5LSN59rjJfMp66gwQacrpejE_A3JKhNmZB1_X284m0nYhAYjwnADKe3NnvOZjTpQHwlf7dSvD59tVRq-S1dEldlWWTn28lOLQyj9D8TIqRjg7lkaeObVFQWDuzE56c-l4MgjmADvzshXZEr3dIQwLCexb5FnRDuIuEVt2Sn6R172OKLVXYJwihe0GZb5YzrVbhM_EZWl59q1jiT98w', 
            'sub': '114934203375379842996', 
            'name': 'My First Name My Last Name', 
            'given_name': 'My First Name', 
            'family_name': 'My Last Name', 
            'picture': 'https://lh6.googleusercontent.com/-bnVkVdwoh28/AAAAAAAAAAI/AAAAAAAAHc8/aWCRIeoRAhg/photo.jpg', 
            'email': 'username@example.com', 
            'email_verified': True, 
            'locale': 'en', 
            'hd': 'umich.edu'
        }, 
        'user': <CustomUser: username@example.com>, 
        'strategy': <rest_social_auth.strategy.DRFStrategy object at 0x106af8470>, 
        'storage': <class 'social_django.models.DjangoStorage'>, 
        'backend': <social_core.backends.google.GoogleOAuth2 object at 0x106b0a198>, 
        'is_new': False, 
        'request': {
            'uuid': '', 
            'created_at': '', 
            'modified_at': '', 
            'code': '4/JgFcz41SHuEf15lIW1J0Cr19FHT6AMR0WgELINY9u0N78pE7UjuHEmBkRYB0jQquXyTZ55Fjl1AQn8uCV2zbGUU', 
            'provider': 'google-oauth2'
        }, 
        'details': {
            'username': 'username', 
            'email': 'username@example.com', 
            'fullname':'My First Name My Last Name', 
            'first_name': 'My First Name', 
            'last_name': 'My Last Name'
        }, 
        'pipeline_index': 10, 
        'uid': 'username@example.com', 
        'social': <UserSocialAuth: username@example.com>, 
        'new_association': False, 
        'username': 'username'
    }
"""
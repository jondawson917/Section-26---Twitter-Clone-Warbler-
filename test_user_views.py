import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
#-------------------------------------
#Further-study - Can refactor code to include User Class example Testuser in the setUp function
#--------------------------

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        # self.testuser = User.signup(username="testuser",
        #                             email="test@test.com",
        #                             password="testuser",
        #                             image_url=None)
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None
                                    bio="The story about my life. Let me talk about my pimples.")

        
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up any fouled commit() transaction."""

        db.session.rollback()

    def test_signup_get(self):
        """Can we SIGNUP during GET request"""
        
        with self.client as client:
            resp = client.get("/signup")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>',html)
    
    def test_signup_post(self):
        """Can we SIGNUP during a POST request"""
        
        with self.client as client:
            resp = client.post("/signup", data={"username": "testuser","email": "test@test.com", "password": "testuser", "image_url": "None"})

            self.assertEqual(resp.status_code, 200)
    def test_login_get(self):
        """Can we access the login form??"""
        with self.client as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
            self.assertIn('<img src="/static/images/warbler-logo.png" alt="logo">', html)
    

    def test_login_post(self):
        """Can we post login data??"""
        with self.client as client:
            resp = client.post('/login', data={"username": "testuser", "password": "testuser"}, follow_redirects=True)

            html = resp.get_data(as_text=True)
            user = User.query.one()
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.username}', "testuser")
            #Should hash the password such that it won't be displayed as plain text 
            self.assertNotIn(f'{self.password}', "password")

    def test_logout(self):
        """Can we logout successfully?"""

        with self.client as client:
            resp = client.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-primary btn-block btn-lg">Log in</button>', html)

    def test_list_users(self):
        """Can we show the list of users on the index.html page??"""
        
        with self.client as client:
            resp = client.get("/users", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.testuser.username}", html)
            self.assertIn(f"{self.testuser.username}", html)
    
    def test_user_show(self):
        """Can we display the user profile given a user id?"""
        

        with self.client as client:
            resp = client.get(f'/users/{self.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
    
    def test_add_like(self):
        """Can we add a like for one user?"""

        new_msg = Message(text="New message", timestamp="2022-07-22 00:01:21.372552", user_id = self.testuser.id)
        db.session.add(new_msg)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/users/add_like/{new_msg.id}", follow_redirect=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 302)
            self.assertIn(new_msg.text, self.testuser.likes)
        

    def test_display_likes(self):
        """Can we show all of the likes from the test user?"""
        new_msg = Message(text="New message", timestamp="2022-07-22 00:01:21.372552", user_id = self.testuser.id)
        self.testuser.likes.append(new_msg)
        db.session.commit()

        with self.client as client:
            resp = client.get(f'/users/{self.testuser.id}/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(new_msg, self.testuser.likes)
            self.assertIn(f'<p>{new_msg.text}</p>',html)

#Test if a user that testuser is following can be displayed

    def test_display_following(self):
        newer_user = User.signup(username="newuser",
                                    email="newtest@newtest.com",
                                    password="newuser",
                                    image_url=None)
        self.testuser.following.append(newer_user)
        db.session.commit()

        with self.client as client:
            resp = client.get(f'users/{self.testuser.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(newer_user, self.testuser.following})
            #Check if the newer_user that testuser is following appears in the html
            self.assertIn(f'<p>@{newer_user.username}</p>', html)


#Test if a user can be displayed as one of testusers followers

    def test_display_followers(self):
        newest_user = User.signup(username="newestuser",
                                    email="newesttest@newesttest.com",
                                    password="newestuser",
                                    image_url=None)

        self.testuser.followers.append(newest_user)
        db.session.commit()
        with self.client as client:
            resp = client.get(f'/users/{self.testuser.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(newer_user.username, self.testuser.followers)
            self.assertIn(f'<p>@{newest_user.username}</p>', html)


#Test if a user can be added to testusers followers
    def test_add_follower(self):
        evennewer_user = User.signup(username="evenneweruser",
                                    email="evennewertest@evennewertest.com",
                                    password="evenneweruser",
                                    image_url=None)

        self.testuser.following.append(evennewer_user)
        db.session.commit()

        with self.client as client:
            resp = client.post(f'/users/follow/{evennewer_user.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn(evennewer_user.username, self.testuser.following)
            self.assertIn(f'<p>@{followed_user.username}</p>', html)
    
    def test_stop_following(self):
        newnew_user = User.signup(username="newnewuser",
                                    email="newnewuser@newnewtest.com",
                                    password="newnewuser",
                                    image_url=None)
        self.testuser.following.append(newnew_user)
        db.session.commit()

        with self.client as client:
            resp = client.post(f'/users/stop-following/{newnew_user.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn(f'<p>@{newnew_user.username}</p>', html)
            self.assertNotIn(newnew_user.username, self.testuser.username)

    def test_edit_profile_get(self):
"""Testing the edit profile page initial display"""
        with self.client as client:
            resp = client.get(f'/users/profile')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<input class="form-control" id="username" name="username" placeholder="Username" required="" type="text" value="">', html)

#Test the creation of a new user being passed as a form 
#Need to confirm how to send the post request with the form
    # def test_edit_profile_post(self):
    #     """Testing the edit profile page submission"""
    #     form = UserEditForm(username="anotherusername", password="newpassword", email="dudebro@jasonmail.com", image_url="http://www.google.com", header_image_header="http://www.google.com", bio="NewBioHere")
        

    #     with self.client as client:
    #         resp = client.post(f'/users/profile', follow_redirects=True, data={form})
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertIn("otheruser", html)
    def test_delete_profile(self):
        last_user = User.signup(username="lastuser",
                                    email="lasttest@lasttest.com",
                                    password="lastuser",
                                    image_url=None)
        with self.client as client:
            resp = client.post(f'/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
        
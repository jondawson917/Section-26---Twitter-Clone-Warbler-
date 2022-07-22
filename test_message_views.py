"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest test_message_views.py


import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, connect_db, Message, User


db.create_all() 

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)


        db.session.commit()
    
    def tearDown(self):
        """Clean up any fouled commit() transaction."""

        db.session.rollback()
#Test the messages view function messages_add

    def test_add_message_get(self):
        """Can we display the add message during GET request"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-success btn-block">Add my message!</button>', html)



    def test_add_message_post(self):
        """Can add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            

            resp = c.post("/messages/new", data={"text": "Hello"})

           
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

#Test the messages view function messages_show
    
    def test_show_messages(self):
        """Can we show a message by its ID"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            new_msg = Message(text="Yo yo!", timestamp="2022-07-22 00:01:21.372552", user_id = self.testuser.id)

            #-Add dummy message to the test database
            db.session.add(new_msg)
            db.session.commit()

            resp = c.get(f'/messages/{new_msg.id}')

            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            msg = Message.query.one()
            
            self.assertIn('<p class="single-message">Yo yo!</p>', html)
            self.assertEqual(msg.text, "Yo yo!")
            
            db.session.delete(new_msg)


#Test the delete view function 'messages_destroy'
    
    def test_messages_delete(self):
        """Can we delete a message? Remove from test database"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            #Setup dummy message
            new_msg = Message(text="New message", timestamp="2022-07-22 00:01:21.372552", user_id = self.testuser.id)
            
            #-Add dummy message to the test database
            db.session.add(new_msg)
            db.session.commit()
            
            resp = c.post(f"/messages/{new_msg.id}/delete")
            #Ensure that the 
            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertNotIn("New message", html)
            #Delete the dummy message from the test database

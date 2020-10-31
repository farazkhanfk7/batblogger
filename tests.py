import unittest
from blog import app,db
from blog.models import User, Post
from blog.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        self.assertEqual([user1],User.query.filter_by(username="test").all())
        self.assertEqual(user1,User.query.get(1))

    def test_create_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(post1,Post.query.get(1))

    def test_users_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(user1.posts,[post1])

    def test_main_page(self):
        with app.test_client() as c:
            response = c.get('/')
            self.assertEquals(response.status_code, 200)
        

if __name__ == '__main__':
    unittest.main()
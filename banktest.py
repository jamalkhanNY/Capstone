import unittest
from flask_testing import TestCase
from __init__ import app , mysql


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('insert into users (name,email,password,role,number,balance) values(%s,%s,%s,%s,%s,%s)',
                       ('admin','admin@admin.com','pbkdf2:sha256:260000$GlEDNmg6ACNFNjjT$1f211420ce4dbfaa65e623f5c8472bc1981a5f26bacf490bfe5fee9cc2e2f7e1','Admin','012345567',0))
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('delete from users where email="admin@admin.com"')
        conn.commit()
        cursor.execute('delete from users where email="flask@testing.com"')
        conn.commit()
        conn.close()

class FlaskAppTestCase(BaseTestCase):
    def test_login_page(self):
        response =  self.client.get('/login',content_type='html/text')
        self.assertEqual(response.status_code,200)

    def test_login_page_loads(self):
        response =  self.client.get('/login',content_type='html/text')
        self.assertTrue(b'Login to Your Account' in response.data)

    def test_user_register(self):

        response =  self.client.post('/register',
                                data=dict(
                                    name = 'Flask Testing',
                                    email='flask@testing.com',
                                    password='qaz',
                                    cpassword='qaz',
                                    number='012345678',

                                ), follow_redirects= True)
        self.assertTrue(b'User Flask Testing Add Successfully..' in response.data)

    def test_correct_login(self):

        response =  self.client.post('/login',
                                data=dict(email='test@admin.com',password='qaz'), follow_redirects= True)
        self.assertTrue(b'Welcome to Banking.' in response.data)

    def test_incorrect_login(self):

        response =  self.client.post('/login',
                                data=dict(email='test@admin.com',password='abc'), follow_redirects= True)
        self.assertTrue(b'Invalid password.' in response.data)

    def test_logout(self):

        response =  self.client.post('/login',
                                data=dict(email='test@admin.com',password='abc'), follow_redirects= True)
        response = self.client.get('/logout', follow_redirects= True)
        self.assertTrue(b'Enter your email & password to login' in response.data)

    def test_main_login(self):

        response =  self.client.get('/', follow_redirects= True)
        self.assertTrue(b'Enter your email & password to login' in response.data)


    def test_dashboard_(self):
        response =  self.client.post('/login',
                                data=dict(email='test@admin.com',password='qaz'), follow_redirects= True)
        self.assertTrue(b'Recent Transitions' in response.data)

    def test_deposit(self):
        self.client.post('/login',data=dict(email='test@admin.com',password='qaz'), follow_redirects= True)
        response = self.client.post('/deposit?action=add',
                                   data=dict(
                                       amount=100,
                                       type='testing deposit',
                                       description = 'testing a deposit from cli',
                                   ), follow_redirects= True)
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'You are credited 100 successfully .!' in response.data)

    def test_withdraw(self):
        self.client.post('/login', data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response = self.client.post('/withdraw?action=add',
                                    data=dict(
                                        amount=100,
                                        type='testing withdraw',
                                        description='testing a withdraw from cli',
                                    ), follow_redirects=True)
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'You are debited 100 successfully .!' in response.data)

    def test_profile(self):
        self.client.post('/login',
                         data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response =  self.client.get('/profile',content_type='html/text')
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'Profile Details' in response.data)


    def test_transitions(self):
        self.client.post('/login',
                         data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response = self.client.get('/transitions', content_type='html/text')
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'Transitions' in response.data)

    def test_settings(self):
        self.client.post('/login',
                         data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response = self.client.get('/settings', content_type='html/text')
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'Users' in response.data)

    def test_settings_add_user(self):
        self.client.post('/login',
                         data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response = self.client.post('/settings?action=add',
                         data=dict(
                             name='Flask Testing 2',
                             email='flask2@testing.com',
                             password='qaz',
                             cpassword='qaz',
                             number='012345678',
                             role='User'
                         ), follow_redirects=True)
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'User Flask Testing 2 Add Successfully..' in response.data)

    def test_settings_delete_user(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('select id from users where email="flask2@testing.com"')
        data =  cursor.fetchall()
        conn.close()
        userid = data[0][0]
        # print(userid)
        self.client.post('/login',
                         data=dict(email='test@admin.com', password='qaz'), follow_redirects=True)
        response = self.client.post('/settings?action=delete&id='+str(userid), follow_redirects=True)
        self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'User delete Successfully.' in response.data)


if __name__ == '__main__':
    unittest.main()


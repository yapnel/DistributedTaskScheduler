from ldap3 import Server, Connection, ALL
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
from my_app import app, db
import keyring
 
def get_ldap_connection(username, password):
    server = Server('DOMAIN', get_info=ALL) 
    try:
        conn = Connection(server, 'CN='+username+',DC=domain,DC=domain,DC=net', password, auto_bind=True)
    except Exception as e:
        print('Exception ' + e)
    return conn
  
class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    
 
    def __init__(self, username, password):
        self.username = username
 
    @staticmethod
    def try_login(username, password):
        
        conn = get_ldap_connection(username, password)
        franchise='FRANCHISE'
        ADGroup='AD_*_GROUP'
        ADGroup=ADGroup.replace('*', franchise)       
        searchFilter = '(&(objectClass=user)(sAMAccountName='+username+')(memberof=CN='+ADGroup+',DC=domain,DC=domain,DC=net))'
        searchBase='OU=desktop,DC=domain,DC=domain,DC=net'
        
        auth=conn.search(searchBase, searchFilter)    
        if(auth):
            conn.unbind()
        else:
            raise Exception(racfid + ' is forbidden')


    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)    
 
 
class LoginForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])

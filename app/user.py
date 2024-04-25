from flask_login import UserMixin
from app import login
from app.queries.users import query_get_user_data
import sys


class User(UserMixin):
    def __init__(self, user_id = None, name = None, last_name = None, email = None, role = None, phone = None, status = True) -> None:
        self.user_id = user_id
        self.email = email
        self.name = name
        self.last_name = last_name
        self.role = role
        self.phone = phone
        self.status = status
        
    def get_id(self):
        return str(self.user_id)
    
@login.user_loader
def load_user(user_id):
    user_data = query_get_user_data(user_id=user_id)
    print(user_data, file=sys.stderr)
    return User(user_id, user_data['name'], user_data['last_name'], user_data['email'], user_data['role'], user_data['phone'])
    
    
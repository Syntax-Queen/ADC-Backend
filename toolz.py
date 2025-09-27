import random
import re
import string

def validate_email(email):
    if email is None:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False
import hashlib

def hash_password(password):
    hashed_pss = hashlib.sha256(password.encode()).hexdigest()
    return hashed_pss


def validate_rut_struct(rut):
    dash = False
    for i in rut.data:
        if i == '.':
            return False
        if i == '-':
            dash = True
    if dash == False:
        return False
    return True

def validate_rut(rut):
    number, validator = rut.split('-')
    number = number[::-1]
    factors = [2,3,4,5,6,7]
    factor_index = 0
    totals = list()
    for i in number:
        val = int(i)*factors[factor_index]
        totals.append(val)
        factor_index += 1
        if factor_index >= 6:
            factor_index = 0

    total_sum = 0
    for num in totals:
        total_sum += num
        
    control = 11-(total_sum%11)

    if control < 10:
        if int(validator) == control:
            return(True)
        else:
            return(False)
    elif control == 11:
        if validator == '0':
            return(True)
        else:
            return(False)
    elif control == 10:
        if validator == 'K' or validator == 'k':
            return(True)
        else:
            return(False)
    else:
        return(False)
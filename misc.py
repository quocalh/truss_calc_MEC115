
"""
k = 1 => 'A'
k = 28 => 'AB'
"""
ALPHA_NAME_COUNTER = 1
# 26 based numeric system
def get_alpha_name(counter = None):
    global ALPHA_NAME_COUNTER 

    if counter is None:
        k = ALPHA_NAME_COUNTER
        ALPHA_NAME_COUNTER += 1
    else:
        k = counter

    if k <= 0:
        return ""

    k -= 1
    char = chr(65 + ((k) % 26))
    return get_alpha_name(k // 26) + char # prev + cur

FORCE_COUNTER = 1
def get_force_name(counter = None):
    global FORCE_COUNTER

    if counter is not None:
        pass
    else:
        counter = FORCE_COUNTER
        FORCE_COUNTER += 1

    name  = "F" + str(counter)
    counter += 1
    return name
"""
print(get_name(28)) # AB
print(get_name(26 + 26 + 2)) # AB
print(get_name(1)) # A
"""


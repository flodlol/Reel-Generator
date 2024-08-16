import os
import binascii

secret = binascii.hexlify(os.urandom(32)).decode()
print(secret)

# c452d8ba6711f0f88ecdad319dac8b44f43945ce3a17b17cbedba4a723124c21
# MeowChiefShow1!
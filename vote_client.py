import socket

from util import Settings

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        return response
    finally:
        sock.close()

def parse_keys(keycollection):
    #Each element is a comma separated string in the form n,e
    parsed_keys = []
    for key in keycollection:
        data = key.split(',')
        name = data[0]
        n, e = map(long, data[1:])
        parsed_keys.append((name, (n, e)))

    return parsed_keys

if __name__ == "__main__":
    #Generate the random votes
    votes = Settings.generate_rand_votes(count=10)
    #Retrieve the public keys of each mix server
    public_keys = []
    mix_count = Settings.mix_count()
    for i in range(1, mix_count+1):
        HOST, PORT = Settings.host_info('Mix{}'.format(i))
        response = client(HOST, PORT, 'get-pk')
        public_keys.append(response)
        client(HOST, PORT, 'vote-count-{}'.format(len(votes)))
    public_keys = parse_keys(public_keys)

    #We have the public keys, now we can construct the appropriate RSA keys
    RSAkeys = []
    for key in public_keys:
        print 'Client: Constructing key from {}'.format(key[0])
        RSAkeys.append(RSA.construct(key[1]))
    RSAkeys.reverse()

    #Encrypt each vote with the keys in reverse order
    #The encryption chain is illustrated below:
    #RSA->RSA->PKCS1_OAEP(rsa)
    #PKCS1_OAEP is used to add randomness in the vote
    print 'Votes:{}'.format(','.join(votes))
    encrypted_votes = []

    for i, v in enumerate(votes):
        print 'Encrypting vote #{}'.format(i+1)
        cipher = PKCS1_OAEP.new(RSAkeys[0])
        result = (cipher.encrypt(v),)
        for key in RSAkeys[1:]:
            #The random(last) parameter is unused
            result = key.encrypt(result[0], 0)
        encrypted_votes.append(result[0])

    #Votes are encrypted, send them to the bulletin board
    #in order to notify the first mixnet
    HOST, PORT = Settings.host_info('BulletinBoard')
    #Notify the bulletin board how many votes it should expect
    client(HOST, PORT, 'vote-count-{}'.format(len(votes)))
    #Send the encrypted votes to the bulletin board
    print 'Sending votes to the bulletin board...'
    for v in encrypted_votes:
        client(HOST, PORT, v)
    print 'Client done sending!'

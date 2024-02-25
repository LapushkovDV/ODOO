import requests

triaflyURL = 'http://194.169.192.155:55556'
triaflyAPI_KEY = '8EBEA456a6'
triaflyUser = 'admin'
triaflyPswd = 'Zraeqw123'
triaflyRegistr = '471971'

_rqst = '{0}/api/3/registry/{1}/'.format(triaflyURL,triaflyRegistr)

print(_rqst)
_resRqst = requests.get(_rqst,
    params={'user': '{0}:{1}'.format(triaflyUser, triaflyPswd)},
    headers={'Netdb-Api-Key': '8EBEA456a6'}
                        )
print(_resRqst.json())
print(_resRqst)

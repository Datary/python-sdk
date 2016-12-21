Datary SDK for Python

```
pip install datary
```

# Generate docs
Documentation powered by sphinx.
```
cd docs && make docs OUTPUT_FORMAT
```

# Usage

Example to retrieve Datary repository info
```
from datary import Datary

# init Datary class using username&password or token
d = Datary(username='test_user', password='test_password')
# d = Datary(token='test_token')

# return repo description asociated to the name introduced and to the account.
repo = d.get_describerepo(repo_name='test_repo_name')

```
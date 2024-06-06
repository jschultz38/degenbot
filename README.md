# Description
Fetch game times for select degenz

# Commands
!help

# Setup

To install required modules: 
```
pip install -r requirements.txt
```
It's good practice to avoid uploading credentials to github, so I've included
them in a file called credentials.py and added it to the gitignore. If you
would like to get this running on your machine, create a file that looks like
this:

```
prod_token = 'prod_token_here'
test_token = 'test_token_here'
```
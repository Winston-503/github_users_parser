# Parse GitHub users based on location and keywords
## Useful application of PyGithub library for HR specialists

| ![preview.jpg](./img/preview.jpg) |
|:--:|
| <b>Preview. Image by Author</b>|

One of my good friend works as an HR specialist. He communicates with candidates, conducts interviews, and has many more other responsibilities, but sometimes he has to manually search for candidates for a certain position.

Recently, he turned to me with a request: "Hey, you can definitely write a program that will parse GitHub and output some users for me according to the hiring position. It will help me a lot. It's definitely more efficient and faster than searching manually!"

Well, let's try it.

## GitHub Search API

First of all, it should be said that GitHub has a fairly rich search functionality. Even without third-party libraries using directly [GitHub search API](https://docs.github.com/en/rest/reference/search), you can get a lot of information. But libraries like [PyGithub](https://pygithub.readthedocs.io/en/latest/introduction.html) take on the subtleties of working with the API. 

If you don't use Python, as I will, you can find some libraries for other languages [here](https://docs.github.com/en/rest/overview/libraries). There are a lot of libraries, so you will definitely choose one for your favorite language - .NET, Java, JavaScript, PHP, or even Go, Julia and Scala and many others.

## Essence of the Program

In fact, this article can be finished right now. I spent most of my time trying to figure out the format of the request and find the right library. Then everything goes like clockwork.

Let me explain the functionality of the program using a good old flowchart. It is very high-level and misses a lot of details, but it will do to understand what is happening.

| ![flowchart.jpg](./img/flowchart.jpg) |
|:--:|
| <b>Essence of the program. Image by Author</b>|

Why not just stop at the very first step? Because search API does not allow you to specify keywords in request for user search. For example programming language can be specified, but setting Python in the request you will get Python backend developers and Python ML engineers in one response, that mixes a lot of positions into one pile. I'll talk about this in more detail in the **Parameters** section.

First we need to get information about users using some kind of request. It seems to me the most convenient way to do this is by using a query of the form `location:... language:...`, although the search API allows you to set much more complex queries.

Going through the received list, we look at the repositories of each user for the presence of any keyword in them. The search is performed in the name and description of the repository, although you can also add a content of the README.md file here. If any keyword was found in any user repository, this user is added to the resulting table - information about him is saved, and the search continues further.

In case of unexpected errors or when the desired number of users is reached, the information is saved to a .xlsx or .csv file using pandas library.

```python
# the following variables are set
# query (str): query without keywords
# keywords (list of str): list of keywords to search
# max_count (int): the desired number of users to get
# filename (str): filename to save resulting data including extension (.xlsx or .csv)
# g = Github(access_token)

from github import Github

users = []
count = 0

# for all users from the request response
for user in g.search_users(query=query):
    try:
        # at least one of repos contains a keyword
        for repo in user.get_repos():
            # form repo_string as repo name and description
            description_str = repo.description if repo.description else ''
            repo_string = repo.name + ' ' + description_str

            # if any keyword is contained in any users repository
            if any(keyword in repo_string for keyword in keywords):
                # add this user in the result table
                add_to_users(user, repo)
                count += 1
                print(f"{count}/{max_count} - add {user.name}")
                # go to the next user
                break

    except Exception as e:
        print("An error occurred while executing the query")
        print("Error: " + str(e))
        save_users(filename)

    if count == max_count:
        save_users(filename)
```

In the repository, this code is wrapped in a class, but the main method of the class `parse_users()` does exactly what is described above. Feel free to experiment with this code to add more flexibility or functionality. Let me know if this will grow into a big project :)

## More About Parameters

The program has 6 parameters that must be set: `is_path`, `token_or_path`, `max_count`, `filename_to_save`, `query` and `keywords_list`. Let's examine each of them in more detail.

A pair of parameters `is_path` and `access_token_path` set your GitHub token. To get it, register GitHub account and go to [tokens page in settings](https://github.com/settings/tokens). Click on **Generate new token**, confirm your password, write anything in **Note** field, select some of the **Expiration** option, click **Generate token** at the bottom of the page and copy your token. Note, that each token has expiration period and the program will not work with expired token. GitHub will mail you a few days before expiration so make sure you create new token or choose **No expiration** option. Then:
- if `is_path`=True, `token_or_path` must be path to .txt file containing access token;
- if `is_path`=False, `token_or_path` must be access token

`max_count` parameter is an integer number that set **the desired number of users to get**. This number is equal to the count of rows that the result table will contain.

`filename_to_save` parameter set filename to save resulting data including extension. Data is saved in Microsoft Excel format (.xlsx) or as comma separated values (.csv).

A pair of parameters `query` and `keywords_list`

You can see examples of different queries below.

```python
import pandas as pd
from github import Github

# class GitHubUsersParser: { ... }

# shared parameters
token_or_path = "ghp_Re4dzGv5a5WQNffbNXRY2gASYLaE26h8CVjZc"
is_path = False
max_count = 5
filename_to_save = 'users.csv'

# Examples of different queries

# 1. Python backend developer from USA
query = "language:python location:USA"
keywords_list = ['backend', 'django', 'flask']

# 2. Python/C++ computer vision engineer
# first query with
query = "language:python"
# then second with
query = "language:C++"
keywords_list = ['computer vision', 'opencv']

# 3. PHP developer from India with more than 100 followers
query = "language:PHP location:India followers:>100"
keywords_list = []

# and so on ... 

# create class instance using access token
github_parser = GitHubUsersParser(token_or_path, is_path)

# parsing with set parameters
github_parser.parse_users(query=query,
                            keywords=keywords_list,
                            max_count=max_count,
                            filename=filename_to_save)
```

## Running Program



## Conclusions

Approximately 3 seconds for a user. Of course, it greatly depends on your Internet connection, the complexity of your request, etc.

## Useful Resources

- Advanced GitHub search to form a right query - https://github.com/search/advanced
- Searching for information on GitHub - https://docs.github.com/en/search-github
- PyGithub documentation - https://pygithub.readthedocs.io/en/latest/introduction.html

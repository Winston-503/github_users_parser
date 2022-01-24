# How to parse GitHub users based on location and multiple keywords
## A useful application of PyGithub library for HR specialists

| ![preview.jpg](./img/preview.jpg) |
|:--:|
| <b>Preview. Image by Author</b>|

One of my good friends works as an HR specialist. He communicates with candidates, conducts interviews, and has many other responsibilities, but sometimes he has to manually search for candidates for a certain position.

Recently, he turned to me with a request: "Hey, you can definitely write a program that will parse GitHub and output some users according to the hiring position for me. It will help me a lot. It's definitely more efficient and faster than searching manually!"

Well, let's try it.

## GitHub Search API

First of all, it should be said that GitHub has fairly rich search functionality. Even without third-party libraries using directly [GitHub search API](https://docs.github.com/en/rest/reference/search), you can get a lot of information. But libraries like [PyGithub](https://pygithub.readthedocs.io/en/latest/introduction.html) take on the subtleties of working with the API - they return classes instead of raw JSON, monitor the number of returned elements, and do a lot of other useful work.

If you don't use Python, as I will, you can find some official or third-party libraries for other languages here. There are a lot of them, so you will definitely choose one for your favorite language: .NET, Java, JavaScript, PHP, or even Go, Julia or Scala, and many many others.

| ![languages.jpg](./img/languages.jpg) |
|:--:|
| <b>Plenty of programming languages you can use. Image by Author</b>|

## The Essence of the Program

In fact, this article can be finished right now. I spent most of my time trying to figure out the format of the request and find the right library. Then everything goes like clockwork.

Let me explain the functionality of the program using a good old flowchart. It is very high-level and misses a lot of details, but it will do to understand what is happening.

| ![parser_flowchart.png](./img/parser_flowchart.png) |
|:--:|
| <b>The essence of the program. Image by Author</b>|

First, we need to get information about users using some kind of request. It seems to me that the most convenient way to do this is by using a query of the form `location:... language:...`, although the search API allows you to set much more complex queries. We will talk more about constructing queries later, in the **Parameters** section.

Going through the received list, we look at the repositories of each user for the presence of any keyword in them. The search is performed in the name and description of the repository, although you can also add the content of the `README.md` file here. If any keyword was found in any user repository, this user is added to the resulting table - information about him is saved, and the search continues further.

In case of unexpected errors or when the desired number of users is reached, the information is saved to a .xlsx or .csv file using [pandas library](https://pandas.pydata.org/docs/getting_started/index.html).

Why not just stop at the very first step? Because search API does not allow you to specify keywords in the user search request. In fact, you can, but this will produce much worse results according to my experiments.

For example, you can specify a programming language, but by setting *Python* in the request you will get *Python backend developers* and *Python ML engineers* in one response, which mixes a lot of positions into one pile. I'll talk about this in more detail in the **Parameters** section.

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
- if `is_path`=False, `token_or_path` must be access token directly.

`max_count` parameter is an integer number that set **the desired number of users to get**. This number is equal to the count of rows that the result table will contain.

`filename_to_save` parameter set filename to save resulting data including extension. Data is saved in Microsoft Excel format (.xlsx) or as comma separated values (.csv).

A pair of parameters `query` and `keywords_list` sets purpose of the parsing - a combination of these parameters defines program output.
- `keywords_list` is a Python list that contains different keywords to search. You can add as many keywords as you want, or don't add any;
- `query` is a search query according to GitHub search API.

It is formed according to certain rules and can specify:
- location of a user;
- limits on the number of followers or public repositories;
- and programming language.

You can also specify a name, but I don't think it makes any sense. You can verify this by examining the [advanced search page](https://github.com/search/advanced) and the [official GitHub documentation](https://docs.github.com/en/search-github/searching-on-github/searching-users).

| ![users_options.jpg](./img/users_options.jpg) |
|:--:|
| <b>Users options. Screenshot of a [public web page](https://github.com/search/advanced)</b>|

The most logical and widely used query format for this task, as I said above, is to specify a location and language. But as you can see, the API allows you to create much more powerful queries.

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

The program is available in [this GitLab repository](https://gitlab.com/Winston-90/github_users_parser).

https://gitlab.com/Winston-90/github_users_parser

Among other auxiliary files, this repository contains Python script `github_parser.py` and `guthub_parser.ipynb` notebook. They have the same content, so you can run this program using a command prompt or Jupyter notebook.

For simplicity, I advise you to run this program as a regular Python script. If you don't know how to do that, check [this tutorial](https://realpython.com/run-python-scripts/). In fact, all you need to do is a few simple steps:

1. Make sure you have Python and needed libraries installed. Otherwise, [install Python](https://www.python.org/downloads/) and install the libraries:
- You should create a virtual environment (although this is not mandatory), activate it, and run `pip install -r requirements.txt`.
- You can also install these libraries using conda or pip directly. You can see the list of libraries in the `requirements.txt` file.
2. Open `github_parser.py` file with any text editor and set your parameters in the **Setting parameters** section, on **lines 218–246**. Remember that you have to specify the access token as said earlier. Don't forget to save the file.
3. Then run the program with `python github_parser.py` command.

Having set your environment and the valid access token, without changing other parameters,  you will see something like the following on your command line:

| ![script.jpg](./img/script.jpg) |
|:--:|
| <b>The result of the script execution with default parameters. Image by Author</b>|

By opening the `data/users.xlsx` file you will see the following content:

| ![result_table.jpg](./img/result_table.jpg) |
|:--:|
| <b>The output of the program with default parameters. Image by Author</b>|

It can be quickly turned into a more attractive version. Create a table using **Ctrl+T** shortcut and set column width using **Main - Format - AutoFit Column Width** (in some versions of Excel, this happens automatically, in some, it does not).

| ![table.gif](./img/table.gif) |
|:--:|
| <b>Make your table more attractive. Gif by Author</b>|

After these simple transformations, you get a table ready to work. The fields of this table are self-explanatory.

| ![result_table_pretty.jpg](./img/result_table_pretty.jpg) |
|:--:|
| <b>Result table. Image by Author</b>|

Of course, some users do not specify the data about themselves and each row in the table requires special attention, but as I said earlier, it is much better than searching manually.

About the execution time - it takes approximately 3 seconds for a user. Of course, it greatly depends on your Internet connection, the complexity of your request, etc.

## Conclusions

I was faced with this task absolutely not knowing how to solve it, but after a few days, I already had a prototype of a working program. I am happy with the result and I think it can be useful to you.

###  Resources that can be useful for you

- Advanced GitHub search to form a right query - https://github.com/search/advanced
- Searching for information on GitHub - https://docs.github.com/en/search-github
- PyGithub documentation - https://pygithub.readthedocs.io/en/latest/introduction.html

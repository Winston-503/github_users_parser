# github parser

# Imports

import requests
from github import Github
import pandas as pd

# Helper functions

def get_repos(access_token, query, keywords, max_count=1000):
    """
    Get information about repositories based on 'keywords' and query
    each time forming a query like: 'current_keyword' + 'query'

    Parameters:
        access_token (str): GitHub access token
        query (str): query for search without keywords
        keywords (list of strings): keyword to search
        max_count (int): count of requests for each keyword

    Returns:
        pd.DataFrame with columns ['keyword', 'name', 'username', 'html_url', 'language']
            contains len(keywords) * max_count rows or less 
    """

    # list of dict with columns
    # ['keyword', 'name', 'username', 'html_url', 'language']
    repos = []

    g = Github(access_token)

    for keyword in keywords:
        print(f"\n\tProcessing {keyword}")
        search_results = g.search_repositories(query=keyword + " " + query)

        for i, repo in enumerate(search_results):

            # accumulate data into list
            repo_info = {'keyword': keyword,
                         'name': repo.name,
                         'language': repo.language,
                         'html_url': repo.html_url,
                         'username': repo.owner.login}
            repos.append(repo_info)

            print(f"{keyword} - {i+1}")
            if i+1 == max_count:
                break

    print("\n\tDone with getting repos")

    repos_df = pd.DataFrame(repos, columns=['keyword', 'name', 'username',
                                            'html_url', 'language'])

    return repos_df


def get_unique_usernames(repos_df):
    """ Return list of unique usernames """
    
    return repos_df['username'].unique().tolist()


def get_users_table(access_token, logins):
    """ Get information about all users and return a DataFrame """

    # list of dict with columns
    # ['html_url', 'name', 'company', 'location', 
    # 'email', 'hireable', 'public_repos', 'followers']
    users = []

    for login in logins:
        g = Github(access_token)

        user = g.get_user(login)

        # get one row for result table and add it to the list
        user_info = {# 'html_url': user.html_url,
                     'html_url':f'=HYPERLINK("{user.html_url}", "{user.html_url}")',
                     'name': user.name,
                     'company': user.company,
                     'location': user.location,
                     'email': user.email,
                     'hireable': user.hireable,
                     'public_repos': user.public_repos,
                     'followers': user.followers}
        users.append(user_info)

    users_df = pd.DataFrame(users, columns=['html_url', 'name', 'company',
                                            'location', 'email', 'hireable',
                                            'public_repos', 'followers'])

    return users_df


def filter_users_by_location(df, locations):
    """ Filter full_users DataFrame with locations """

    # drop NaN values from location column
    df.dropna(subset=["location"], inplace=True)

    return df[df['location'].str.contains('|'.join(locations))]


def save_info(repos_df, repos_filename,
              full_users_df, full_users_filename,
              users_df, users_filename):
    """ Save three dataframes into excel files """

    if repos_filename:
        repos_df.to_excel(repos_filename, index=False)

    if full_users_filename:
        full_users_df.to_excel(full_users_filename, index=False)

    if users_filename:
        users_df.to_excel(users_filename, index=False)


# Setting parameters
########################################################################################################

access_token_path = 'data/access_token.txt'

try:
    f = open(access_token_path, 'r')
except OSError:
    print(f"Could not open/read file: {access_token_path}.")
    print("Specify the path to file, containing your GitHub access token.")
    print("To know more, visit: https://github.com/settings/tokens")

with f:
    access_token = f.read()

# query without keywords
# see https://github.com/search/advanced
query = "language:python"

# python list of keywords to search
# ['keyword1', 'keyword2', 'keyword3']
keywords_list = ['ml', 'machine learning']

# count of requests for each keyword
max_count = 5

# locations to filter users
locations = ['China', 'Brooklyn', 'Amsterdam']

# filenames to save dataframes
# False if no need to save
repos_filename = 'data/repos.xlsx'
full_users_filename = False
users_filename = 'data/users.xlsx'

########################################################################################################


# Main program
def main():

    # Get information about repos
    print('Getting information about repos...')
    repos_df = get_repos(access_token=access_token, query=query,
                        keywords=keywords_list, max_count=max_count)

    print(f"Got {repos_df.shape[0]} rows in repos_df DataFrame")

    print('Getting unique usernames...')
    usernames = get_unique_usernames(repos_df)
    print(f"Got {len(usernames)} unique users")

    # Get information about users
    print('Getting information about users...')
    full_users_df = get_users_table(access_token=access_token, logins=usernames)
    print(f"Got {full_users_df.shape[0]} rows in full_users_df DataFrame")
    full_users_df

    print('Filtering users by locations...')
    users_df = filter_users_by_location(full_users_df, locations)
    print(f"Got {users_df.shape[0]} rows in users_df DataFrame")

    print('Saving information...')
    save_info(repos_df, repos_filename,
            full_users_df, full_users_filename,
            users_df, users_filename)

    print("Information saved. Check your 'data' folder...")

if __name__ == '__main__':
    main()




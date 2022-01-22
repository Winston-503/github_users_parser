# GitHub users parser
# originally published in https://gitlab.com/Winston-90/github_users_parser

# Imports
import pandas as pd
from github import Github


# GitHubUsersParser() class
class GitHubUsersParser:
    """ 
    A class that represents parser to get information about GitHub users
    Create an instance of the class by providing information about your token
    and call parse_users() method with needed parameters

    >>> gup = GitHubUsersParser(token, is_path=False)
    >>> gup.parse_users(...)

    See methods documentation for more information
    """

    def __init__(self, token_or_path, is_path=True):
        """ 
        Create PyGithub Github() object to request information

        Parameters:
            token_or_path (str): access token or path to .txt file 
                that contains it.
                To get the token, visit: https://github.com/settings/tokens
            is_path (bool): if true, 'token_or_path' must be path
                to .txt file containing access token.
                If false 'token_or_path' must be access token
        """

        # array of dict with fields:
        # ['repo_html_url', 'repo_language', 'user_html_url', 'name', 'company',
        #  'location', 'email', 'hireable', 'public_repos', 'followers']
        self.users = []

        if not is_path:
            access_token = token_or_path
        else:
            # reading text file
            try:
                f = open(token_or_path, 'r')
                access_token = f.read()
            except OSError:
                print(f"Could not open/read file: {token_or_path}.")
                return

        print("Your access token was successfully read")
        self.g = Github(access_token)

        # test query to check if token is correct
        try:
            repo = self.g.get_repo("PyGithub/PyGithub")
        except Exception as e:
            print("An error occurred while executing the test query.\n" +
                  "Most likely your token is incorrect or expired.")
            print("Error: " + str(e))
            return

        print("The test request was successfully executed")

    def __add_to_users(self, user, repo):
        """
        Private method to append information about 'user' and 'repo'
        into 'users' list

        Parameters:
            user (PyGithub NamedUser): user object received
                for example using g.get_user()
            repo (PyGithub Repository): repository object received
                for example using g.get_repo()
        """

        data = {'repo_html_url': repo.html_url,
                'repo_language': repo.language,
                'user_html_url': user.html_url,
                'name': user.name,
                'company': user.company,
                'location': user.location,
                'email': user.email,
                'hireable': user.hireable,
                'public_repos': user.public_repos,
                'followers': user.followers}

        self.users.append(data)

    def __save_users(self, filename, test=False):
        """
        Private method to save information about 'users' into file

        Parameters:
            filename (str): filename to save including extension (.xlsx or .csv)
            test (bool): if True provide test save to check that filename is valid

        Returns:
            -1 if an error occurred while saving the file,
            otherwise - None
        """

        if filename[-3:] == 'csv':
            to_csv = True
        elif filename[-4:] == 'xlsx':
            to_csv = False
        else:
            print("Unsupported file format. " +
                  "'filename_to_save' must have an .xlsx or .csv extension")
            return -1

        if test:
            try:
                if to_csv:
                    pd.DataFrame().to_csv(filename, index=False)
                else:
                    pd.DataFrame().to_excel(filename, index=False)
            except Exception as e:
                print("An error occurred while saving a file.\n" +
                      "Check 'filename_to_save'.")
                print("Error: " + str(e))
                return -1

            print("The test saving was successfully executed.")
            return

        # define DataFrame from list of dict
        users_df = pd.DataFrame(
            self.users,
            columns=['repo_html_url', 'repo_language',
                     'user_html_url', 'name', 'company', 'location',
                     'email', 'hireable', 'public_repos', 'followers'])

        # filling missing values with space to sort Excel table
        users_df.fillna(' ', inplace=True)

        # save file
        if to_csv:
            users_df.to_csv(filename, index=False)
        else:
            users_df.to_excel(filename, index=False)

        print(f"\nData about users was saved into '{filename}' " +
              f"file ({users_df.shape[0]} rows).")

    def parse_users(self, query, keywords, max_count, filename):
        """
        Parse GitHub users with set parameters
        Save information about users into table when the number
        of users reaches the desired number or when an error occurs

        Parameters:
            query (str): query without keywords. See https://github.com/search/advanced
            keywords (list of str): list of keywords to search
            max_count (int): the desired number of users to get
            filename (str): filename to save resulting data including extension (.xlsx or .csv)
        """

        self.users = []
        count = 0

        # test saving to check that filename is valid
        if self.__save_users(filename, test=True) == -1:
            # error saving the file
            return

        if not isinstance(max_count, int) or max_count <= 0:
            print("'max_count' must be positive integer")
            return

        print("\nStart parsing with the following parameters:\n" +
              f"\tquery = '{query}'\n" +
              f"\tkeywords = {keywords}\n" +
              f"\tmax_count = {max_count}\n" +
              f"\tfilename = '{filename}'\n")

        # for all users from the request response
        for user in self.g.search_users(query=query):
            try:
                # at least one of repos contains a keyword
                for repo in user.get_repos():
                    # form repo_string as repo name and description
                    description_str = repo.description if repo.description else ''
                    repo_string = repo.name + ' ' + description_str

                    # if any keyword is contained in any users repository
                    if any(keyword in repo_string for keyword in keywords):
                        # add this user in the result table
                        self.__add_to_users(user, repo)
                        count += 1
                        print(f"{count}/{max_count} - add {user.name}")
                        # go to the next user
                        break

            except Exception as e:
                print("An error occurred while executing the query")
                print("Error: " + str(e))
                self.__save_users(filename)
                return

            if count == max_count:
                self.__save_users(filename)
                return


# Main program
def main():
    ########################################################################################################
    # Setting parameters

    # access token or path to .txt file that contains it
    # To get the token, visit: https://github.com/settings/tokens
    token_or_path = 'data/access_tokens/access_token.txt'

    # if True, 'token_or_path' must be path to .txt file containing access token
    # if False, 'token_or_path' must be access token
    is_path = True

    # or set your access token explicitly
    # token_or_path = "ghp_Re4dzGv5a5WQNffbNXRY2gASYLaE26h8CVjZc"
    # is_path = False

    # query without keywords
    # see https://github.com/search/advanced
    query = "language:python location:USA"

    # the desired number of users to get
    max_count = 5

    # list of keywords to search
    # ['keyword1', 'keyword2', 'keyword3']
    keywords_list = ['django', 'flask']

    # filename to save resulting data including extension (.xlsx or .csv)
    filename_to_save = 'data/users.xlsx'

    ########################################################################################################

    # create class instance using access token
    github_parser = GitHubUsersParser(token_or_path, is_path)

    # parsing with set parameters
    github_parser.parse_users(query=query,
                              keywords=keywords_list,
                              max_count=max_count,
                              filename=filename_to_save)


if __name__ == '__main__':
    main()

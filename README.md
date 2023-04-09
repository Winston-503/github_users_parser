# GitHub Users Parser

Search for GitHub users with multiple keywords using Python and PyGithub library

![preview.jpg](./data/preview.jpg)

## Setup and Usage

See the detailed tutorial on [Medium](https://medium.com/@andimid/how-to-parse-github-users-based-on-location-and-multiple-keywords-c08d68578c8d).

- Make sure you have Python and needed libraries installed. Otherwise, [install Python](https://www.python.org/downloads/) and install the libraries:
    - You should create a virtual environment (although it is not necessary), activate it, and run `pip install -r requirements.txt`. 
    - You can also install these libraries using conda or pip directly. You can see the list of libraries in the `requirements.txt` file.
- Open `github_parser.py` file with any text editor and set your parameters in the **Setting parameters** section, **on lines 165-194**. Remember that you have to specify the access token:
- To get it, register GitHub account and go to [tokens page in settings](https://github.com/settings/tokens). Click on **Generate new token**, confirm your password, write anything in **Note** field, select some of the **Expiration** option, click **Generate token** at the bottom of the page and copy your token. Note, that each token has expiration period and the program will not work with expired token. GitHub will mail you a few days before expiration so make sure you create new token or choose **No expiration** option. 
- Then run the program with `python github_parser.py` command.

To explore code or to make your experiments see `github_parser.ipynb` notebook. It contains the same code as python script.

## Useful links

- Advanced GitHub search to form a query - https://github.com/search/advanced
- PyGithub documentation - https://pygithub.readthedocs.io/en/latest/introduction.html
- Searching for information on GitHub - https://docs.github.com/en/search-github
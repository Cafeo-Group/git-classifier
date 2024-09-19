from github import Github
import pandas as pd
from dotenv import load_dotenv
from os import getenv

load_dotenv()
g = Github(getenv('GITHUB_TOKEN'), per_page=100)

def fetch_commits(org_name: str, repo_name: str) -> pd.DataFrame:
    organization = g.get_organization(org_name)
    repo = organization.get_repo(repo_name)
    commits = repo.get_commits()
    
    data = []
    
    for commit in commits:
        data.append({
            'id': commit.sha,
            'message': commit.commit.message
        })
    
    return pd.DataFrame(data)

def get_directories(commits: pd.DataFrame, org: str, repo: str) -> pd.DataFrame:
    commit_dirs = []
    repo = g.get_organization(org).get_repo(repo)
    
    for commit in commits.itertuples():
        directories = ''
        for file in repo.get_commit(commit[1]).files:
            file_path = file.filename
            if '/' in file_path:
                directory = '/'.join(file_path.split('/')[:-1])
                if directory not in directories:
                    directories += directory + ' '
        if directories:
            commit_dirs.append(directories)
    
    
    return pd.DataFrame(commit_dirs, columns=['directory'])

def get_pull_reqs_related_to_commits(commits: pd.DataFrame, org: str, repo: str) -> pd.DataFrame:
    repo = g.get_organization(org).get_repo(repo)
    pull_reqs = repo.get_pulls(state='all')
    
    data = []
    
    for commit in commits.itertuples():
        for pull_req in pull_reqs:
            if pull_req.merge_commit_sha == commit[1]:
                print(pull_req.merge_commit_sha,'---', commit[1])
                data.append({
                    'pull_req_id': pull_req.number,
                    'pull_req_title': pull_req.title,
                    'pull_req_body': pull_req.body
                })
        
    return pd.DataFrame(data, columns=['pull_req_id', 'pull_req_title', 'pull_req_body'])

def get_commit_messages(commits: pd.DataFrame, org: str, repo: str) -> pd.DataFrame:
    repo = g.get_organization(org).get_repo(repo)
    
    messages = []
    
    for commit in commits.itertuples():
        message = repo.get_commit(str(commit[1])).commit.message
        messages.append(message)
        
    return pd.DataFrame(messages, columns=['message'])
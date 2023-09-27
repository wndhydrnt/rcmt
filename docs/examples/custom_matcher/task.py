"""
This file demonstrates the various ways to create a Matcher.
A Matcher is a function that accepts a source.Repository as an argument
and returns a boolean.
That makes it possible to create a Matcher in multiple ways, depending
on what is needed.
All Matchers in this file do the same thing:
Match if the repository is "github.com/wndhydrnt/rcmt".
"""
from rcmt import Task
from rcmt.matcher import Base, RepoName
from rcmt.source import source


# Create a class-based Matcher by extending matcher.Base.
# matcher.Base provides helper methods, but it is not required to
# create a Matcher.
class MatcherAsClassFromBase(Base):
    def match(self, repo: source.Repository) -> bool:
        return repo.full_name == "github.com/wndhydrnt/rcmt"


# Use a callable class to create the Matcher.
# This is a vanilla Python class.
# It is recommended to extend matcher.Base as it provides some
# useful helper methods.
class MatcherAsCallableClass:
    def __call__(self, repo: source.Repository) -> bool:
        return repo.full_name == "github.com/wndhydrnt/rcmt"


# A function.
def matcher_as_function(repo: source.Repository) -> bool:
    return repo.full_name == "github.com/wndhydrnt/rcmt"


with Task(name="matcher-example") as task:
    # Use the built-in Matcher RepoName that ships with rcmt. It also
    # supports regular expressions.
    task.add_matcher(RepoName(search="github.com/wndhydrnt/rcmt"))
    # Or use the custom class that extends matcher.Base.
    task.add_matcher(MatcherAsClassFromBase())
    # Or use the vanilla class.
    task.add_matcher(MatcherAsCallableClass())
    # Use the function.
    task.add_matcher(matcher_as_function)
    # Use a lambda function.
    task.add_matcher(lambda repo: repo.full_name == "github.com/wndhydrnt/rcmt")

"""
This file demonstrates the various ways to create a Filter.
A Filter is a function that accepts a rcmt.context.Context as an argument
and returns a boolean.
That makes it possible to create a Filter in multiple ways, depending
on what is needed.
All Filter in this file do the same thing:
Match if the repository is "github.com/wndhydrnt/rcmt".
"""
from rcmt import Context, Task
from rcmt.filter import Base, RepoName


# Create a class-based Filter by extending filter.Base.
# filter.Base provides helper methods, but it is not required to
# create a Filter.
class FilterAsClassFromBase(Base):
    def filter(self, ctx: Context) -> bool:
        return ctx.repo.full_name == "github.com/wndhydrnt/rcmt"


# Use a callable class to create the Filter.
# This is a vanilla Python class.
# It is recommended to extend filter.Base as it provides some
# useful helper methods.
class FilterAsCallableClass:
    def __call__(self, ctx: Context) -> bool:
        return ctx.repo.full_name == "github.com/wndhydrnt/rcmt"


# A function.
def filter_as_function(ctx: Context) -> bool:
    return ctx.repo.full_name == "github.com/wndhydrnt/rcmt"


with Task(name="filter-example") as task:
    # Use the built-in Filter RepoName that ships with rcmt. It also
    # supports regular expressions.
    task.add_filter(RepoName(search="github.com/wndhydrnt/rcmt"))
    # Or use the custom class that extends filter.Base.
    task.add_filter(FilterAsClassFromBase())
    # Or use the vanilla class.
    task.add_filter(FilterAsCallableClass())
    # Use the function.
    task.add_filter(filter_as_function)
    # Use a lambda function.
    task.add_filter(lambda ctx: ctx.repo.full_name == "github.com/wndhydrnt/rcmt")


import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def search_results(search):
    entries = list_entries()
    search = search.strip().lower()
    matches = [entry for entry in entries if search in entry.lower()]
    return matches
        

def entry_exists(title):
    result = search_results(title)
    return len(result) == 1 and result[0].lower() == title.lower()




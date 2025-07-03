import random
from django import forms
from django.shortcuts import redirect, render
import markdown2
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The title doesn't exist"
        })
    
    page_content = markdown2.markdown(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": page_content
    })

def search(request):
    search = request.GET.get("q")
    result = util.search_results(search)
    if result:
        if util.entry_exists(search):
            return redirect(f"wiki/{result[0]}")
        else:
            return render(request, "encyclopedia/search_results.html", {
                "results": result,
                "search": search
            })
    else:
        return render(request, "encyclopedia/error.html",{
            "message": f"No se encontraron resultados para '{search}'."
        })
        


class NewPageForm(forms.Form):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter a title."
        })
        )
    content = forms.CharField(
        label="Content",
        widget=forms.Textarea(attrs={
            "rows": 10,
            "class": "form-control",
            "placeholder": "Enter the content.",
            "style": "resize: vertical;"  
            })
        )
class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
            "rows": 10,
            "class": "form-control",
            "placeholder": "Enter the content.",
            "style": "resize: vertical;"
            })
    )


def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            result = util.search_results(title)
            if util.entry_exists(title):
                return render(request, "encyclopedia/error.html", {
                    "message": f"The page {title} already exists."
                })
            else:
                util.save_entry(title,f"# {title}\n\n{content}")
                return redirect(f"wiki/{title}")
        else:
            return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm()
            })
    return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm()
    })

def editpage(request, title):
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data['content']
            util.save_entry(title, new_content)
            return redirect(f"/wiki/{title}")
    else:
        content = util.get_entry(title)
        if content is None:
            return render(request, "encyclopedia/error.html",{
                "message": "The request page was not found."
            })
        form = EditPageForm(initial={"content": content})
    return render(request, "encyclopedia/editpage.html",{
        "form": form,
        "title": title
    })
    




def randompage(request):
    entries = util.list_entries()
    randomtitle = random.choice(entries)
    return redirect(f"wiki/{randomtitle}")


This project uses MKDocs for documentation generation. So this section will be a quick introduction to MDDocs.

MKDocs allows you to create modern looking documentation by combining MarkDown files with you Python docstrings. Currently we are using the 
'material'-look popularized by google. This can be changed at any time at will. 

# General overview

All markdownfiles are collected in the 'docs' directory. So if you want to add to the existing documentation it is wise to add a new
file in this directory.
If you want to change any of the settings of the documentation; the theme, the markdown extensions the navigation, you need to change the
mkdocs.yml-file. Alle markdown-files you want to display in the documentation need to be listed under the point 'nav'.

# Serving the documentaion locally
If you want to take a quick look at the changes to yaml or any markdown-file you made run 
```{bash}
mkdocs serve
``` 
in the directory where the .yml-file is located.
The documentaion will be served at you localhost in the browser.
Most changes will be quickloaded meaning that you do not have to reserve after minor changes.
If you have any errors in your code, i.e. forgetting the colon (:) after a function definition, the process will fail and you will get an error message.

# Inserting your docstrings into the documentation
MKDocs allows you to use your docstrings directly inside the markdown-files.
For this you need the special identifier (:::) inside the makrdown-fie.
After the ::: add the path to the directory or file from which you want to get the docstrings.

# Building the documentation
To build your documentation run the command:
```{bash}
mkdocs build
```
This will create a directory called /site which contains all neccessary assets for hosting the documentation.

You can host the documentation wherever you want, for this project we host the documentation on github.
To do this simply run
```{bash}
mkdocs gh-deploy
```

# Plugins
 * mkdocstrings: This Plugin allows us to use python docstrings in the markdown-files.
 * pymdownx.superfences: This plugin allwos us to create the diagramms you saw in the introduction.

# Further reading
A more detailed tutorial on mkdocs can be found [here](https://realpython.com/python-project-documentation-with-mkdocs).

The Documentation for MKDocs is located [here](https://www.mkdocs.org).

The Diagram plugin is explored [here](https://squidfunk.github.io/mkdocs-material/reference/diagrams/).


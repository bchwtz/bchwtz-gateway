This project uses MKDocs for documentation generation. So this section will be a quick introduction to MKDocs.

MKDocs allows you to create a modern looking documentation by combining MarkDown files with you Python docstrings. Currently we are using the 'material'-look popularized by google.

# General overview

All markdownfiles are collected in the 'docs' directory. If you add to the existing documentation you need to add a new .md file in this directory. Inside the 'docs'-directory new subdirectories can be added to group related bits of documentation in a clear way.
To change any of the settings of the documentation; the theme, the markdown extensions the navigation, you need to change the mkdocs.yml-file. Alle markdown-files you want to display in the documentation need to be listed under the point 'nav'.


# Inserting your docstrings into the documentation
MKDocs allows you to use your docstrings directly inside the markdown-files.
For this you need the special identifier (:::) inside the makrdown-file.
After the ::: add the path to the directory or file from which you want to get the docstrings.
```{markdown}
::: path.to.directory
```

# Serving the documentaion locally
If you want to take a quick look at the changes to yaml or any markdown-file you made run 
```{bash}
mkdocs serve
``` 
in the projects root-directory where the .yml-file is located.
The documentaion will be served at you localhost in the browser.
Most changes will be quickloaded meaning that you do not have to reserve after minor changes.
If you have any errors in your code, i.e. forgetting the colon (:) after a function definition, the process will fail and you will get an error message.

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
This will push the latest changes to the documentation to the gh-deploy branch.
# Github action

If pushes or Pull request are made to the main-/ or gh-pages-branch a github action will trigger and redeploy the entire
documentation.

# Plugins
 * [mkdocstrings](https://mkdocstrings.github.io): This Plugin allows us to use python docstrings in the markdown-files.
 * [pymdownx.superfences](https://squidfunk.github.io/mkdocs-material/reference/diagrams/): This plugin allwos us to create the diagramms you saw in the introduction.
 * [pymdownx.highlight](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/): Adds support for code highlighting. 

# Further reading
A more detailed tutorial on mkdocs can be found [here](https://realpython.com/python-project-documentation-with-mkdocs).

The Documentation for MKDocs is located [here](https://www.mkdocs.org).



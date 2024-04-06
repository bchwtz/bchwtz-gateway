# MkDocs

This project uses MKDocs for documentation generation. So this section will be a quick introduction to MKDocs.

MKDocs allows you to create a modern looking documentation by combining MarkDown files with you Python docstrings. Currently we are using the 'material'-look popularized by google.

## Installing MkDocs packages
In order to use MkDocs to view the documentation locally, you first need to run the following pip commands:
Depending on if you are using conda or venv to manage your python environments you have to activate the correct environment into which you want to install the MkDocs package by either doing

```{bash}
conda activate env_name
```
or
```{bash}
source path_to_env/bin/activate
```
Afterwards you can go ahead and run the following command to install MkDocs and all its required dependencies and addons:

```{bash}
pip install mkdocs pymdown-extensions mkdocs-minify-plugin mkdocs-material mkdocstrings-python
```
## General overview
All markdownfiles are collected in the 'docs' directory. If you want to add to the existing documentation you need to add a new .md file in this directory. Inside the 'docs'-directory new subdirectories can be added to group related bits of documentation in a clear way.
To change any of the settings of the documentation; the theme, the markdown extensions, the navigation etc. you need to change the mkdocs.yml-file. All markdown-files you want to display in the documentation need to be listed under the point 'nav'.

## Running MkDocs locally
To run MkDocs locally you now just need to activate the correct environment and call the mkdocs.yaml file from the correct directory. In our case you can just clone the gateway repository, the mkdocs.yaml is located in its root directory while all referenced pages are contained in the "docs" folder.

```{bash}
git clone https://github.com/bchwtz/bchwtz-gateway
```

Now navigate to the root of the cloned repository and run the following command:
```{bash}
mkdocs serve
```
If everything is configured correctly this should now spin up a local session which you can access via your web browser by using the URL posted in the terminal (localhost).  
Most changes will be quickloaded meaning that you do not have to run "serve" again after minor changes.

## Editing documents
You can edit a document by just opening it with a text editor of your choice (or RStudio), MkDocs expects valid markdown syntax.
Whenever you save a document you can just reload the current page in your browser and the edits should be reflected immediately. If you have no open MkDocs session running, just start up a new one as shown above.

## Inserting your docstrings into the documentation
MKDocs allows you to use your docstrings directly inside the markdown-files.
For this you need the special identifier (:::) inside the makrdown-file.
After the ::: add the path to the directory or file from which you want to get the docstrings.
```{markdown}
::: path.to.directory
```

## Building the documentation
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
## Github action

If pushes or Pull request are made to the main-/ or gh-pages-branch a github action will trigger and redeploy the entire
documentation.

## Plugins
 * [mkdocstrings](https://mkdocstrings.github.io): This Plugin allows us to use python docstrings in the markdown-files.
 * [pymdownx.superfences](https://squidfunk.github.io/mkdocs-material/reference/diagrams/): This plugin allwos us to create the diagramms you saw in the introduction.
 * [pymdownx.highlight](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/): Adds support for code highlighting. 

## Further reading
A more detailed tutorial on mkdocs can be found [here](https://realpython.com/python-project-documentation-with-mkdocs).

The Documentation for MKDocs is located [here](https://www.mkdocs.org).



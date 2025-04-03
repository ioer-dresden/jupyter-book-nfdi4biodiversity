[![version](https://training.fdz.ioer.info/version.svg)][static-gl-url] [![pipeline](https://training.fdz.ioer.info/pipeline.svg)][static-gl-url]

# IOER Jupyter-Book NFDI4Biodiversity 

This is the public repository for the Jupytwer book, available at https://training.fdz.ioer.info/. We use this repository for outreach. All internal collaboration and continuous integration and deployment (CI & CD) takes place in [this Gitlab repository](https://gitlab.hrz.tu-chemnitz.de/ioer/fdz/jupyter-book-nfdi4biodiversity).

## TL;DR

The workflow is as follows:
1. Edit notebooks (`*.ipynb` files) in `notebooks/`
2. Commit changes, optionally on a separate branch/fork and create a Pull Request
3. Notebooks are converted to Markdown and then to Jupyter-book
4. The jupyter book is published (deployed) under https://stag.training.fdz.ioer.info/ (git staging branch) and  https://training.fdz.ioer.info/ (git main branch)

 ```mermaid 
 %%{init: { 'theme':'forest', 'securityLevel': 'loose', 'sequence': {'useMaxWidth':false} } }%%
 flowchart LR;
    notebooks/01_introduction.ipynb-->01_introduction.md-->HTML-->Gitlab-CI-->Webserver-->'training.fdz.ioer.info'
 ```

See the [Contribution Documentation](https://training.fdz.ioer.info/CONTRIBUTING.html) for a brief walkthrough of the collaboration process.

## Developers

- This repository is versioned with 
  [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/),
- If you want to run these notebooks, have a look at the instructions to use the 
  [Carto-Lab Docker](https://gitlab.vgiscience.de/lbsn/tools/jupyterlab), 
  provided at the beginning of the [Part I - Introduction][1].
- See [the Contributing](https://stag.training.fdz.ioer.info/CONTRIBUTING.html) section for a step by step description

[1]: https://training.fdz.ioer.info/notebooks/102_jupyter_notebooks.html#carto-lab-docker
[static-gl-url]: https://gitlab.hrz.tu-chemnitz.de/ioer/fdz/jupyter-book-nfdi4biodiversity

[![version](https://training.fdz.ioer.info/version.svg)][static-gl-url] [![pipeline](https://training.fdz.ioer.info/pipeline.svg)][static-gl-url]

# Jupyter-Book NFDI4Biodiversity 

This is the repository for the work-in-progress project that is available under https://training.fdz.ioer.info/

## TL;DR

The workflow is as follows:
1. Edit notebooks (`*.ipynb` files) in `notebooks/`
2. Commit changes to gitlab
3. Notebooks are converted to Markdown and then to Jupytr-book
4. The jupyter book is published (deployed) under https://stag.training.fdz.ioer.info/ (git staging branch) and  https://training.fdz.ioer.info/ (git main branch)

 ```mermaid 
 %%{init: { 'theme':'forest', 'securityLevel': 'loose', 'sequence': {'useMaxWidth':false} } }%%
 flowchart LR;
    notebooks/01_introduction.ipynb-->01_introduction.md-->HTML-->Gitlab-CI-->Webserver-->'training.fdz.ioer.info'
 ```

See the [Contribution Documentation](https://stag.training.fdz.ioer.info/contributing.html) for a brief walkthrough of the collaboration process.

## Developers

- This repository is versioned with 
  [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/),
- Jupyter notebooks are tracked as Markdown files using [Jupytext](https://github.com/mwouts/jupytext).
- If you want to run these notebooks, have a look at the instructions to use the 
  [Carto-Lab Docker](https://gitlab.vgiscience.de/lbsn/tools/jupyterlab), 
  provided at the beginning of the [notebook][1].

To manually bump a version:
```python
semantic-release publish
```

To create `ipynb` files from Markdown:
```
conda activate jupyter_env
jupytext --sync /home/jovyan/work/md/notebook.md
```

This will create notebooks that can be opened in JupyterLab in the subfolder [notebooks/](notebooks/).

[1]: https://training.fdz.ioer.info/
[static-gl-url]: https://gitlab.hrz.tu-chemnitz.de/ioer/fdz/jupyter-book-nfdi4biodiversity

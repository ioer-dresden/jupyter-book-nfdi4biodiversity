# conf.py, needed for custom reference citation style, see:
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#custom-inline-citation-references

from dataclasses import dataclass, field
import sphinxcontrib.bibtex.plugin
from sphinxcontrib.bibtex.style.referencing import BracketStyle
from sphinxcontrib.bibtex.style.referencing.author_year import AuthorYearReferenceStyle

# Define a new bracket style for round parentheses
def round_bracket_style() -> BracketStyle:
    return BracketStyle(
        left='(',
        right=')',
    )

# Define your custom reference style
@dataclass
class MyAuthorYearRoundReferenceStyle(AuthorYearReferenceStyle):
    # Override the bracket style for textual citations (like :cite:t:)
    # This specifically affects the [year] part in "Author [year]"
    bracket_textual: BracketStyle = field(default_factory=round_bracket_style)
    
    # You might also want to ensure parenthetical citations (:cite:p:) also use round brackets
    # if you use them elsewhere, though your example is for :cite:t:
    bracket_parenthetical: BracketStyle = field(default_factory=round_bracket_style)

    # The original example also overrode these, you can include them for completeness
    # or if you use :cite:author:, :cite:year:, :cite:label: roles directly.
    # For :cite:t: Author (Year), bracket_textual is the key one.
    bracket_author: BracketStyle = field(default_factory=round_bracket_style)
    bracket_label: BracketStyle = field(default_factory=round_bracket_style)
    bracket_year: BracketStyle = field(default_factory=round_bracket_style)


# Register your custom style with sphinxcontrib-bibtex
sphinxcontrib.bibtex.plugin.register_plugin(
    'sphinxcontrib.bibtex.style.referencing',  # Group
    'author_year_round_custom',                # Name of your style
    MyAuthorYearRoundReferenceStyle            # The class implementing the style
)

# Ensure sphinxcontrib.bibtex is in your extensions list if not already managed by Jupyter Book's _config.yml
# extensions = ['sphinxcontrib.bibtex'] # This is usually handled by _config.yml for Jupyter Book

# The bibtex_bibfiles setting is already in your _config.yml, so no need to duplicate here
# bibtex_bibfiles = ["references.bib"]

# The bibtex_reference_style will be set in _config.yml to use your new custom style
# bibtex_reference_style = 'author_year_round_custom'
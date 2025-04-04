"""
tools.py – A number of helper tools to reduce and share code in spatial data processing with JupyterLab notebooks.

Author: Dr.-Ing. Alexander Dunkel
License: MIT License
Source: https://gitlab.hrz.tu-chemnitz.de/s7398234--tu-dresden.de/base_modules/
"""

# --- Standard Library ---
import base64
import csv
import fnmatch
import io
import os
import platform
import shutil
import textwrap
import warnings
import zipfile
from collections import namedtuple
from datetime import date
from itertools import islice
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# --- Third-Party Libraries ---
import geopandas as gp
import matplotlib.pyplot as plt
import mapclassify as mc
import numpy as np
import pandas as pd
import pkg_resources
import requests
from PIL import Image
from adjustText import adjust_text
from cartopy import crs
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from pyproj import Transformer
import geoviews as gv

# --- Jupyter-Specific ---
from IPython.display import HTML, Markdown as md, clear_output, display
from html import escape

# --- Globals ---
OUTPUT = Path.cwd().parents[0] / "out"
class DbConn(object):

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def query(self, sql_query: str) -> pd.DataFrame:
        """Execute Calculation SQL Query with pandas"""
        with warnings.catch_warnings():
            # ignore warning for non-SQLAlchemy Connecton
            # see github.com/pandas-dev/pandas/issues/45660
            warnings.simplefilter('ignore', UserWarning)
            # create pandas DataFrame from database query
            df = pd.read_sql_query(sql_query, self.db_conn)
        return df

    def close(self):
        self.db_conn.close()

def classify_data(values: np.ndarray, scheme: str):
    """Classify data (value series) and return classes,
       bounds, and colormap
       
    Args:
        grid: A geopandas geodataframe with metric column to classify
        metric: The metric column to classify values
        scheme: The classification scheme to use.
        mask_nonsignificant: If True, removes non-significant values
            before classifying
        mask_negative: Only consider positive values.
        mask_positive: Only consider negative values.
        cmap_name: The colormap to use.
        return_cmap: if False, returns list instead of mpl.ListedColormap
        store_classes: Update classes in original grid (_cat column). If
            not set, no modifications will be made to grid.
        
    Adapted from:
        https://stackoverflow.com/a/58160985/4556479
    See available colormaps:
        http://holoviews.org/user_guide/Colormaps.html
    See available classification schemes:
        https://pysal.org/mapclassify/api.html
        
    Notes: some classification schemes (e.g. HeadTailBreaks)
        do not support specifying the number of classes returned
        construct optional kwargs with k == number of classes
    """
    optional_kwargs = {"k":7}
    if scheme == "HeadTailBreaks":
        optional_kwargs = {}
    scheme_breaks = mc.classify(
        y=values, scheme=scheme, **optional_kwargs)
    return scheme_breaks

def display_file(file_path: Path, formatting: str = 'Python', summary_txt: str = 'Have a look at '):
    """Load a file and display as Markdown formatted details-summary code-block"""
    txt = f"<details style='cursor: pointer;'><summary>{summary_txt}<code>{file_path.name}</code></summary>\n\n```{formatting}\n\n"
    txt += open(file_path, 'r').read() 
    txt += "\n\n```\n\n</details>"
    display(md(txt))

def print_link(url: str, hashtag: str):
    """Format HTML link with hashtag"""
    return f"""
        <div class="alert alert-warning" role="alert" style="color: black;">
            <strong>Open the following link in a new browser tab and have a look at the content:</strong>
            <br>
            <a href="{url}">Instagram: {hashtag} feed (json)</a>
        </div>
        """

FileStat = namedtuple('File_stat', 'name, size, records')

def get_file_stats(name: str, file: Path) -> Tuple[str, str, str]:
    """Get number of records and size of CSV file"""
    num_lines = f'{sum(1 for line in open(file)):,}'
    size = file.stat().st_size
    size_gb = size/(1024*1024*1024)
    size_format = f'{size_gb:.2f} GB'
    size_mb = None
    if size_gb < 1:
        size_mb = size/(1024*1024)
        size_format = f'{size_mb:.2f} MB'
    if size_mb and size_mb < 1:
        size_kb = size/(1024)
        size_format = f'{size_kb:.2f} KB'
    return FileStat(name, size_format, num_lines)

def display_file_stats(filelist: Dict[str, Path]):
    """Display CSV """
    df = pd.DataFrame(
        data=[
            get_file_stats(name, file) for name, file in filelist.items() if file.exists()
            ]).transpose()
    header = df.iloc[0]
    df = df[1:]
    df.columns = header
    display(df.style.background_gradient(cmap='viridis'))

def get_sample_url(use_base: bool = None):
    """Retrieve sample json url from .env"""
    if use_base is None:
        use_base = True
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None 

    if load_dotenv:
        load_dotenv(Path.cwd().parents[0] / '.env', override=True)
    else:
        print("dotenv package not found, could not load .env")
    SAMPLE_URL = os.getenv("SAMPLE_URL")
    if SAMPLE_URL is None:
        raise ValueError(
            f"Environment file "
            f"{Path.cwd().parents[0] / '.env'} not found")
    if use_base:
        SAMPLE_URL = f'{BASE_URL}{SAMPLE_URL}'
    return SAMPLE_URL

def return_total(headers: Dict[str, str]):
    """Return total length from requests header"""
    if not headers:
        return 
    total_length = headers.get('content-length')
    if not total_length:
        return
    try:
        total_length = int(total_length)
    except:
        total_length = None
    return total_length
    
def stream_progress(total_length: int, loaded: int):
    """Stream progress report"""
    clear_output(wait=True)            
    perc_str = ""
    if total_length:
        total = total_length/1000000
        perc = loaded/(total/100)
        perc_str = f"of {total:.2f} ({perc:.0f}%)"
    print(
        f"Loaded {loaded:.2f} MB "
        f"{perc_str}..")

def stream_progress_basic(total: int, loaded: int):
    """Stream progress report"""
    clear_output(wait=True)            
    perc_str = ""
    if total:
        perc = loaded/(total/100)
        perc_str = f"of {total:.0f} ({perc:.0f}%)"
    print(
        f"Processed {loaded:.0f} "
        f"{perc_str}..")

def get_stream_file(url: str, path: Path):
    """Download file from url and save to path"""
    chunk_size = 8192
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = return_total(r.headers)
        with open(path, 'wb') as f:
            for ix, chunk in enumerate(r.iter_content(chunk_size=chunk_size)): 
                f.write(chunk)
                loaded = (ix*chunk_size)/1000000
                if (ix % 100 == 0):
                    stream_progress(
                        total_length, loaded)
            stream_progress(
                total_length, loaded)
                        
def get_stream_bytes(url: str):
    """Stream file from url to bytes object (in-memory)"""
    chunk_size = 8192
    content = bytes()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = return_total(r.headers)
        for ix, chunk in enumerate(r.iter_content(
                chunk_size=chunk_size)): 
            content += bytes(chunk)
            loaded = (ix*chunk_size)/1000000
            if (ix % 100 == 0):
                stream_progress(
                    total_length, loaded)
    stream_progress(
        total_length, loaded)
    return content
                        
def highlight_row(s, color):
    return f'background-color: {color}'

def display_header_stats(
        df: pd.DataFrame, metric_cols: List[str], base_cols: List[str]):
    """Display header stats for CSV files"""
    pd.options.mode.chained_assignment = None
    # bg color metric cols
    for col in metric_cols:
        df.loc[df.index, col] = df[col].str[:25]
    styler = df.style
    styler.applymap(
        lambda x: highlight_row(x, color='#FFF8DC'), 
        subset=pd.IndexSlice[:, metric_cols])
    # bg color base cols
    styler.applymap(
        lambda x: highlight_row(x, color='#8FBC8F'), 
        subset=pd.IndexSlice[:, base_cols])
    # bg color index cols (multi-index)
    css = []
    for ix, __ in enumerate(df.index.names):
        idx = df.index.get_level_values(ix)
        css.extend([{
            'selector': f'.row{i}.level{ix}',
            'props': [('background-color', '#8FBC8F')]}
                for i,v in enumerate(idx)])
    styler.set_table_styles(css)
    display(styler)

def get_folder_size(folder: Path):
    """Return size of all files in folder in MegaBytes"""
    if not folder.exists():
        raise Warning(
            f"Folder {folder} does not exist")
        return
    size_mb = 0
    for file in folder.glob('*'):
        size_mb += file.stat().st_size / (1024*1024)
    return size_mb

def get_zip_extract(
    output_path: Path, 
    uri: str = None, filename: str = None, uri_filename: str = None,
    create_path: bool = True, skip_exists: bool = True,
    report: bool = True, filter_files: List[str] = None,
    write_intermediate: bool = None):
    """Get Zip file and extract to output_path.
    Create Path if not exists."""
    if uri is None or filename is None:
        if uri_filename is None:
            raise ValueError("Either specify uri and filename or the complete url (uri_filename)")
        url_prs = urlparse(uri_filename)
        filename = os.path.basename(url_prs.path)
        uri = f"{url_prs.scheme}://{url_prs.netloc}{os.path.dirname(url_prs.path)}/"
    if write_intermediate is None:
        write_intermediate = False
    if create_path:
        output_path.mkdir(
            exist_ok=True)
    if skip_exists and Path(
        output_path / Path(filename).with_suffix('')).exists():
        # check if folder exists 
        # remove .zip suffix from filename first
        if report:
            print("File already exists.. skipping download..")
        return
    if write_intermediate:
        out_file = output_path / filename
        get_stream_file(f'{uri}{filename}', out_file)
        z = zipfile.ZipFile(out_file)
    else:
        content = get_stream_bytes(
            f'{uri}{filename}')
        z = zipfile.ZipFile(io.BytesIO(content))
    print("Extracting zip..")
    if filter_files:
        file_names = z.namelist()
        for filename in file_names:
            if filename in filter_files:
                z.extract(filename, output_path)
    else:
        z.extractall(output_path)
    if write_intermediate:
        if out_file.is_file():
            out_file.unlink()
    if report:
        raw_size_mb = get_folder_size(output_path)
        print(
            f"Retrieved {filename}, "
            f"extracted size: {raw_size_mb:.2f} MB")

def zip_dir(path: Path, zip_file_path: Path):
    """Zip all contents of path to zip_file. Will not recurse subfolders."""
    files_to_zip = [
        file for file in path.glob('*') if file.is_file()]
    with zipfile.ZipFile(
        zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
        for file in files_to_zip:
            zip_f.write(file, file.name)

def drop_cols_except(
        df: pd.DataFrame, columns_keep: List[str], inplace: bool = None) -> Optional[pd.DataFrame]:
    """Drop all columns from DataFrame except those specified in columns_keep
    """
    cols_to_drop = df.columns.difference(columns_keep)
    if inplace is None:
        # by default, drop with inplace=True
        df.drop(
            cols_to_drop, axis=1, inplace=True)
        return
    return df.drop(cols_to_drop, axis=1, inplace=False)
        
    
def clean_folder(path: Path):
    """Remove folder, warn if recursive"""
    if not path.is_dir():
        print(f"{path} is not a directory")
        return
    raw_size_mb = get_folder_size(path)
    contents = [content for content in path.glob('*')]
    answer = input(
        f"Removing {path.stem} with "
        f"{len(contents)} files / {raw_size_mb:.0f} MB ? "
        f"Type 'y' or 'yes'")
    if answer not in ["y", "yes"]:
        print("Cancel.")
        return
    for content in contents:
        if content.is_file():
            content.unlink()
            continue
        try:
            content.rmdir()
        except:
            raise Warning(
                f"{content.name} contains subdirs. "
                f"Cancelling operation..")
            return
    path.rmdir()

def clean_folders(paths: List[Path]):
    """Clean list of folders (depth: 2)"""
    for path in paths:
        clean_folder(path)
    print(
        "Done. Thank you. "
        "Do not forget to shut down your notebook server "
        "(File > Shut Down), once you are finished with "
        "the last notebook.")

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def package_report(root_packages: List[str], python_version = True):
    """Report package versions for root_packages entries"""
    root_packages.sort(reverse=True)
    root_packages_list = []
    if python_version:
        pyv = platform.python_version()
        root_packages_list.append(["python", pyv])
    for m in pkg_resources.working_set:
        if m.project_name.lower() in root_packages:
            root_packages_list.append([m.project_name, m.version])
    html_tables = ''
    for chunk in chunks(root_packages_list, 10):
        # get table HTML
        html_tables += pd.DataFrame(
                    chunk,
                    columns=["package", "version"]
                ).set_index("package").transpose().to_html()
    display(HTML(
        f'''
        <details><summary style="cursor: pointer;">List of package versions used in this notebook</summary>
        {html_tables}
        </details>
        '''
        ))

def tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False,
         length_limit: int = 1000, ignore_files_folders=None, ignore_match=None,
         sort_key=lambda x: x.name.lower()):
    """
    Pretty-print a visual tree structure of the directory in a Jupyter notebook,
    with root-level folders listed before files.
    """
    dir_path = Path(dir_path)
    files = 0
    directories = 0

    space = '    '
    branch = '│   '
    tee = '├── '
    last = '└── '

    print_list = []

    always_ignore = {".git", ".ipynb_checkpoints", "__pycache__", "__init__.py"}
    if ignore_files_folders is None:
        ignore_files_folders = always_ignore
    else:
        ignore_files_folders = set(ignore_files_folders) | always_ignore

    if ignore_match is None:
        ignore_match = ["_*", "*.pyc", "*.bak"]

    def inner(current_path: Path, prefix: str = '', level: int = -1, is_root=False):
        nonlocal files, directories
        if level == 0:
            return

        try:
            contents = [p for p in current_path.iterdir()
                        if p.name not in ignore_files_folders and
                        not any(fnmatch.fnmatch(p.name, pat) for pat in ignore_match)]
        except PermissionError:
            return

        # At root: folders first, then files (both sorted)
        if is_root:
            dirs = sorted([p for p in contents if p.is_dir()], key=sort_key)
            non_dirs = sorted([p for p in contents if not p.is_dir()], key=sort_key)
            contents = dirs + non_dirs
        else:
            contents = sorted(contents, key=sort_key)

        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            line = prefix + pointer + path.name
            yield line

            if path.is_dir():
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix + extension, level=level - 1)
            elif not limit_to_directories:
                files += 1

    # Generate tree body
    iterator = inner(dir_path, level=level, is_root=True)
    for line in islice(iterator, length_limit):
        print_list.append(escape(line))

    if next(iterator, None):
        print_list.append(f"... length_limit, {length_limit}, reached, counted:")

    print_list.append(f"\n{directories} directories" + (f", {files} files" if files else ""))
    print_list.append(".")  # Root at the end

    return HTML(f"""
    <div>
        <details><summary style='cursor: pointer;'><kbd>Directory file tree</kbd></summary>
        <pre><code>{"<br>".join(print_list)}</code></pre>
        </details>
    </div>      
    """)


def record_preview_hll(file: Path, num: int = 0):
    """Get record preview for hll data"""
    with open(file, 'r', encoding="utf-8") as file_handle:
        post_reader = csv.DictReader(
                    file_handle,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
        for ix, hll_record in enumerate(post_reader):
            hll_record = get_hll_record(hll_record, strip=True)
            # convert to df for display
            display(pd.DataFrame(data=[hll_record]).rename_axis(
                f"Record {ix}", axis=1).transpose().style.background_gradient(cmap='viridis'))
            # stop iteration after x records
            if ix >= num:
                break

HllRecord = namedtuple('Hll_record', 'latitude, longitude, user_hll, post_hll, date_hll')
HllOriginRecord = namedtuple('HllOrigin_record', 'origin_id, latitude, longitude, user_hll, post_hll, date_hll')

def strip_item(item, strip: bool):
    if item is None:
        return
    if not strip:
        return item
    if len(item) > 120:
        item = item[:120] + '..'
    return item

def get_hll_record(record, strip: bool = None):
    """Concatenate topic info from post columns"""

    origin_id = record.get('origin_id')
    latitude = record.get('latitude')
    longitude = record.get('longitude')
    cols = ['user_hll', 'post_hll', 'date_hll']
    col_vals = []
    for col in cols:
        col_val = record.get('user_hll')
        col_vals.append(strip_item(record.get(col), strip))
    if not origin_id is None:
        return HllOriginRecord(origin_id, latitude, longitude, *col_vals)
    return HllRecord(latitude, longitude, *col_vals)

def hll_series_cardinality(
    hll_series: pd.Series, db_conn: DbConn,) -> pd.Series:
    """HLL cardinality estimation from a series of hll sets

    Args:
        hll_series: Indexed series of hll sets. 
    """
    # create list of hll values for pSQL
    hll_values_list = ",".join(
        [f"({ix}::int,'{hll_item}'::hll)" 
         for ix, hll_item
         in enumerate(hll_series.values.tolist())])
    # Compilation of SQL query
    return_col = hll_series.name
    db_query = f"""
        SELECT s.ix,
               hll_cardinality(s.hll_set)::int AS {return_col}
        FROM (
            VALUES {hll_values_list}
            ) s(ix, hll_set)
        ORDER BY ix ASC
        """
    df = db_conn.query(db_query)
    # to merge values back to grouped dataframe,
    # first reset index to ascending integers
    # matching those of the returned df;
    # this will turn series_grouped into a DataFrame;
    # the previous index will still exist in column 'index'
    df_series = hll_series.reset_index()
    # drop hll sets not needed anymore
    df_series.drop(columns=[hll_series.name], inplace=True)
    # append hll_cardinality counts 
    # using matching ascending integer indexes
    df_series.loc[df.index, return_col] = df[return_col].values
    # set index back to original multiindex
    df_series.set_index(hll_series.index.names, inplace=True)
    # return as series
    return df_series[return_col].astype(np.int64)

def union_hll_series(
    hll_series: pd.Series, db_conn: DbConn, cardinality: bool = True, multiindex: bool = None) -> pd.Series:
    """HLL Union and (optional) cardinality estimation from series of hll sets
    based on group by composite index.

        Args:
        hll_series: Indexed series (bins) of hll sets. 
        cardinality: If True, returns cardinality (counts). Otherwise,
            the unioned hll set will be returned.
        multiindex: Specify, whether Series is indexed with a multiindex (a composite index)
            
    The method will combine all groups of hll sets first,
        in a single SQL command. Union of hll-sets belonging 
        to the same group (bin) and (optionally) returning the cardinality 
        (the estimated count) per group will be done in postgres.
    
    By utilizing Postgres´ GROUP BY (instead of, e.g. doing 
        the group with numpy), it is possible to reduce the number
        of SQL calls to a single run, which saves overhead 
        (establishing the db connection, initializing the SQL query 
        etc.). Also note that ascending integers are used for groups,
        instead of their full original bin-ids, which also reduces
        transfer time.
    
    cardinality = True should be used when calculating counts in
        a single pass.
        
    cardinality = False should be used when incrementally union
        of hll sets is required, e.g. due to size of input data.
        In the last run, set to cardinality = True.
    """
    # group all hll-sets per index (bin-id)
    series_grouped = hll_series.groupby(
        hll_series.index).apply(list)
    # From grouped hll-sets,
    # construct a single SQL Value list;
    # if the following nested list comprehension
    # doesn't make sense to you, have a look at
    # spapas.github.io/2016/04/27/python-nested-list-comprehensions/
    # with a decription on how to 'unnest'
    # nested list comprehensions to regular for-loops
    hll_values_list = ",".join(
        [f"({ix}::int,'{hll_item}'::hll)" 
         for ix, hll_items
         in enumerate(series_grouped.values.tolist())
         for hll_item in hll_items])
    # Compilation of SQL query,
    # depending on whether to return the cardinality
    # of unioned hll or the unioned hll
    return_col = "hll_union"
    hll_calc_pre = ""
    hll_calc_tail = "AS hll_union"
    if cardinality:
        # add sql syntax for cardinality 
        # estimation
        # (get count distinct from hll)
        return_col = "hll_cardinality"
        hll_calc_pre = "hll_cardinality("
        hll_calc_tail = ")::int"
    db_query = f"""
        SELECT sq.{return_col} FROM (
            SELECT s.group_ix,
                   {hll_calc_pre}
                   hll_union_agg(s.hll_set)
                   {hll_calc_tail}
            FROM (
                VALUES {hll_values_list}
                ) s(group_ix, hll_set)
            GROUP BY group_ix
            ORDER BY group_ix ASC) sq
        """
    df = db_conn.query(db_query)
    # to merge values back to grouped dataframe,
    # first reset index to ascending integers
    # matching those of the returned df;
    # this will turn series_grouped into a DataFrame;
    # the previous index will still exist in column 'index'
    df_grouped = series_grouped.reset_index()
    # drop hll sets not needed anymore
    df_grouped.drop(columns=[hll_series.name], inplace=True)
    # append hll_cardinality counts 
    # using matching ascending integer indexes
    df_grouped.loc[df.index, return_col] = df[return_col].values
    # set index back to original bin-ids
    if multiindex:
        df_grouped.index = pd.MultiIndex.from_tuples(
            df_grouped["index"], names=hll_series.index.names)
    else:
        # set index from column named "index",
        # the original composite-inex, stored as tuples
        df_grouped.set_index(hll_series.index.names, inplace=True)
    series = df_grouped[return_col]
    if cardinality:
         return series.astype(np.int64)
    return series

def check_table_exists(
        db_conn: DbConn, table_name: str, schema: str = None) -> bool:
    """Check if a table exists or not, using db_conn and table_name"""
    if not schema:
        schema = 'mviews'
    sql_query = f"""
    SELECT EXISTS (
       SELECT FROM information_schema.tables 
       WHERE  table_schema = '{schema}'
       AND    table_name   = '{table_name}'
       );
    """
    result = db_conn.query(sql_query)
    return result["exists"][0]

def get_shapes(
        reference: str, shape_dir: Path,
        clean_cols: Optional[bool] = None, normalize_cols: Optional[bool] = None,
        set_index: Optional[bool] = None, project_wgs84: Optional[bool] = None) -> gp.GeoDataFrame:
    """Custom method to get frequently used shapes (DE Bundesländer, US States)
    and return a geopandas.GeoDataFrame (WGS1984)

    reference: str - "us" and "de" are currently supported
    clean_cols: will remove all columns except geometry and state-reference. Defaults to True.
    normalize_cols: will rename columns to sane defaults. Defaults to True.
    set_index: will set state-reference as index column. Defaults to True.
    project_wgs84: Project shapes to WGS1984. Defaults to True.
    """
    if clean_cols is None:
        clean_cols = True
    if normalize_cols is None:
        normalize_cols = True
    if set_index is None:
        set_index = True
    if project_wgs84 is None:
        project_wgs84 = True
    target_name = "state"
    if reference == "us":
        source_zip = "https://www2.census.gov/geo/tiger/GENZ2018/shp/"
        filename = "cb_2018_us_state_5m.zip"
        shapes_name = "cb_2018_us_state_5m.shp"
        col_name = "NAME"
    elif reference == "de":
        source_zip = "https://daten.gdz.bkg.bund.de/produkte/vg/vg2500/aktuell/"
        filename = "vg2500_12-31.utm32s.shape.zip"
        shapes_name = "vg2500_12-31.utm32s.shape/vg2500/VG2500_LAN.shp"
        col_name = "GEN"
    elif reference == "world":
        source_zip = "https://naciscdn.org/naturalearth/110m/cultural/"
        filename = "ne_110m_admin_0_countries.zip"
        shapes_name = "ne_110m_admin_0_countries.shp"
        col_name = "SOVEREIGNT"
        target_name = "country"
    # create  temporary storage folder, if not exists already
    shape_dir.mkdir(exist_ok=True)
    # test if file already downloaded
    if not (shape_dir / shapes_name).exists():
        get_zip_extract(
            uri=source_zip, filename=filename, output_path=shape_dir)
    else:
        print("Already exists")
    shapes = gp.read_file(shape_dir / shapes_name)
    if clean_cols:
        drop_cols_except(df=shapes, columns_keep=["geometry", col_name])
    if normalize_cols:
        shapes.rename(columns={col_name: target_name}, inplace=True)
        col_name = target_name
    if set_index:
        shapes.set_index(col_name, inplace=True)
    if project_wgs84:
        shapes.to_crs("EPSG:4326", inplace=True)
    return shapes

def annotate_locations(
    ax, gdf: gp.GeoDataFrame, label_off: List[Tuple[int,int]],
    label_rad: List[float], text_col: str, coords: str = None, coords_col: str = None,
    arrow_col: str = None, arrowstyle: str = None, fontsize: str = None):
    """Annotate map based on a list of locations
    
    Example values:
    label_off = {
        "San Francisco":(5500000, 1000000),
        "Berlin":(4500000, 1000000),
        "Cabo Verde":(4500000, -1000000)}
    label_rad = {
        "San Francisco":0.1,
        "Berlin":0.5,
        "Cabo Verde":-0.3}
    """
    
    if arrow_col is None:
        arrow_col = 'red'
    if arrowstyle is None:
        arrowstyle = '->'    
    xy_coords = coords 
    for idx, row in gdf.iterrows():
        # print(row)
        if coords_col:
            xy_coords = row[coords_col]
        elif coords is None:
            xy_coords = (row.geometry.centroid.x, row.geometry.centroid.y)
        ax.annotate(
            text=row[text_col], 
            xy=xy_coords,
            fontsize=fontsize,
            xytext=np.subtract(xy_coords, label_off.get(row[text_col])),
            horizontalalignment='left',
            arrowprops=dict(
                arrowstyle=arrowstyle, 
                connectionstyle=f'arc3,rad={label_rad.get(row[text_col])}',
                color=arrow_col))

def annotate_locations_fit(
    ax, gdf: gp.GeoDataFrame, text_col: str, coords: str = None, coords_col: str = None,
    arrow_col: str = None, arrowstyle: str = None, fontsize: int = None, font_path: str = None):
    """Annotate map based on a list of locations and auto-fit to prevent overlap
    
    Example values:
    label_off = {
        "San Francisco":(5500000, 1000000),
        "Berlin":(4500000, 1000000),
        "Cabo Verde":(4500000, -1000000)}
    label_rad = {
        "San Francisco":0.1,
        "Berlin":0.5,
        "Cabo Verde":-0.3}
    """
    if fontsize is None:
        fontsize = 8
    font_prop = None
    if not font_path is None:
        font_manager.fontManager.addfont(font_path)
        font_prop = font_manager.FontProperties(fname=font_path)
    if arrow_col is None:
        arrow_col = 'red'
    if arrowstyle is None:
        arrowstyle = '->'    
    xy_coords = coords
    texts = []
    for idx, row in gdf.iterrows():
            texts.append(
                plt.text(
                    s='\n'.join(textwrap.wrap(
                        row[text_col], 18, break_long_words=True)),
                    x=row.geometry.centroid.x,
                    y=row.geometry.centroid.y,
                    horizontalalignment='center',
                    fontsize=fontsize,
                    fontproperties=font_prop,
                    bbox=dict(
                        boxstyle='round,pad=0.5',
                        fc='white',
                        alpha=0.5)))
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)        
        adjust_text(
            texts, autoalign='y', ax=ax,
            arrowprops=dict(
                arrowstyle="simple, head_length=2, head_width=2, tail_width=.2",
                color='black', lw=0.5, alpha=0.2, mutation_scale=4, 
                connectionstyle=f'arc3,rad=-0.3'))
        
def save_fig(
        fig: plt.Figure, output: Path, name: str, formats: List[str] = ['PNG', 'svg']):
    """Save matplotlib figure to standard folders and file types"""
    (output / "figures").mkdir(exist_ok=True)
    (output / "svg").mkdir(exist_ok=True)
    if 'PNG' in formats:
        fig.savefig(
            output / "figures" / f"{name}.png", dpi=300, format='PNG',
            bbox_inches='tight', pad_inches=1, facecolor="white")
    if 'svg' in formats:
        fig.savefig(
            output / "svg" / f"{name}.svg", format='svg',
            bbox_inches='tight', pad_inches=1, facecolor="white")

def apply_formatting(col, hex_colors):
    """Apply background-colors to pandas columns"""
    for hex_color in hex_colors:
        if col.name == hex_color:
            return [f'background-color: {hex_color}' for c in col.values]

def apply_formatting_num(col, hex_colors, as_id_list):
    """Apply background-colors to pandas columns (id variant)"""
    for ix, id in enumerate(as_id_list):
        if col.name == id:
            return [f'background-color: {hex_colors[ix]}' for c in col.values]
        
def display_hex_colors(hex_colors: List[str], as_id: bool = None):
    """Visualize a list of hex colors using pandas. Use
    as_id=True to output a table with equal-width cols, useful for legends"""
    df = pd.DataFrame(hex_colors).T
    if as_id:
        as_id_list = [f'{x:05d}' for x in list(range(0, len(hex_colors)))]
        df.columns = as_id_list
    else:
        df.columns = hex_colors
    df.iloc[0,0:len(hex_colors)] = ""
    if as_id:
        display(df.style.apply(lambda x: apply_formatting_num(x, hex_colors, as_id_list)))
        return
    display(df.style.apply(lambda x: apply_formatting(x, hex_colors)))
    
def display_debug_dict(debug_dict, transposed: bool = None):
    """Display dict with debug values as (optionally) transposed table"""
    
    if transposed is None:
        transposed = True
    df = pd.DataFrame(debug_dict, index=[0])
    if transposed:
        pd.set_option('display.max_colwidth', None)
        display(df.T)
        # set back to default
        pd.set_option('display.max_colwidth', 50)
    else:
        pd.set_option('display.max_columns', None)
        display(df)
        pd.set_option('display.max_columns', 10)
    
    
def is_nan(x):
    return (x is np.nan or x != x)

def series_to_point(
        points: gp.GeoSeries, crs=crs.Mollweide(), 
        mod_x: Optional[int] = 0, mod_y: Optional[int] = 0) -> gv.Points:
    """Convert a Geopandas Geoseries of points to a Geoviews Points layer"""
    return gv.Points(
        [(point.x+mod_x, point.y+mod_y) for point in points.geometry], crs=crs)

def series_to_label(points: gp.GeoSeries, crs=crs.Mollweide()) -> List[gv.Text]:
    """Convert a Geopandas Geoseries of points to a list of Geoviews Text label layers"""
    return [gv.Text(point.x+300000, point.y+300000, str(i+1), crs=crs) for i, point in enumerate(points.geometry)]

def _svg_to_pdf(filename: Path, out_dir: Optional[Path] = None):
    """Convert a svg on disk to a pdf using cairosvg"""
    if out_dir is None:
        out_dir = filename.parents[0]
    if svg2pdf is None:
        raise ImportError("Please install cairosvg for svg2pdf")
    svg2pdf(file_obj=open(
        filename, "rb"), write_to=str(out_dir / f'{filename.stem}.pdf'))

def svg_to_pdf_chromium(filename: Path,  out_dir: Optional[Path] = None):
    """Convert a svg on disk to a pdf using Selenium and Chromedriver"""
    import json
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    if out_dir is None:
        out_dir = filename.parents[0]
        
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--kiosk-printing')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=2000x2000")
    chrome_options.add_argument('--disable-dev-shm-usage')

    webdriver_chrome = webdriver.Chrome(service=service, options=chrome_options)
    webdriver_chrome.get(f'file://{filename}')

    pdf = webdriver_chrome.execute_cdp_cmd(
        "Page.printToPDF", {
            "paperWidth": 8.3,
            "paperHeight": 11.7,
            "printBackground": True, 
            'landscape': True,
            'displayHeaderFooter': False,
            'scale': 0.75
            })
    
    webdriver_chrome.close()
    
    with open(out_dir / f'{filename.stem}.pdf', "wb") as f:
        f.write(base64.b64decode(pdf['data']))
    
def convert_svg_pdf(in_dir: Path,  out_dir: Optional[Path] = None):
    """Convert all svg in in_dir to a pdf using Selenium and Chromedriver"""
    
    if out_dir is None:
        out_dir = in_dir
    out_dir.mkdir(exist_ok=True)
    files_folders = Path(in_dir).glob('*.svg')
    files_svg = [x for x in files_folders if x.is_file()]
    for cnt, file in enumerate(files_svg):
        svg_to_pdf_chromium(
            filename=file, out_dir=out_dir)
        clear_output(wait=True)
        print(f"Processed {cnt+1} of {len(files_svg)} files..")

def min_max_lim(min_v: int, max_v: int, centroid, orig_centroid):
    if np.isinf(centroid):
        if orig_centroid < 0:
            return min_v
        if orig_centroid > 0:
            return max_v
    return centroid

def image_grid(imgs: List[Path], resize: Optional[Tuple[int, int]] = None, figsize: Optional[Tuple[int, int]] = None):
    """Load and show images in a grid from a list of paths"""
    count = len(imgs)
    if figsize is None:
        figsize = (11, 18)
    plt.figure(figsize=figsize)
    if resize is None:
        resize = (150, 150)
    for ix, path in enumerate(imgs):
        i = Image.open(path)
        i = i.resize(resize)
        plt.subplots_adjust(bottom=0.3, right=0.8, top=0.5)
        ax = plt.subplot(3, 5, ix + 1)
        ax.axis('off')
        plt.imshow(i)


def project_point(
        crs_in: str, crs_out: str, point: Tuple[float, float] = None, 
        points: List[Tuple[float, float]] = None):
    """Project a single or multiple points given two CRS"""
    if not point is None:
        points = [point]
    transformer = Transformer.from_crs(crs_in, crs_out, always_xy=True)
    if not point is None:
        return transformer.itransform(point)
    points_proj = []
    for pt in transformer.itransform(points):
        points_proj.append(pt)
    return points_proj


Bbox = Tuple[float, float, float, float]


def project_bounds(
        bbox: Bbox, crs_in: str, crs_out: str) -> Bbox:
    """Project Bounding Box to new coordinate system"""
    west, south, east, north = bbox
    points = [(west, south), (west, north), (east, north),  (east, south)]
    points_proj = project_point(crs_in=crs_in, crs_out=crs_out, points=points)
    west, south, east, north = points_proj[0][0], points_proj[3][1], \
        points_proj[2][0], points_proj[1][1]
    return (west, south, east, north)


def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


def create_paths(
        output: str = OUTPUT,
        subfolders: List[str] = [
            "html", "pickles", "csv", "figures", "svg", "pdf"]):
    """Create subfolder for results to be stored"""
    output.mkdir(exist_ok=True)
    for subfolder in subfolders:
        Path(OUTPUT / f'{subfolder}').mkdir(exist_ok=True)

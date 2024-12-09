""" A number of helper tools to reduce code in the training materials

    Source: https://gitlab.hrz.tu-chemnitz.de/s7398234--tu-dresden.de/base_modules/
"""
import os
import io
import requests
import pandas as pd
import zipfile
from pathlib import Path
from collections import namedtuple
from IPython.display import clear_output
from typing import List, Optional, Dict, Tuple
from IPython.core.display import display
from IPython.display import Markdown as md
from urllib.parse import urlparse

OUTPUT = Path.cwd().parents[0] / "out"


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

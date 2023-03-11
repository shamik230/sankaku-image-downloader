import requests
import re
import shutil
import os
from pathlib import Path

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        return r
    else:
        print(f"HTML Code: {r.status_code}")
        return None


def get_file(url, folder_name):
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=3)
        f_name = re.findall("/../../(.+)\?", url)
        if len(f_name) == 0:
            return
        with open(folder_name + "/" + f_name[0], 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        del r
        print(f"[DONE] {url}")
    except Exception as e:
        print(f"Exception happened: {e}")
        return


def get_data_from_json(html_json, filename, counter):
    lst = []
    data_json = html_json['data']
    for i in data_json:
        item = i['sample_url']
        if item is not None:
            lst.append(item)
        else:
            continue
    counter += len(lst)
    print(f"Total: {counter}, HTML: {len(lst)}")
    file = open(filename, 'a+')
    for item in lst:
        file.write(item + '\n')
    file.close()
    return counter


def load_links(tags, filename):
    i = 0
    counter = 0
    limit = 40
    url = f'https://capi-v2.sankakucomplex.com/posts/keyset?limit={limit}&tags={tags}'
    html = get_html(url)
    if html is None:
        print("Unable to get HTML")
        return
    print(f"[GET] HTML {i}")
    html_json = html.json()
    counter = get_data_from_json(html_json, filename, counter)
    next_key = html_json['meta']['next']
    url_next = f'https://capi-v2.sankakucomplex.com/posts/keyset?next={next_key}&limit={limit}&tags={tags}'
    while True:
        i += 1
        print("URL:", url_next)
        html = get_html(url_next)
        if html is None:
            print("Unable to get HTML")
            return
        print(f"[GET] HTML {i}")
        html_json = html.json()
        counter = get_data_from_json(html_json, filename, counter)
        next_key = html_json['meta']['next']
        url_next = f'https://capi-v2.sankakucomplex.com/posts/keyset?next={next_key}&limit={limit}&tags={tags}'


def load_files(filename, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    f = open(filename, 'r')
    lst = f.readlines()
    lst = list(map(lambda x: x.strip(), lst))
    len_lst = len(lst)
    print(f"Link count: {len_lst}")
    print("Starting position: ", end='')
    start_pos = int(input())
    print("End position: ", end='')
    end_pos = int(input())
    total_amount = end_pos - start_pos
    my_iter = 1
    for i in range(start_pos, end_pos):
        get_file(lst[i], folder_name)
        print(f"[{my_iter}/{total_amount}]")
        my_iter += 1
    f.close()


def sort_files(dir_path, reverse_order=True):
    paths = sorted(Path(dir_path).iterdir(), key=os.path.getmtime, reverse=reverse_order)
    counter = 1
    for i in paths:
        new_name = i.with_stem(str(counter))
        i.rename(new_name)
        counter += 1


tag = 'high_resolution'     # write tags here
link_file = 'links.txt'     # pic links file name
load_folder = 'dataset01'   # pic folder name

load_links(tag, link_file)                      # loading pic links to link_file, links gets expired after some time :(
load_files(link_file, load_folder)              # loading pictures to load_folder(up to 3500 pics approximately)
sort_files(load_folder, reverse_order=True)     # sorting pics in newer-to-older order or older-to-newer

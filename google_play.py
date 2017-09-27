import json
import os
import subprocess
import sys

from collections import defaultdict
from csv import DictReader

DATA_DIR = 'data'


def download_csvs(account_id):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    uri = 'gs://pubsite__rev_{}/stats/installs/*_overview.csv'.format(account_id)
    cmd = ['gsutil', 'cp', '-r', uri, 'data']
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print(err.decode('utf-8'))
        exit(2)


def to_json():
    stats = defaultdict(list)
    for dirpath, dnames, file_names in os.walk(DATA_DIR):
        for file_name in file_names:
            path = os.path.join(dirpath, file_name)
            if path.endswith('.csv'):
                with open(path, encoding='utf-16') as fp:
                    for line in DictReader(fp):
                        stats[line['Package Name']].append(line)

    # Sort
    for pkg, lines in stats.items():
        stats[pkg] = sorted(lines, key=lambda x: x['Date'])

    # Write
    for pkg, lines in stats.items():
        with open(os.path.join(DATA_DIR, '{}.json'.format(pkg)), 'w', encoding='utf-8') as fp:
            json.dump(lines, fp, indent=4)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python google_play.py ACCOUNT_ID")
        exit(1)

    download_csvs(sys.argv[1])
    to_json()

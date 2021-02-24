import os, re

pattern = '\s\(.+\)|\s\[.+\]'
[os.rename(f, re.sub(pattern,"",f)) for f in os.listdir('.') if not f.startswith('.')]
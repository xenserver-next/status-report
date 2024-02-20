#!/bin/sh
mv .vscode/ltex.dictionary.en-US.txt .git/
LC_ALL=C sort -fu .git/ltex.dictionary.en-US.txt >.vscode/ltex.dictionary.en-US.txt
diff -u .git/ltex.dictionary.en-US.txt .vscode/ltex.dictionary.en-US.txt &&
     rm .git/ltex.dictionary.en-US.txt

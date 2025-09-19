.RECIPEPREFIX=>
.PHONY: check darker-xen-bugtool pylint

check: darker-xen-bugtool pylint

# get the line-length from pyproject.toml
LINE_LENGTH = $(shell sed -n 's/line-length = \([0-9]*\).*/\1/p' pyproject.toml)
DARKER_OPTS = --isort -tpy36 -l$(LINE_LENGTH)
darker-xen-bugtool:
>@ pip install 'darker[isort]'
>@ tmp=`mktemp`                                       ;\
>  darker --stdout $(DARKER_OPTS) xen-bugtool >$$tmp ||\
>    exit 5                                           ;\
>  diff -u xen-bugtool $$tmp                          ;\
>  if [ $$? != 0 ]; then cat $$tmp >xen-bugtool       ;fi
>@ rm -f $$tmp

pylint:
> pylint xen-bugtool tests/*/*.py

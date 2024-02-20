.RECIPEPREFIX=>
.PHONY: check darker-xen-bugtool pylint

check: darker-xen-bugtool pylint

DARKER_OPTS = --isort -tpy36 --skip-string-normalization -l88
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

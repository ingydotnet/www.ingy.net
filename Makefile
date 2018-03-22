R := https://github.com/makeplus/makes
M := .cache/makes
$(shell [ -d '$M' ] || git clone -q $R '$M')

include $M/init.mk

LOCAL-ROOT := $(ROOT)/.cache/local
PYTHON-VENV := $(LOCAL-ROOT)/venv

include $M/python.mk
include $M/perl.mk
include $M/clean.mk

SHELL-DEPS += $(PYTHON-VENV)

include $M/shell.mk

export UV_LINK_MODE := copy
export UV_CACHE_DIR := $(LOCAL-CACHE)/uv
export NO_MKDOCS_2_WARNING := 1
export PYTHONPATH := $(CURDIR)/python

PUBLISH-REMOTE ?= origin
PUBLISH-BRANCH ?= main

MAKES-CLEAN := site
MAKES-REALCLEAN := $(PYTHON-VENV)
MAKES-DISTCLEAN := .cache/

default:: site

site: $(PYTHON-VENV) $(PERL) FORCE
	$(RM) -r $@
	mkdocs build --strict -d $@
	find $@ -type f \( -name '*.html' -o -name '*.css' \
	  -o -name '*.js' -o -name '*.json' -o -name '*.xml' \) \
	  -exec $(PERL) -0777 -pi -e \
	  's/[ \t]+$$//mg; s/\s+\z/\n/; s/\xE2\x80\x94/--/g' {} +

serve: $(PYTHON-VENV)
	mkdocs serve --livereload -a 127.0.0.1:$${PORT:-8000} \
	  --watch hooks.py --watch overrides --watch projects.yaml \
	  --watch photos.yaml

test: site
	$(PYTHON-VENV)/bin/python test/site.py

check: test
	git diff --check

root: site
	$(RM) -r assets
	cp -Rp site/assets .
	cp -p site/index.html site/CNAME site/sitemap.xml \
	  site/sitemap.xml.gz .

publish: root test
	test -z "$$(git status --porcelain)" || { \
	  git status --short; \
	  echo 'Commit all site changes before publishing'; \
	  exit 1; \
	}
	git push $(PUBLISH-REMOTE) HEAD:$(PUBLISH-BRANCH)

FORCE:

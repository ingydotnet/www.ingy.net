ALL := $(shell find . -name index.yaml | grep -v = | perl -pe 's/(.*\/).*/\1/')

TOP := $(shell pwd)

all:
	for d in $(ALL); do T=$(TOP) make -C $$d -f $(TOP)/=make/index.mk clean all; done;

clean:
	for d in $(ALL); do make -C $$d -f $(TOP)/=make/index.mk clean; done;

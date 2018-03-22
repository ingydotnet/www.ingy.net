all: index.html

index.html:
	tt-render --path=./:$T/=template/ --data=index.yaml $@.tt2 > $@
# 	tt-render --path=./:$T/=template/ --data=index.yaml $@.tt2 | iconv -f latin1 -t utf8 > $@

clean:
	rm -f index.html

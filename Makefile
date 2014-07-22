
lint:
	-pylint --include-ids=y --output-format=html `find src -name "*.py"`  > out.html

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.py.new" -exec rm {} \;
	python setup.py clean
	rm -rfv src/mreorg.egg-info/
	rm -rfv build/ dist/

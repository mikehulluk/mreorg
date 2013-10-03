
lint:
	-pylint --include-ids=y --output-format=html `find src -name "*.py"`  > out.html

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.py.new" -exec rm {} \;
	python setup.py clean
	rm -rf build/ dist/

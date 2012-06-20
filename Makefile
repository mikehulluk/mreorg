
lint:

	-pylint --include-ids=y --output-format=html `find src -name "*.py"`  > out.html

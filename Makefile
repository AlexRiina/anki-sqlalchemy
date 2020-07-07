.PHONY: clean test

plugin.zip:
	python setup.py sdist --format zip
	unzip -j $$(ls -t dist/*.zip | head -1) '*/src/*' -d dist/plugin
	zip plugin.zip -j -r dist/plugin
	# Test to confirm some files look right
	unzip -l plugin.zip '__init__.py'
	unzip -l plugin.zip 'main.py'

clean:
	rm -r build dist **/*.egg-info plugin.zip || true
	pyclean .

test:
	flake8 anki_sqlalchemy
	mypy anki_sqlalchemy
	black --check anki_sqlalchemy

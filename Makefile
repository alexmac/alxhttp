all:
	uv run pyright --createstub alxhttp
	rsync -a typings/alxhttp/ alxhttp/
	uv build
	twine upload dist/*
clean:
	find alxhttp |  grep pyi | xargs rm
	rm -rf dist alxhttp.egg-info typings

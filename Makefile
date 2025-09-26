all:
	uv run basedpyright --createstub alxhttp
	rsync -a typings/alxhttp/ alxhttp/
	uv build
	twine upload dist/*
clean:
	find alxhttp |  grep pyi | xargs rm
	rm -rf dist alxhttp.egg-info typings
check:
	uv run basedpyright --level error --threads 2 alxhttp tests example
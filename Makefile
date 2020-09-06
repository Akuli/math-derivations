buildloop:
	while true; do python3 build.py; inotifywait -e CLOSE_WRITE *.py content/*.txt content/*/*.txt Makefile; done

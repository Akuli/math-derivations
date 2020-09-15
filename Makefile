buildloop:
	while true; do python3 build.py; inotifywait -e CLOSE_WRITE *.py js/*.js js/*/*.js css/*.css content/*.txt content/*/*.txt Makefile; done

linkcheck:
	linkchecker html/*.html html/*/*.html

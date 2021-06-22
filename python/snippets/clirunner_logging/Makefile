NAME := world

hello: hello.py
	python hello.py $(NAME)

test: hello.py test_hello.py
	python -m pytest -svx .


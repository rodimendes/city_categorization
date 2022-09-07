# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

check_code:
	@flake8 scripts/* city-categorization/*.py

black:
	@black scripts/* city-categorization/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr city-categorization-*.dist-info
	@rm -fr city-categorization.egg-info

install:
	@pip install . -U

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)


#################### PACKAGE ACTIONS ###################

reinstall_package:
	@pip uninstall -y city-categorization || :
	@pip install -e .

run_image_load:
	python -c 'from city_categorization.main import image_load; image_load()'

run_make_array:
	python -c 'from city_categorization.main import make_array; make_array()'

run_model_load:
	python -c 'from city_categorization.main import model_load; model_load()'

run_preprocess:
	python -c 'from city_categorization.main import preprocess; preprocess()'

run_predict:
	python -c 'from city_categorization.main import predict; predict()'

run_y_cat_make:
	python -c 'from city_categorization.main import y_cat_make; y_cat_make()'

run_prediction_df:
	python -c 'from city_categorization.main import prediction_df; prediction_df()'

run_rgb_image:
	python -c 'from city_categorization.main import rgb_image; rgb_image()'

run_final_outputs:
	python -c 'from city_categorization.main import final_outputs; final_outputs()'

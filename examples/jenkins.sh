echo "PATH=.env/bin:$PATH" > my.props
grep version setup.py | sed "s/^.*version='\(.*\)',$/TXWINRM_SETUP_VERSION=\1/" >> my.props

# Inject environment variables

if [ -d ".env" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    virtualenv .env
fi
easy_install twisted
easy_install flake8
easy_install coverage
if [ -d "cyclic_complexity" ]; then
    echo "**> cyclic_complexity exists"
else
    echo "**> creating cyclic_complexity"
    git clone https://github.com/dgladkov/cyclic_complexity
fi
python setup.py sdist
python -m unittest discover
flake8 txwinrm
coverage run --include="txwinrm/*" --omit="txwinrm/test/*" -m unittest discover
coverage report --fail-under=60
txwinrm/test/complex

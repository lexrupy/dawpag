# Remove backup and compiled files
find . -name "*.py[oc]" -exec rm {} \;
find . -name ".*~" -exec rm {} \;
find . -name "*~" -exec rm {} \;

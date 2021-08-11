mkdir -pv input output

pip3 install nltk
pip3 install requests
pip3 install pandas
pip3 install openpyxl
pip3 install tqdm
pip3 install xlrd
pip3 install pygtrie
pip3 install plantweb
pip3 install pyspellchecker

# The followings are for development and testing purpose only
#pip install -U pip setuptools wheel
pip3 install -U spacy
python3 -m spacy download en_core_web_sm
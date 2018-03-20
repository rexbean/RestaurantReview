
## Installation
pip3 install spacy
pip3 install yattag

# download spacy corpus
python3 -m spacy download en_core_web_lg

# if "ValueError: unknown locale: UTF-8" error occurs
# refering https://spacy.io/usage/#unknown-locale , add below two lines into ~/.bashrc
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8


## Run Program
cd path_to_xxxxx
python3 demo.py

# wait for the "model loaded."   It will take about 1min to load the corpus model

# specify input data file, there are 10 example data in the review_data/ directory.
# For example, typein "review_data/3.json" and press enter to wait for the result

# It starts to parse the text, typically 500KB data will take 1min to process
# then it generate a web page, including the calculated result, use a web browser to open it to view

## Environment Install

```
pip3 install spacy
pip3 install yattag

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python3 -m spacy download en_core_web_lg

#python install nltk, twpython
```

## Note

For evaluation:   let              Count(Positive)                    rating  -  1
                         ----------------------------------   =  --------------------
                          Count(Positive) + Count(Negative))             5 - 1
                          
In this way, Count(Poistive) = 0, rating will be 1, 
             Count(Positive) = Count(Positive) + Count(Negative), rating will be 5

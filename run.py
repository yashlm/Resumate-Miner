import nltk
nltk.download('stopwords')
from pyresparser.resume_parser import ResumeParser
data = ResumeParser("temp.pdf").get_extracted_data();
print(data)
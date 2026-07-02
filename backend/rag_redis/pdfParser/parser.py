from io import BytesIO
import pdfplumber
import re
import pprint
import requests

class PDFParser:
    def __init__(self, url):
        filecontents = requests.get(url)
        self.file = BytesIO(filecontents.content)
        self.pages = []
        with pdfplumber.open(self.file) as pdf:
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=0.5, y_tolerance=0.5)
                if text:
                    self.pages.append({"page": idx + 1, "text": text})

    def __cleanPage(self, page_text):
        ctrlChars = ['\x00', '\x0c' , '\r']
        ligatures = {'ﬁ' : 'fi',
                     'ﬂ':'fl',
                     'ﬀ': 'ff', 
                     'ﬃ':'ffi',
                     'ﬄ': 'ffl'}
        
        for char in ctrlChars:
           page_text = page_text.replace(char, '')
        
        for old, new in ligatures.items():
            page_text = page_text.replace(old, new)
        
        lines = [l for l in page_text.strip().split('\n') if l.strip()]
        lines = [l for l in lines if l.strip() not in self.repeatingLines]

        page_text = '\n'.join(lines)
        # Step 4 - Fix hyphenated line breaks
        page_text = re.sub(
            r'([A-Za-z])-\n([a-z]{3,})',
            r'\1\2',
            page_text)
            
        return page_text
    
    def __repair(self, page_text):
        repairedList = []
        endings = ('.', '?', '!', ':' , ')')
        # pprint.pp(self.pages)
        lines = page_text.strip().split('\n')        
        i = 0
        while i < len(lines) - 1:
            if not lines[i].endswith(endings) and lines[i+1][0].islower():
                repairedList.append(lines[i] + " " + lines[i+1])
                i += 2  # skip next line since it was merged
            else:
                repairedList.append(lines[i])
                i += 1

        # Don't forget the last line
        repairedList.append(lines[-1])
        return '\n'.join(repairedList)
      
            
    def cleanup(self):
        self.lineCounts = {}
        for page in self.pages:
            lines = [l for l in page['text'].strip().split('\n') if l.strip()]
            candidates = lines[:2] + lines[-2:]
            for line in candidates:
                normalized = line.strip()
                self.lineCounts[normalized] = self.lineCounts.get(normalized, 0) + 1
                
        total = len(self.pages)
        self.repeatingLines = set()
        for line, count in self.lineCounts.items():
                if count/ total > 0.4:
                    self.repeatingLines.add(line)
                    
        for page in self.pages:
            cleaned = self.__cleanPage(page['text'])
            page['text'] = self.__repair(cleaned)
            
        return self.pages
            


# if __name__ == "__main__":
#     pdf = PDFParser("/home/ng/Desktop/New Folder/2005.pdf")

#     print("BEFORE")
#     print(pdf.pages[10]["text"][:1000])

#     pdf.cleanup()

#     print("\nAFTER")
#     print(pdf.pages[10]["text"][:1000])

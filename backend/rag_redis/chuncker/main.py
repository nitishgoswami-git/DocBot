class Chuncker:
    
    def __init__(self, pages):
        self.pages = pages
        self.chunks = []
        
        
    def chunk_pages(self, max_token = 512):
        i = 0
        for page in self.pages:
            paragraphs = page['text'].split('\n\n')
            
            
            excess_text = ''
            for paragraph in paragraphs:
                paragraph += excess_text
                if len(paragraph.split()) > max_token:
                    words = paragraph.split()
                    
                    excess_text = ' '.join(words[max_token:])
                    paragraph = ' '.join(words[:max_token])
                else:
                    excess_text = ''
                    
                self.chunks.append({'chunk_id': i+1, 'content': paragraph , 'page': page['page']})
                i+=1
            if excess_text:
                self.chunks.append({'chunk_id': i+1, 'content': paragraph ,'page': page['page']})
            
                
        return self.chunks            
            
    
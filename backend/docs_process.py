class Documents:
    def __init__(self, docs: str):
        self.docs = docs
        self.chunk_size = 50
        self.cleaned_document = []
        self.chunk = []
        self.word_count = 0

    def cleaning_process(self) -> list:
        print("start document processing")
        for line in self.docs:
            if line != "":
                words = line.split()
                self.chunk.append(line)
                self.word_count += len(words)
                if self.word_count >= self.chunk_size:
                    self.cleaned_document.append(" ".join(self.chunk))
                    self.chunk = []
                    self.word_count = 0
        if self.word_count < self.chunk_size and self.word_count != 0:
            self.cleaned_document.append(" ".join(self.chunk))
        print("document processed")
        return self.cleaned_document

class Documents:
    def __init__(self, f, chunk_size):
        self.f = f
        self.chunk_size = chunk_size
        self.cleaned_document = []
        self.chunk = []
        self.word_count = 0

    def cleaning_process(self) -> str:
        for line in self.f:
            strip = line.strip()
            if strip != "":
                words = strip.split()
                self.word_count += len(words)
                self.chunk.append(strip)
                if self.word_count >= self.chunk_size:
                    self.cleaned_document.append(" ".join(self.chunk))
                    self.chunk = []
                    self.word_count = 0
                elif self.word_count < self.chunk_size and self.word_count != 0:
                    self.cleaned_document.append(" ".join(self.chunk))
        return self.cleaned_document

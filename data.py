"""Small, offline UTF-8 byte tokenizer and non-overlapping next-token windows."""
import torch
from torch.utils.data import Dataset

def encode(text):
    return list(text.encode("utf-8"))

def decode(tokens):
    return bytes(tokens).decode("utf-8", errors="replace")

class ByteWindows(Dataset):
    def __init__(self, text, context=32):
        if context < 1:
            raise ValueError("context must be positive")
        self.tokens = torch.tensor(encode(text), dtype=torch.long)
        self.context = context
        if len(self.tokens) <= context:
            raise ValueError("Corpus needs more bytes than one context window")

    def __len__(self):
        return (len(self.tokens)-1)//self.context

    def __getitem__(self, index):
        if not 0 <= index < len(self):
            raise IndexError(index)
        start = index*self.context
        return self.tokens[start:start+self.context], self.tokens[start+1:start+self.context+1]

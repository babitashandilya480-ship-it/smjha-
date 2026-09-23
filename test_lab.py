import tempfile
import unittest
from pathlib import Path
import torch
from .data import ByteWindows,encode,decode
from .model import GPTModel
from .lab import CONFIG,train,hardware_check

class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): torch.set_num_threads(2)

    def test_utf8_roundtrip(self):
        text="Force बल samjho"
        self.assertEqual(decode(encode(text)),text)

    def test_next_token_alignment(self):
        data=ByteWindows("abcdefghi",4)
        self.assertEqual(len(data),2)
        x,y=data[1]
        self.assertEqual(decode(x.tolist()),"efgh")
        self.assertEqual(decode(y.tolist()),"fghi")

    def test_short_corpus_rejected(self):
        with self.assertRaises(ValueError):ByteWindows("abc",32)

    def test_causal_attention(self):
        model=GPTModel(CONFIG).eval()
        a=torch.tensor([[1,2,3,4]])
        b=torch.tensor([[1,2,99,100]])
        with torch.no_grad():torch.testing.assert_close(model(a)[:,:2],model(b)[:,:2])

    def test_real_backward_on_cpu(self):
        self.assertTrue(hardware_check(torch.device("cpu"))["backward_pass"])

    def test_smoke_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            report,out=train(30,"cpu",Path(tmp)/"run")
            self.assertLess(report["final_train_loss"],report["initial_train_loss"])
            self.assertTrue(report["checkpoint_reload_verified"])
            self.assertTrue((out/"checkpoint.pt").is_file())
            self.assertFalse(report["student_ready"])
            with self.assertRaises(FileExistsError):train(1,"cpu",out)

    def test_duplicate_corpora_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"train.txt";q=Path(tmp)/"val.txt"
            p.write_text("Repeated sentence across splits. "*4)
            q.write_text(p.read_text())
            with self.assertRaises(ValueError):train(1,"cpu",Path(tmp)/"out",p,q)

    def test_invalid_steps(self):
        for steps in (0,-1,10001):
            with self.assertRaises(ValueError):train(steps)

if __name__=="__main__":unittest.main()

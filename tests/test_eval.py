from harborline.eval import run
from harborline.ingest import EVALS_PATH


def test_customer_eval_set_passes():
    assert run(EVALS_PATH) == 0

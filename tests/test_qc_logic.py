from studio.qc import QCCheck, QCReport


def test_qc_report_boolean():
    good = QCReport(True, [QCCheck("x", True, "ok")])
    bad = QCReport(False, [QCCheck("x", False, "bad")])
    assert good.passed is True
    assert bad.passed is False
